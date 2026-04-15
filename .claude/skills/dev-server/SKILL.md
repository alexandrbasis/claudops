---
name: dev-server
description: >
  Start any project's dev server and monitor it for errors in real-time.
  Universal — works with Node.js (Next.js, Vite, Remix, Astro, SvelteKit,
  Nuxt, Angular, Gatsby, Expo), Python (Django, Flask, FastAPI, Uvicorn),
  Ruby (Rails, Sinatra), Go, Rust (Cargo), Java (Spring Boot, Gradle, Maven),
  PHP (Laravel, Symfony), Elixir (Phoenix), and Docker Compose. Auto-detects
  the stack and package manager from project files. Uses the Monitor tool to
  stream only errors, warnings, and crashes — not routine request logs.
  Use this skill whenever the user says "start dev server", "run dev",
  "start the app", "launch the server", "npm run dev", "cargo run",
  "python manage.py runserver", "rails server", "go run", or anything that
  implies starting a local development server. Also trigger when the user
  asks to "monitor the server", "watch the build", "check for errors while
  I work", or simply "dev".
user-invokable: true
argument-hint: "[port] [-- extra-args]"
allowed-tools: Bash, Monitor, Read, Glob
---

# Dev Server — Start & Monitor

Start the project's dev server and watch its output for errors. The user says "start dev" and you handle detection, startup, and monitoring — they only hear from you when something breaks.

## Workflow

### 1. Detect the stack

Scan the working directory for project markers. Check in this order — first match wins:

| Marker file | Stack | Dev command | Default port |
|---|---|---|---|
| `package.json` | Node.js (see framework table) | varies | 3000 |
| `manage.py` | Django | `python manage.py runserver` | 8000 |
| `Pipfile` or `pyproject.toml` with `[tool.poetry]` | Python (check for framework) | varies | 8000 |
| `requirements.txt` with `fastapi` | FastAPI | `uvicorn main:app --reload` | 8000 |
| `requirements.txt` with `flask` | Flask | `flask run --reload` | 5000 |
| `Gemfile` with `rails` | Rails | `bin/rails server` | 3000 |
| `Gemfile` with `sinatra` | Sinatra | `ruby app.rb` | 4567 |
| `go.mod` | Go | `go run .` | 8080 |
| `Cargo.toml` | Rust | `cargo run` | 8080 |
| `pom.xml` | Maven/Spring | `./mvnw spring-boot:run` | 8080 |
| `build.gradle` / `build.gradle.kts` | Gradle/Spring | `./gradlew bootRun` | 8080 |
| `mix.exs` with `phoenix` | Phoenix | `mix phx.server` | 4000 |
| `composer.json` with `laravel` | Laravel | `php artisan serve` | 8000 |
| `docker-compose.yml` | Docker | `docker compose up` | varies |
| `Makefile` with `dev` target | Make | `make dev` | varies |

**Node.js framework detection** — when `package.json` exists, check dependencies:

| Dependency | Framework | Default command |
|---|---|---|
| `next` | Next.js | `next dev` |
| `vite` or `@vitejs/*` | Vite | `vite` |
| `@remix-run/dev` | Remix | `remix dev` |
| `astro` | Astro | `astro dev` |
| `@sveltejs/kit` | SvelteKit | `vite dev` |
| `nuxt` | Nuxt | `nuxt dev` |
| `@angular/cli` | Angular | `ng serve` |
| `gatsby` | Gatsby | `gatsby develop` |
| `expo` | Expo | `expo start` |
| _(none match)_ | npm scripts | `<pm> run dev` | 3000 |

**Node.js package manager** — check in order:
1. `bun.lock` or `bun.lockb` → `bunx` / `bun run`
2. `pnpm-lock.yaml` → `pnpm exec` / `pnpm run`
3. `yarn.lock` → `yarn` / `yarn run`
4. Default → `npx` / `npm run`

**Python environment** — check in order:
1. `.venv/` or `venv/` exists → `source .venv/bin/activate &&`
2. `poetry.lock` → `poetry run`
3. `Pipfile.lock` → `pipenv run`
4. Default → direct command

If nothing matches, tell the user you couldn't detect the stack and ask what command to run.

### 2. Pre-flight checks

Before starting:

1. **Port conflict** — check if the default (or user-specified) port is taken:
   ```bash
   lsof -i :<port> -t 2>/dev/null
   ```
   If occupied, tell the user and ask: kill the process or use a different port?

2. **Dependencies installed?**
   - Node: check `node_modules/` exists
   - Python: check virtualenv exists or key packages importable
   - Ruby: check `bundle check` passes
   - Go/Rust/Java: no check needed (build tools handle it)

   If missing, ask the user if you should install first.

### 3. Start with Monitor

Use the **Monitor** tool with `persistent: true` so the server runs for the session.

The filter is the critical piece — raw dev server output floods the conversation. Pipe through grep to catch only errors, warnings, and crashes:

```bash
<dev-command> 2>&1 | grep --line-buffered -iE \
  '(error[:\[]| ERR[!_]|EADDRINUSE|EACCES|ENOENT|ECONNREFUSED|FATAL|panic|Segmentation|Module not found|Cannot find module|ModuleNotFoundError|ImportError|SyntaxError|TypeError|ReferenceError|NameError|AttributeError|KeyError|ValueError|RuntimeError|IndentationError|failed to|build failed|compile error|compilation error|WARN[:\[]|warning[:\[]|deprecated|port.*already|address already in use|unhandled|rejected|crash|killed|Traceback|Exception|FAILED|ActionView|ActiveRecord|LoadError|undefined method|NoMethodError|cannot find|not found|Permission denied|exit code [1-9]|exit status [1-9]|thread.*panic|cannot compile)'
```

Set the Monitor `description` to something specific: `"Next.js dev :3000"` or `"Django dev :8000"`.

**Port flag by stack** (when user specifies a port):
- Next.js: `-p PORT`
- Vite/Astro/SvelteKit/Nuxt/Remix/Angular: `--port PORT`
- Django: `0.0.0.0:PORT`
- Flask: `--port PORT`
- FastAPI/Uvicorn: `--port PORT`
- Rails: `-p PORT`
- Phoenix: via `PORT=PORT` env var
- Laravel: `--port PORT`
- Go/Rust: usually via env var or arg (check the code)

**Announce** once started:
> Started **Next.js** dev server (`bun run dev`) on :3000 — monitoring for errors.

### 4. React to errors

When a Monitor notification fires:

1. **Classify** — build error, runtime exception, missing dependency, port conflict, type error, syntax error?
2. **Context** — quote the error, name the file and line if visible.
3. **Fix or ask** — for obvious issues (missing dep, typo, known pattern), suggest or apply the fix. For ambiguous ones, ask.
4. **Warnings are low-priority** — mention briefly, don't alarm.

### 5. Stopping

When the user says "stop", "kill it", "shut down", or similar:
- `TaskStop` the Monitor
- Confirm stopped

## Edge cases

- **Monorepo**: If `package.json` has `workspaces` or there's a `turbo.json`/`nx.json`, ask which package. Or check for a root `dev` script.
- **Multiple servers**: Frontend + backend? Start multiple Monitors with distinct descriptions.
- **Docker Compose**: If `docker-compose.yml` exists alongside a framework, mention both options.
- **Custom commands**: If the user says "run `XYZ` and watch it", skip detection — just run their command through the Monitor filter.
- **Turbopack**: If Next.js dev script includes `--turbo`, preserve it.
