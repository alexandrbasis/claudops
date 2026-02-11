# Image generation (nanobanana extension)

This workspace has the `nanobanana` Gemini CLI extension installed (verify with `gemini --list-extensions`).

Source: [`gemini-cli-extensions/nanobanana`](https://github.com/gemini-cli-extensions/nanobanana)

## Key concept: chat model vs image model

- `gemini --model ...` controls the **chat model** (how Gemini reasons and writes text).
- `nanobanana` uses a separate **image model**:
  - default: `gemini-2.5-flash-image`
  - pro: `gemini-3-pro-image-preview` (set via `NANOBANANA_MODEL`)

So: pinning `--model gemini-3-pro-preview` is useful for better prompts/reviews, but it **does not** switch the image model. To switch the image model you must set `NANOBANANA_MODEL` and restart the CLI.

## Prerequisites (practical)

- **Extension installed**: `gemini --list-extensions` should include `nanobanana`.
- **API key**: set one of the env vars supported by the extension:
  - `NANOBANANA_GEMINI_API_KEY` (recommended when you normally auth to Gemini CLI via “Login with Google”)
  - `NANOBANANA_GOOGLE_API_KEY` (Vertex key users)
  - fallbacks: `GEMINI_API_KEY`, `GOOGLE_API_KEY`

## Recommended workflow (interactive; verified working here)

In our interactive session inside this repo, `generate_image (nanobanana)` was available and successfully generated PNG files under `./nanobanana-output/`.

1) Start an interactive Gemini session in the project root:

```bash
gemini --model gemini-3-pro-preview
```

2) Use the nanobanana commands (as documented by the extension):
- `/generate` (text-to-image)
- `/edit` (edit an existing image)
- `/restore` (restore/enhance)
- `/icon`, `/pattern`, `/story`, `/diagram`
- `/nanobanana` (natural language interface)

Examples:

```text
/generate "a watercolor painting of a fox in a snowy forest"
/generate "sunset over mountains" --count=3 --preview
/edit portrait.jpg "change background to a beach scene" --preview
/icon "coffee cup logo" --sizes="64,128,256" --type="app-icon" --preview
```

Output directory:
- The extension saves outputs to `./nanobanana-output/` by default (this repo also gitignores it).

## Switching to Nano Banana Pro (Gemini 3 image model)

In this workspace we **always** want the Pro image model:
- `NANOBANANA_MODEL=gemini-3-pro-image-preview`

To actually use it, set the env var and restart `gemini`:

```bash
export NANOBANANA_MODEL=gemini-3-pro-image-preview
gemini --model gemini-3-pro-preview
```

Tip: to make it persistent, add the export to your shell profile (e.g. `~/.zshrc`) and restart your terminal.

## One-shot (headless) notes (less reliable)

In a headless one-shot attempt from this repo, we saw failures like:
- folder considered **not trusted** (approval mode downgraded)
- tool registry errors (e.g. `generate_image` / `run_shell_command` not found)

If one-shot fails, use the interactive flow above (it is the workflow we verified).

