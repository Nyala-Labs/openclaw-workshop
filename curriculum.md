# OpenClaw — 120-Minute Workshop Itinerary

**Total duration:** 120 minutes (strict)  
**Live build scope:** Basic environment setup + run **one** skill (`local_file_io`).  
**Repository:** Production-style layout for self-study after the session.

---

> ## Security warning — `REQUIRE_EXEC_APPROVAL`
>
> **Set `REQUIRE_EXEC_APPROVAL=true` in `.env` for this workshop and for any environment where the agent can run code, touch the filesystem, or invoke tools.**  
> When this flag is enabled, destructive or high-risk actions (execution, broad writes, privilege changes) should not proceed without explicit human approval in the control channel (e.g. Telegram or dashboard).  
> **Never** disable this in shared, internet-exposed, or untrusted-input scenarios. Treat autonomous agents like privileged automation: default deny, explicit approve.

---

## Minute 0–15 — Intro (15m)

- What OpenClaw is: autonomous agent **runtime** + **skills** (tools) + **prompts** (policy and behavior), not a single monolithic script.
- Threat model in one slide: untrusted input → LLM → **your** skills → **your** data and systems.
- Learning outcomes: sandbox mental model, one safe skill, where production files live (`skills/`, `prompts/`, `tests/`, `openclaw.yaml`).
- Icebreaker: one example task students *wish* an agent could do — map it to “skill + approval + audit log.”

## Minute 15–45 — Docker Sandbox Setup (30m)

- Prerequisites check: Docker / Docker Compose, editor, Telegram optional for later.
- Copy `.env.example` → `.env`; paste **LLM** key only if running model calls in-session (facilitator may demo with keys in a private vault).
- `docker compose up -d` — explain each volume: `agent_workspace` (jail), `skills`, `prompts`, `logs`.
- Verify mounts: shell into container or list paths; confirm `OPENCLAW_WORKSPACE_ROOT` matches `/workspace` in compose.
- **Checkpoint:** Container healthy; students see mapped directories on host.

## Minute 45–65 — API / Telegram Connection (20m)

- Walk through `openclaw.yaml`: `llm`, `telegram`, `security`, `skills`.
- Telegram (if used): BotFather token → `TELEGRAM_BOT_TOKEN`; obtain `TELEGRAM_CHAT_ID` (bot must `/start` in the chat first).
- Relate env vars to runtime: no secrets in YAML; keys only via `.env` / secret store.
- **Checkpoint:** At least one successful “ping” or log line showing config loaded (facilitator script or stub runner as your org provides).

## Minute 65–95 — The “Aha!” File I/O Run (30m)

- Open `skills/local_file_io.py` — **read** path validation: realpath + commonprefix against workspace root.
- Run **one** skill invocation (facilitator-led): write a small file under `agent_workspace/`, then read it back.
- Show `logs/` or audit trail if wired — tie to compliance narrative.
- **Deliberate failure:** attempt path outside workspace (should refuse). Connect to pytest in next section’s preview.
- **Checkpoint:** Students have created one file inside the jail only.

## Minute 95–110 — Industry Tour (15m)

Facilitator-led **tour of production-shaped files** (students do not build these in-session):

| Area | Path | Why it matters |
|------|------|----------------|
| Skill implementation | `skills/local_file_io.py` | Tool code is where **enforcement** lives; prompts alone are not enough. |
| Policy / separation | `prompts/core_directive.md` | Industry separates **prompt engineering** from **application logic** for reviewability and versioning. |
| Safety net | `tests/test_local_file_io.py` | Unit tests **lock** sandbox boundaries across refactors and model changes. |
| Contract | `openclaw.yaml` | Single place to see integrations and security-related env wiring. |
| Operations | `docker-compose.yml`, `.env.example` | Reproducible deploys and least-surprise mounts. |

Close with: post-workshop homework — read comments in `skills/` and `prompts/`, run `pytest tests/`.

## Minute 110–120 — Q&A and Wrap (10m buffer within 120m)

- Recap: sandbox + approval + tests + audit.
- Optional: roadmap (more skills, CI, secret manager).
- Collect feedback; point to `README.md` for commands.

---

## Facilitator notes

- Keep **live coding** to setup + **one** skill run; everything else is explanation and tour.
- If time slips, shorten Intro by 5m and Industry Tour by 5m — never cut the sandbox + file I/O block.
- Ensure `.env` is never committed; use `.env.example` only in repo.
