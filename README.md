*Run Ctrl + Shift + V in the IDE to preview this file as rendered Markdown.*

# OpenClaw Workshop

A **2-hour** hands-on session for **OpenClaw**, an autonomous AI agent framework. You will set up the Docker-based sandbox and run **one** skill (`local_file_io`) during the workshop. The rest of the repo is **production-shaped** so you can study it afterward.

## Prerequisites

- Docker and Docker Compose v2
- Python 3.10+ (for post-workshop tests)

## Intro

- **What OpenClaw is:** autonomous **runtime** + **skills** (tools) + **prompts** (policy and behavior), not a single monolithic script.
- **Threat model:** untrusted input → LLM → **your** skills → **your** data and systems.
- **Learning outcomes:** sandbox mental model, one safe skill, where production files live (`skills/`, `prompts/`, `tests/`, `openclaw.yaml`).
- **Icebreaker:** one example task students *wish* an agent could do — map it to “skill + approval + audit log.”

### Choose where the gateway runs

| Mode | Gateway | Agent workspace (files) | Typical use |
|------|---------|---------------------------|-------------|
| **Docker (recommended for this repo)** | Inside container `openclaw-workshop-agent` | Host **`./agent_workspace`** ↔ container **`/workspace`** | Workshop default; matches `docker-compose.yml` mounts |
| **Local (no Docker)** | **`openclaw gateway`** on your machine | Often **`~/.openclaw/workspace`** until you change config | Quick dev without containers |

**To use Docker and not the local gateway:** install only the **CLI** on your host (Step 2), configure **`.env`** (Step 3), then run **`docker compose up`** (Step 4) and point the **TUI** at **`ws://127.0.0.1:18789`** (Step 5). **Stop any local gateway first** so nothing else binds port **18789** and the TUI does not stay attached to a process on your laptop.

---

## Step 1: Clone the repository

```bash
git clone https://github.com/Nyala-Labs/openclaw-workshop.git
cd openclaw-workshop
```

Use your own fork URL if you did not clone from the org above.

---

## Step 2: Install the CLI client

**We are only installing the client interface (TUI and `openclaw` commands), not starting the agent engine.** The gateway runs **inside Docker** after Step 4.

**Official install script (curl):**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Or npm:**

```bash
npm install -g openclaw@latest
```

**Or pnpm:**

```bash
pnpm add -g openclaw@latest
pnpm approve-builds -g
```

---

## Step 3: Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your **LLM API credentials** (OpenAI, Mistral, or any provider your OpenClaw stack supports). Variables are injected into the container via Compose so the gateway can read them.

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key from your provider. |
| `LLM_BASE_URL` | Provider base URL (e.g. Mistral: `https://api.mistral.ai/v1`). |
| `LLM_MODEL` | Model id (e.g. `gpt-4o-mini`, `mistral-small-latest`). |
| `REQUIRE_EXEC_APPROVAL` | Keep **`true`** unless your facilitator explicitly enables otherwise in a trusted lab. |

`openclaw.yaml` in this repo documents how the workshop wires env-backed settings; the gateway also uses **`docker/openclaw.workshop.json`** (baked into the image) for `gateway` bind/port and default agent workspace **`/workspace`**.

Never commit `.env`. It is listed in `.gitignore`.

> **Security — `REQUIRE_EXEC_APPROVAL`**  
> Set `REQUIRE_EXEC_APPROVAL=true` in workshops and anywhere the agent can run code, touch the filesystem, or invoke tools. When enabled, high-risk actions should not proceed without explicit human approval in the control channel (e.g. TUI, dashboard). **Never** disable this in shared, internet-exposed, or untrusted-input scenarios.

---

## Step 4: Start the sandbox (Docker gateway)

The **`Dockerfile`** builds an image that installs the **`openclaw`** CLI and starts **`openclaw gateway run`** automatically. The **gateway process runs only in the container** — you do **not** run `openclaw gateway start` on your host for this path.

### 4a. Stop any local gateway (important)

If you ever started OpenClaw on your **host** (installer wizard, `openclaw gateway run`, or a system service), that process may still own port **18789**. Then the TUI can stay connected to **localhost on your machine** instead of the Docker container.

Do this **before** `docker compose up`:

```bash
openclaw gateway stop
# If your OpenClaw version uses a service:
# openclaw gateway status
```

Confirm nothing is listening on **18789** (optional):

```bash
ss -tlnp 2>/dev/null | grep 18789 || true
# or: lsof -i :18789
```

You want the Docker container to be the only listener on **`127.0.0.1:18789`** after Step 4b.

### 4b. Build and run Compose

From the repo root (use **`--build`** the first time, or after changing `Dockerfile` / gateway config):

```bash
docker compose up -d --build
```

**What gets mounted** (host → container):

| Host path | Role |
|-----------|------|
| `./agent_workspace` | **Execution jail** — file skills default to this workspace. |
| `./skills` | Skill code (Python modules). |
| `./prompts` | System prompts / directives. |
| `./logs` | Audit and runtime logs. |

**Verify the container is up and mounts exist:**

```bash
docker compose ps
docker inspect openclaw-workshop-agent --format '{{json .Mounts}}' | jq
docker exec openclaw-workshop-agent sh -c 'ls -la /workspace /app/skills /app/prompts /var/log/openclaw /app/openclaw.yaml'
docker exec openclaw-workshop-agent printenv OPENCLAW_WORKSPACE_ROOT
# Expect: /workspace
```

**Confirm the gateway is listening** (logs should show the gateway starting, not exiting):

```bash
docker compose logs openclaw-agent --tail 50
```

---

## Step 5: Enter the TUI (connect only to the Docker gateway)

The **gateway** runs **inside** the `openclaw-workshop-agent` container (`openclaw gateway run` with **`--bind lan`** and **`docker/openclaw.workshop.json`** so the default workspace is **`/workspace`**). Your **host** only runs the **TUI client** from Step 2 — **no local `openclaw gateway`** should be running (Step 4a).

1. **Docker is up** — `docker compose ps` shows `openclaw-workshop-agent` running; **`docker compose logs openclaw-agent --tail 30`** shows the gateway started, not crashed.
2. **Port** — published as **`127.0.0.1:18789`** on the host (maps to the gateway in the container).

3. **Verify the remote gateway before the TUI**

   ```bash
   openclaw gateway health --url ws://127.0.0.1:18789
   ```

   If this fails, fix the container first (`docker compose logs -f openclaw-agent`), not your `~/.openclaw` profile.

4. **Open the TUI on the host** (talks to **Docker**, not a second gateway on your laptop):

   ```bash
   openclaw tui
   ```

   Prefer forcing the gateway URL if your CLI supports it (names vary by version), e.g. **`--url ws://127.0.0.1:18789`** — see **`openclaw tui --help`**.

5. **Confirm you are on the workshop workspace** — when connected to the container, file tools should use **`/workspace`** inside the box, which is **`./agent_workspace`** on your machine. If the status line still shows **`~/.openclaw/workspace`**, the TUI is almost certainly still using a **local** gateway: return to Step 4a, stop the local process, restart Compose, and try again.

**Troubleshooting**

- **Port in use:** Another process grabbed **18789** — stop local OpenClaw (Step 4a) or change the host port in **`docker-compose.yml`** (e.g. `"18790:18789"`) and point the TUI at **`ws://127.0.0.1:18790`**.
- **`openclaw: not found` in `docker exec`** — rebuild the image: **`docker compose build --no-cache`**.
- **TUI offline** — **`docker compose logs -f openclaw-agent`** and confirm **`curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18789/`** returns some HTTP status (not connection refused).

---

## Step 6: The “Aha!” File I/O run

1. **Skim** `skills/local_file_io.py` — path checks keep reads/writes under the workspace root.
2. In the **TUI** (after Step 5), **paste or type this prompt** so the agent uses file I/O in the workspace:

   **Prompt to type in the TUI:**

   > Please write a short poem about automation and save it to a file called `poem.txt` in your workspace.

3. Confirm **`./agent_workspace/poem.txt`** exists on the host (same as `/workspace/poem.txt` in the container). Read it back or open it in your editor.
4. **Optional stretch:** ask the agent to attempt a path outside the workspace — the skill should refuse.
5. **Checkpoint:** one file created **inside** the jail only.

---

## Where to look next

| File | Purpose |
|------|---------|
| `Dockerfile` | Installs `openclaw`, copies gateway config, runs `openclaw gateway run`. |
| `docker/openclaw.workshop.json` | Minimal gateway (`port` **18789**, `bind` **lan**) and agent workspace **`/workspace`**. |
| `docker-compose.yml` | Builds the image, env file, volumes, port **18789**. |
| `openclaw.yaml` | Workshop reference for LLM env keys, security, skill paths. |
| `skills/local_file_io.py` | Sandboxed read/write skill. |
| `prompts/core_directive.md` | Example system prompt (policy separate from code). |
| `tests/test_local_file_io.py` | Unit tests for the sandbox boundary. |

---

## Appendix A: Optional — interactive install wizard

If you used `curl … install.sh` and OpenClaw walked you through questions, you can use **Quick Start**, pick your **model provider** and **model**, skip **search** and extra **API key** prompts if you already set keys in `.env` (Step 3). This is **not** required for the numbered steps if you already have the CLI and `.env` configured.

---

## Appendix B: Local gateway only (no Docker)

Use this only if you **deliberately** skip **`docker compose`** and run **`openclaw gateway`** on your host. **Do not** run local and Docker gateways both on port **18789**.

OpenClaw defaults to **`~/.openclaw/workspace`**. To align with this repo’s jail:

```bash
cd /path/to/openclaw-workshop
openclaw config set agents.defaults.workspace "$(pwd)/agent_workspace"
```

Restart the local gateway, then **`openclaw tui`**. If `openclaw config set` is unavailable, set **`agents.defaults.workspace`** in **`~/.openclaw/openclaw.json`** to the absolute path of **`agent_workspace`**. Skills/prompts under **`./skills`** and **`./prompts`** may need extra OpenClaw wiring compared to the Docker image.

---

## Run tests (post-workshop)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pytest
pytest tests/ -v
```

## Security reminder

Keep **`REQUIRE_EXEC_APPROVAL=true`** in real deployments until you have a full trust and monitoring story.
