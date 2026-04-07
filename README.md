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

### Choose where the gateway runs

| Mode | Gateway | Agent workspace (files) | Typical use |
|------|---------|---------------------------|-------------|
| **Docker (recommended for this repo)** | Inside container `openclaw-workshop-agent` | Host **`./agent_workspace`** ↔ container **`/workspace`** | Workshop default; matches `docker-compose.yml` mounts |
| **Local (no Docker)** | **`openclaw gateway`** on your machine | Often **`~/.openclaw/workspace`** until you change config | Quick dev without containers |

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

First edit `.env`. Compose injects the file into the container (`env_file`) so the gateway can read them.

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key from your provider. |
| `LLM_BASE_URL` | Provider base URL (e.g. Mistral: `https://api.mistral.ai/v1`). |
| `LLM_MODEL` | Model id (e.g. `gpt-4o-mini`, `mistral-small-latest`). |
| `REQUIRE_EXEC_APPROVAL` | Keep **`true`**. |
| `OPENCLAW_GATEWAY_TOKEN` | Secret for connecting to OpenClaw gateway inside Docker. |

For the token, you set it yourself. Can also randomly generate it using:
```bash
openssl rand -hex 32
```

Never commit `.env`. It is listed in `.gitignore`.

In the `.openclaw_container` folder, copy the `openclaw.json.example` file, put your token in.

> **Security — `REQUIRE_EXEC_APPROVAL`**  
> Set `REQUIRE_EXEC_APPROVAL=true` in workshops and anywhere the agent can run code, touch the filesystem, or invoke tools. When enabled, high-risk actions should not proceed without explicit human approval in the control channel (e.g. TUI, dashboard). **Never** disable this in shared, internet-exposed, or untrusted-input scenarios.

Next check `~/.openclaw/openclaw.json`. In the gateway field, need to config as follows:
```json
"gateway": {
    "auth": {
      "mode": "token",
      "token": "insert your own token"
    },
    "mode": "remote",
    "remote": {
        "url": "ws://127.0.0.1:18789",
        "token": "same value as auth token"
    }
  },
```

Then check `./docker-compose.yml`. must have:
```yaml
environment:
   OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN}

volumes:
   # Overwrite the Dockerfile config with actual OpenClaw config file
   - ./.openclaw_container:/app/.openclaw:rw
```

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

Once the container is up, the OpenClaw gateway is open inside; no need to open it again in host terminal. Just use TUI client in host terminal.

**What gets mounted** (host → container):

| Host path | Role |
|-----------|------|
| `./agent_workspace` | **Execution jail** — file skills default to this workspace. |
| `./skills` | Skill code (Python modules). |
| `./prompts` | System prompts / directives. |
| `./logs` | Audit and runtime logs. |
| `./.openclaw_container` | The folder to contain the OpenClaw config file `openclaw.yaml` that will be passed into Docker. |

**Verify the container is up and mounts exist:**

```bash
docker compose ps
docker inspect openclaw-workshop-agent --format '{{json .Mounts}}' | jq
docker exec openclaw-workshop-agent sh -c 'ls -la /workspace /app/skills /app/prompts /var/log/openclaw /app/.openclaw'
docker exec openclaw-workshop-agent printenv OPENCLAW_WORKSPACE_ROOT
# Expect: /workspace
```

**Confirm the gateway is listening** (logs should show the gateway starting, not exiting):

```bash
docker compose logs openclaw-agent --tail 30
```

You should see a line like **`listening on ws://0.0.0.0:18789`**. If the container **restarts in a loop** (`docker compose ps` shows **Restarting**), read the logs: the **`openclaw`** CLI may require a **newer Node.js** than the image provides — the **`Dockerfile`** uses **`node:22-bookworm-slim`** for that reason. Rebuild with **`docker compose pull`** / **`docker compose build --no-cache`** after pulling the repo.

**Pair device for the first time** - mutual authentication, when creating container for the very first time, need to approve connection from device to gateway:
```bash
# Enter the container
docker exec -it openclaw-workshop-agent bash

# Find the Request ID (it should be there now that the TUI tried to connect)
openclaw devices list

# Approve it
openclaw devices approve <YOUR_ID_HERE>

# Exit the container
exit
```

---

## Step 5: Enter the TUI (Docker gateway)

Your **host** only runs the **TUI**.

1. **Optional — check the gateway**

   ```bash
   openclaw gateway health --url ws://127.0.0.1:18789tyo 
   ```

   If this fails, inspect **`docker compose logs -f openclaw-agent`** and confirm Step 4a (nothing else on **18789**).

2. **Start the TUI** (normal invocation; it should discover **`localhost:18789`**):

   ```bash
   openclaw tui
   ```

3. **Confirm the workshop workspace** — when using the **Docker** gateway, the agent workspace is **`/workspace`** in the container (**`./agent_workspace`** on the host). If the UI still shows **`~/.openclaw/workspace`**, you are likely still hitting a **local** gateway — repeat **Step 4a**, then **`docker compose restart`** and open the TUI again.

---

## Step 6: File I/O run

1. **Paste or type this prompt** so the agent uses file I/O in the workspace:

   **Prompt to type in the TUI:**

   > Please write a short poem about automation and save it to a file called `poem.txt` in your workspace.

2. Confirm **`./agent_workspace/poem.txt`** exists on the host (same as `/workspace/poem.txt` in the container). Read it back or open it in your editor.
3. **Optional stretch:** ask the agent to attempt a path outside the workspace — the skill should refuse.
4. **Checkpoint:** one file created **inside** the jail only.

---

## Where to look next

| File | Purpose |
|------|---------|
| `Dockerfile` | Installs `openclaw` on **Node 22** (required by current `openclaw` CLI), copies gateway config, runs `openclaw gateway run`. |
| `docker-compose.yml` | Builds the image, env file, volumes, port **18789**. Gateway **`port` / `bind`**, default agent workspace **`/workspace`**. |
| `openclaw.yaml` | OpenClaw reference for LLM env keys, security, skill paths. |
| `skills/local_file_io.py` | Sandboxed read/write skill. |
| `prompts/core_directive.md` | Example system prompt (policy separate from code). |
| `tests/test_local_file_io.py` | Unit tests for the sandbox boundary. |

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
