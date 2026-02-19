Purpose
-------
This file guides automated coding agents (Copilot-style) to quickly become productive in this repository.

Repository state: no source files were detected when this guidance was generated. If you (human) have additional files, re-run the discovery steps below and update this document with concrete examples.

Quick start (what to do first)
- **Scan:** Run `git status`, `ls -la`, and search for common manifest files: `README.md`, `package.json`, `pyproject.toml`, `go.mod`, `setup.py`, `Cargo.toml`, `Makefile`, `Dockerfile`.
- **Identify entrypoints:** Look for top-level folders named `src/`, `cmd/`, `app/`, `server/`, `frontend/`, or `packages/`.
- **Look for CI:** Search for `.github/workflows/` and `Makefile` to learn build/test automation.

Discoverable patterns to extract
- **Language & runtime:** Determine by presence of `package.json` (Node), `pyproject.toml`/`requirements.txt` (Python), `go.mod` (Go), `Cargo.toml` (Rust). Use that to choose build/test commands.
- **Start scripts:** If `package.json` exists, prefer `npm run build` / `npm test` scripts over ad-hoc commands.
- **Service boundaries:** If you find `cmd/` or multiple top-level services (e.g., `api/`, `worker/`, `web/`), treat each as a separate component and list their Dockerfiles, env files, and main ports.
- **Configuration patterns:** Note use of `env` files, `config/` folders, `*.yaml` or `*.json` for shared config; record expected env vars found in examples like `.env.example`.

Project-specific workflows (what to record)
- **Build:** Exact commands to build each component (copy the `npm`, `make`, `go build`, or `python -m build` invocation).
- **Run locally:** Command and env setup to run services (example: `PORT=3000 yarn start` or `uvicorn app.main:app --reload --port 8000`).
- **Tests:** How to run tests and any required test fixtures or DBs (e.g., `npm test`, `pytest -q`, `go test ./...`).
- **Debugging:** Preferred approach (run with `--inspect`, `pdb`, or attach debugger to process); reference any VS Code launch configs in `.vscode/` if present.

Merging guidance (if this file already exists)
- Preserve existing human-authored sections verbatim whenever they contain specific commands or examples.
- If merging automated findings, add a new section titled `Discovered (auto)` with a timestamp and the exact commands you used to verify.

When you can't discover facts
- If the repository truly has no manifests or README, pause and request the following from the human: a sample `README.md`, an example service entrypoint, or access to the repository remote.

Next steps for humans
- Add an existing `README.md` or one-line manifest pointers so agents can provide concrete build/run/test commands.
- If you want richer automation, include `AGENT.md` or `.github/copilot-instructions.md` examples in language-specific subfolders.

If anything here is unclear, tell me which files exist in the repo and I'll re-run discovery and produce an updated, merged `copilot-instructions.md` with concrete examples.
