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

**To use Docker and not the local gateway:** install the **CLI** on your host (Step 2), configure **`.env`** (Step 3), **stop any local `openclaw gateway`** so port **18789** is free (Step 4a), then **`docker compose up`** (Step 4b) and run **`openclaw tui`** (Step 5). If a local gateway is still running, the TUI often attaches to it instead of the container.

---

## Step 1: Clone the repository

```bash
git clone https://github.com/Nyala-Labs/openclaw-workshop.git
cd openclaw-workshop
```

Use your own fork URL if you did not clone from the org above.

---

## Step 2: Install the CLI client

**We are only installing the client interface (TUI and `openclaw` commands), not the long-lived gateway on your laptop.** For this workshop’s **Docker** path, the **gateway runs in the container** (Step 4). Your host only needs the CLI so you can run **`openclaw tui`** (and optionally **`openclaw gateway health`**) against the gateway on **`localhost:18789`** once the Docker stack is up.

### Install methods

**Official install script (curl)** — often runs an **interactive onboarding** (questions about risks, Quick Start vs full setup, model provider, channels, skills, API keys, hooks, etc.):

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Or npm** (usually **no** questionnaire — only puts `openclaw` on your `PATH`):

```bash
npm install -g openclaw@latest
```

**Or pnpm:**

```bash
pnpm add -g openclaw@latest
pnpm approve-builds -g
```

### If you go through the wizard (typical with `curl` install)

The prompts change between OpenClaw versions; use this as **intent**, not exact wording:

| Topic | Suggested choice for **gateway in Docker** |
|-------|---------------------------------------------|
| **Continue / risks** | Accept so you can finish install. |
| **Onboarding** | **Quick Start** is fine if offered — you mainly need the CLI. |
| **Model provider / model** | Match what you will put in **`.env`** (Step 3). Duplicates are OK; the **container** reads **`env_file: .env`** in Compose. |
| **Channel** (Telegram, WhatsApp, …) | **Skip / disable for now** unless the facilitator requires a channel. The workshop focuses on **TUI + repo workspace**; extra channels can confuse “which gateway is running.” |
| **Search / web / extra tools** | Skip unless required. |
| **Skills / dependencies / node manager** | Skip for now, only need the Docker gateway + TUI for this repo. |
| **API keys in the wizard** | Optional; you can rely on **`.env`** + **`docker compose`** only. Prefer **one source of truth** — **`.env`** for the container — to avoid mismatches. |
| **Hooks / advanced** | Skip for now. |

**Important:** Some installers register or start a **local gateway** (user service / background `openclaw gateway`). For this repo you want **only the Docker gateway** on port **18789**. After the wizard finishes:

- Run **`openclaw gateway stop`** (or **`openclaw gateway status`**) and stop/disable any **local** gateway service if your OS installed one.
- If you are unsure, continue to **Step 4a** — you will stop local listeners and free port **18789** before starting Compose.

**If you install via npm/pnpm only** and never ran the script, you may have **no** questionnaire — that is fine. You still need **Step 3** (`.env`) and **Step 4** (Docker).

### Verify the CLI

```bash
openclaw --version
```

Do **not** rely on a local gateway until you have intentionally chosen **Appendix B**. For the default path, the next gateway you use should be the one **inside** **`openclaw-workshop-agent`**.

---

## Step 3: Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your **LLM API credentials**. Compose injects the file into the container (`env_file`) so the gateway can read them.

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key from your provider. |
| `LLM_BASE_URL` | Provider base URL (e.g. Mistral: `https://api.mistral.ai/v1`). |
| `LLM_MODEL` | Model id (e.g. `gpt-4o-mini`, `mistral-small-latest`). |
| `REQUIRE_EXEC_APPROVAL` | Keep **`true`** unless your facilitator explicitly enables otherwise in a trusted lab. |

`openclaw.yaml` documents workshop-oriented env wiring; **`docker/openclaw.workshop.json`** sets **`gateway.bind`** to **`lan`**, **`port`** to **18789**, and **`agents.defaults.workspace`** to **`/workspace`**.

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

## Step 5: Enter the TUI (Docker gateway)

The **gateway** runs **inside** the `openclaw-workshop-agent` container (`openclaw gateway run` with **`--bind lan`** so the published port **18789** works). Your **host** only runs the **TUI** from Step 2 — **no local `openclaw gateway`** (Step 4a).

1. **Docker is up** — `docker compose ps` shows `openclaw-workshop-agent` running; **`docker compose logs openclaw-agent --tail 30`** shows the gateway started, not crashed.

2. **Optional — check the gateway**

   ```bash
   openclaw gateway health --url ws://127.0.0.1:18789
   ```

   If this fails, inspect **`docker compose logs -f openclaw-agent`** and confirm Step 4a (nothing else on **18789**).

3. **Start the TUI** (normal invocation; it should discover **`localhost:18789`**):

   ```bash
   openclaw tui
   ```

   If your CLI defaults to a different gateway, use **`openclaw tui --help`** and point at **`ws://127.0.0.1:18789`** if needed.

4. **Confirm the workshop workspace** — when using the **Docker** gateway, the agent workspace is **`/workspace`** in the container (**`./agent_workspace`** on the host). If the UI still shows **`~/.openclaw/workspace`**, you are likely still hitting a **local** gateway — repeat **Step 4a**, then **`docker compose restart`** and open the TUI again.

**Troubleshooting**

- **Port in use:** Stop local OpenClaw (Step 4a) or remap the host port in **`docker-compose.yml`** (e.g. `"18790:18789"`) and pass **`--url ws://127.0.0.1:18790`** if your CLI requires it.
- **`openclaw: not found` in `docker exec`** — rebuild: **`docker compose build --no-cache`**.
- **No assistant reply** — try **`/deliver on`** in the TUI (see **`openclaw tui --help`** for **`--deliver`**).

---

## Step 6: File I/O run

1. **Skim** `skills/local_file_io.py` — path checks keep reads/writes under the workspace root.
2. In the **TUI** (after Step 5), check **`/status`** if something looks off. **“Gateway not connected”** usually means a **local** gateway is still running or port **18789** is wrong — go back to **Step 4a** and Step 5.
3. If the model does not reply, turn on delivery: **`/deliver on`** once, or **`openclaw tui --deliver`** if your CLI supports it.
4. **Paste or type this prompt** so the agent uses file I/O in the workspace:

   **Prompt to type in the TUI:**

   > Please write a short poem about automation and save it to a file called `poem.txt` in your workspace.

5. Confirm **`./agent_workspace/poem.txt`** exists on the host (same as `/workspace/poem.txt` in the container). Read it back or open it in your editor.
6. **Optional stretch:** ask the agent to attempt a path outside the workspace — the skill should refuse.
7. **Checkpoint:** one file created **inside** the jail only.

---

## Where to look next

| File | Purpose |
|------|---------|
| `Dockerfile` | Installs `openclaw`, copies gateway config, runs `openclaw gateway run`. |
| `docker/openclaw.workshop.json` | Gateway **`port` / `bind`**, default agent workspace **`/workspace`**. |
| `docker-compose.yml` | Builds the image, env file, volumes, port **18789**. |
| `openclaw.yaml` | Workshop reference for LLM env keys, security, skill paths. |
| `skills/local_file_io.py` | Sandboxed read/write skill. |
| `prompts/core_directive.md` | Example system prompt (policy separate from code). |
| `tests/test_local_file_io.py` | Unit tests for the sandbox boundary. |

---

## Appendix A: Optional — interactive install wizard

See **Step 2** for the full wizard guidance (Quick Start, channels, API keys, and stopping an accidental **local** gateway). **npm/pnpm** installs often skip the questionnaire entirely.

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
