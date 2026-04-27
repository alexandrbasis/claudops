#!/usr/bin/env python3
"""Deterministic claudops upstream update helper."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


UPSTREAM_REPO = "https://github.com/alexandrbasis/claudops.git"
UPSTREAM_BRANCH = "main"
LOCK_PATH = ".claude/skills/update-setup/claudops-upstream.lock.json"
SKIP_EXACT = {".claude/settings.json", ".claude/settings.local.json", "CLAUDE.md"}
SKIP_PREFIXES = (".claude/hooks/logs/",)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return Path(output)
    except subprocess.CalledProcessError:
        return start


def is_scoped_file(relative_path: str) -> bool:
    if relative_path in SKIP_EXACT:
        return False
    if not relative_path.startswith(".claude/"):
        return False
    if relative_path.endswith(".gitkeep"):
        return False
    if ".local." in Path(relative_path).name:
        return False
    if any(relative_path.startswith(prefix) for prefix in SKIP_PREFIXES):
        return False
    return True


def upstream_files(upstream_root: Path) -> list[str]:
    files: list[str] = []
    claude_root = upstream_root / ".claude"
    if not claude_root.exists():
        return files
    for path in sorted(claude_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(upstream_root).as_posix()
        if is_scoped_file(relative):
            files.append(relative.removeprefix(".claude/"))
    return files


def load_manifest(manifest_path: Path) -> dict[str, object]:
    if not manifest_path.exists():
        return {"upstream": {}, "files": {}}
    return json.loads(read_text(manifest_path))


def re_split_placeholders(text: str) -> list[tuple[str, bool]]:
    result: list[tuple[str, bool]] = []
    cursor = 0
    for match in re.finditer(r"\{\{[^}]+\}\}", text):
        if match.start() > cursor:
            result.append((text[cursor : match.start()], False))
        result.append((match.group(0), True))
        cursor = match.end()
    if cursor < len(text):
        result.append((text[cursor:], False))
    return result


def placeholder_only(upstream_text: str, local_text: str) -> bool:
    if "{{" not in upstream_text or "}}" not in upstream_text:
        return False
    pattern = "^"
    for value, is_placeholder in re_split_placeholders(upstream_text):
        pattern += r"[\s\S]+?" if is_placeholder else re.escape(value)
    pattern += "$"
    return re.match(pattern, local_text) is not None


def unified_diff(upstream_text: str, local_text: str, path: str) -> str:
    return "".join(
        difflib.unified_diff(
            upstream_text.splitlines(keepends=True),
            local_text.splitlines(keepends=True),
            fromfile=f"upstream/.claude/{path}",
            tofile=f"local/.claude/{path}",
            n=3,
        )
    )


def classify_status(
    path: str,
    upstream_text: str,
    upstream_hash: str,
    local_root: Path,
    manifest_entry: dict[str, object] | None,
) -> tuple[str, str, str]:
    local_path = local_root / ".claude" / path
    disabled_path = local_root / ".claude" / f"{path}.disabled"

    if not local_path.exists():
        if disabled_path.exists():
            return "disabled", "", ""
        return "new", "", ""

    local_bytes = local_path.read_bytes()
    local_hash = sha256_bytes(local_bytes)
    if local_hash == upstream_hash:
        return "unchanged", "", local_hash

    local_text = local_bytes.decode("utf-8", errors="replace")
    if placeholder_only(upstream_text, local_text):
        return "placeholder_only", "", local_hash

    diff = unified_diff(upstream_text, local_text, path)
    if manifest_entry and manifest_entry.get("target_hash") != local_hash:
        return "conflicting", diff, local_hash
    return "modified", diff, local_hash


def build_report(
    upstream_root: Path,
    local_root: Path,
    upstream_commit: str,
    manifest_path: Path | None = None,
) -> dict[str, object]:
    manifest_path = manifest_path or local_root / LOCK_PATH
    manifest = load_manifest(manifest_path)
    manifest_files = manifest.get("files", {})
    items: list[dict[str, object]] = []
    seen: set[str] = set()

    for path in upstream_files(upstream_root):
        seen.add(path)
        upstream_path = upstream_root / ".claude" / path
        upstream_bytes = upstream_path.read_bytes()
        upstream_hash = sha256_bytes(upstream_bytes)
        upstream_text = upstream_bytes.decode("utf-8", errors="replace")
        status, diff, local_hash = classify_status(
            path,
            upstream_text,
            upstream_hash,
            local_root,
            manifest_files.get(path),
        )
        items.append(
            {
                "path": path,
                "source_root": str(upstream_root),
                "status": status,
                "source_hash": upstream_hash,
                "target_hash": upstream_hash,
                "local_hash": local_hash,
                "diff": diff,
                "requires_approval": status in {"new", "modified", "conflicting", "disabled"},
            }
        )

    for path, entry in sorted(manifest_files.items()):
        if path not in seen:
            items.append(
                {
                    "path": path,
                    "source_root": str(upstream_root),
                    "status": "removed",
                    "source_hash": entry.get("source_hash", ""),
                    "target_hash": entry.get("target_hash", ""),
                    "local_hash": "",
                    "diff": "",
                    "requires_approval": True,
                }
            )

    summary: dict[str, int] = {}
    for item in items:
        summary[item["status"]] = summary.get(item["status"], 0) + 1

    return {
        "upstream": {
            "repo": UPSTREAM_REPO,
            "branch": UPSTREAM_BRANCH,
            "commit": upstream_commit,
        },
        "manifest_path": str(manifest_path),
        "summary": summary,
        "items": items,
    }


def selection(path: Path) -> dict[str, set[str]]:
    data = json.loads(read_text(path))
    return {
        "update": set(str(item) for item in data.get("update", [])),
        "refresh_disabled": set(str(item) for item in data.get("refresh_disabled", [])),
        "delete": set(str(item) for item in data.get("delete", [])),
    }


def remove_empty_parents(path: Path, stop_at: Path) -> None:
    current = path.parent
    stop_at = stop_at.resolve()
    while current.resolve() != stop_at and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def apply_selection(
    report: dict[str, object],
    selection_path: Path,
    local_root: Path,
    manifest_path: Path | None = None,
) -> dict[str, object]:
    manifest_path = manifest_path or local_root / LOCK_PATH
    chosen = selection(selection_path)
    manifest = load_manifest(manifest_path)
    files = manifest.setdefault("files", {})
    result = {"updated": 0, "disabled_refreshed": 0, "deleted": 0, "skipped": []}

    for item in report["items"]:
        path = str(item["path"])
        status = str(item["status"])
        source_root = Path(str(item["source_root"]))
        upstream_path = source_root / ".claude" / path
        local_path = local_root / ".claude" / path

        if path in chosen["delete"] and status == "removed":
            if local_path.exists():
                local_path.unlink()
                remove_empty_parents(local_path, local_root / ".claude")
            files.pop(path, None)
            result["deleted"] += 1
            continue

        if path in chosen["refresh_disabled"] and status == "disabled":
            disabled_path = local_root / ".claude" / f"{path}.disabled"
            disabled_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(upstream_path, disabled_path)
            files[path] = {
                "source_hash": item["source_hash"],
                "target_hash": sha256_bytes(disabled_path.read_bytes()),
                "status": "disabled",
            }
            result["disabled_refreshed"] += 1
            continue

        if path in chosen["update"] and status in {"new", "modified"}:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(upstream_path, local_path)
            files[path] = {
                "source_hash": item["source_hash"],
                "target_hash": sha256_bytes(local_path.read_bytes()),
                "status": "adopted",
            }
            result["updated"] += 1
            continue

        result["skipped"].append(path)

    manifest["upstream"] = report["upstream"]
    write_json(manifest_path, manifest)
    return result


def verify(local_root: Path, manifest_path: Path | None = None) -> dict[str, object]:
    manifest_path = manifest_path or local_root / LOCK_PATH
    manifest = load_manifest(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []
    for path, entry in sorted(manifest.get("files", {}).items()):
        suffix = ".disabled" if entry.get("status") == "disabled" else ""
        target = local_root / ".claude" / f"{path}{suffix}"
        if not target.exists():
            errors.append(f"missing tracked file: {path}{suffix}")
            continue
        expected = entry.get("target_hash")
        actual = sha256_bytes(target.read_bytes())
        if expected and expected != actual:
            errors.append(f"hash mismatch: {path}{suffix}")
        if "{{" in target.read_text(encoding="utf-8", errors="replace"):
            warnings.append(f"placeholder remains: {path}{suffix}")
    return {"errors": errors, "warnings": warnings}


def clone_upstream(repo: str, branch: str, destination: Path) -> str:
    if destination.exists():
        shutil.rmtree(destination)
    subprocess.check_call(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--single-branch",
            "--branch",
            branch,
            repo,
            str(destination),
        ],
        stdout=subprocess.DEVNULL,
    )
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination, text=True).strip()


def command_scan(args: argparse.Namespace) -> int:
    local_root = repo_root(Path(args.local_root))
    manifest_path = local_root / args.manifest
    if args.upstream_root:
        upstream_root = Path(args.upstream_root).resolve()
        commit = args.commit or "local-upstream"
    else:
        upstream_root = Path(args.tmp_dir or tempfile.mkdtemp(prefix="claudops-upstream-"))
        commit = clone_upstream(args.repo, args.branch, upstream_root)
    report = build_report(upstream_root, local_root, commit, manifest_path)
    write_json(Path(args.output), report)
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def command_report(args: argparse.Namespace) -> int:
    report = json.loads(read_text(Path(args.report)))
    print("# Claudops Upstream Update Report\n")
    print(f"Upstream: `{report['upstream']['commit']}`\n")
    for status in [
        "new",
        "modified",
        "conflicting",
        "disabled",
        "removed",
        "placeholder_only",
        "unchanged",
    ]:
        entries = [item for item in report["items"] if item["status"] == status]
        print(f"## {status.upper()} ({len(entries)})")
        if not entries:
            print("(none)\n")
            continue
        for item in entries:
            print(f"- `{item['path']}`")
        print()
    return 0


def command_apply(args: argparse.Namespace) -> int:
    local_root = repo_root(Path(args.local_root))
    report = json.loads(read_text(Path(args.report)))
    result = apply_selection(report, Path(args.selection), local_root, local_root / args.manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    local_root = repo_root(Path(args.local_root))
    result = verify(local_root, local_root / args.manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["errors"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-root", default=".")
    parser.add_argument("--manifest", default=LOCK_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan")
    scan.add_argument("--repo", default=UPSTREAM_REPO)
    scan.add_argument("--branch", default=UPSTREAM_BRANCH)
    scan.add_argument("--upstream-root")
    scan.add_argument("--commit")
    scan.add_argument("--tmp-dir")
    scan.add_argument("--output", default=".claudops-update-report.json")
    scan.set_defaults(func=command_scan)

    report = subparsers.add_parser("report")
    report.add_argument("--report", default=".claudops-update-report.json")
    report.set_defaults(func=command_report)

    apply = subparsers.add_parser("apply")
    apply.add_argument("--report", default=".claudops-update-report.json")
    apply.add_argument("--selection", required=True)
    apply.set_defaults(func=command_apply)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.set_defaults(func=command_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
