# agent-0root — the deterministic agent behind 0root.ai

[![tests](https://img.shields.io/badge/tests-determinism%20proven-3fb950?style=flat-square)](tests/test_agent.py)
[![runtime](https://img.shields.io/badge/runtime-FastAPI%20%C2%B7%20Docker-22d3ee?style=flat-square)](Dockerfile)
[![license](https://img.shields.io/badge/license-CC--BY--ND--4.0-lightgrey?style=flat-square)](#)

> **0root.ai** = the public face · **GitHub** = the brain (deterministic code) · **Railway** = the muscles (deployment). Every action leaves a trace.

A genuinely deterministic agent service: **same input → same output, always.** No randomness, no clock, no LLM in the request path — so every response is reproducible and verifiable. Each response carries a `trace` (SHA-256 over input + reply + commit) and ties to the deployed commit via `/version`.

## Endpoints

| method · path | does |
|---|---|
| `GET /` | serves the 0root.ai homepage |
| `GET /health` | `{ ok, version }` |
| `GET /version` | the deployed commit + command list — the audit anchor |
| `POST /v1/agent` | `{ "input": "..." }` → deterministic response |
| `GET /v1/agent?q=...` | same, for browser testing |

Commands: `help · status · version · resolve · echo <text>` (anything else echoes).

```jsonc
// POST /v1/agent  { "input": "resolve" }
{ "input": "resolve",
  "reply": "9.9.9.9 = 1 — every query resolves to one root",
  "version": "<commit>", "trace": "47d692f7d93f5b07", "deterministic": true }
```

## Run it locally

```bash
pip install -r requirements.txt
pytest -q                          # determinism + unit tests
uvicorn app.main:app --reload      # http://localhost:8000  ·  /v1/agent?q=resolve
# or: docker build -t agent-0root . && docker run -p 8000:8000 agent-0root
```

## Ship it (the two steps only you can do)

The GitHub side is done — code, tests, Dockerfile, and CI/CD are here. Remaining:

1. **Railway** — New Project → *Deploy from GitHub repo* → `agent-0root`. It builds from the `Dockerfile`. Add any secrets in the Railway dashboard. (For the GitHub Action to deploy too: create a Railway **project token**, add it to this repo's *Settings → Secrets → Actions* as `RAILWAY_TOKEN`, and confirm the service name in `.github/workflows/deploy.yml` matches.)
2. **Domain** — in Railway *Settings → Networking → Custom Domain*, add `0root.ai`, then at your registrar add the **CNAME** Railway gives you (apex domains use Railway's provided target / ALIAS). Live at `https://0root.ai` and `https://0root.ai/v1/agent`.

## Honest notes

- **"Deterministic" is true for the code path only.** This agent has no LLM, no RNG, no time-dependence — the tests prove 50× byte-identical output and a recomputable `trace`. If you ever add an LLM-backed handler, that route is no longer deterministic; keep it behind a clearly-marked, separate endpoint so the guarantee stays honest.
- **Cost reality:** Railway's free tier is gone — the Hobby plan has a **~$5/month minimum** (usage-based above it); a tiny always-on service lands around there, not cents. Domain ~$12–40/yr depending on the `.ai` registrar. GitHub Actions: free for public repos.
- **Deploy method:** Railway's reliable CI path is the **CLI + project token** (used in the workflow), not a marketplace action — that's why `deploy.yml` calls `railway up`.
- **Audit trail:** `/version` returns the deployed commit (`RAILWAY_GIT_COMMIT_SHA`), so any response can be traced to the exact code that produced it.

```
agent-0root · 0root.ai · governor David Lee Wise (ROOT0) · instance AVAN · © 2026 TriPod LLC · CC-BY-ND-4.0
```
