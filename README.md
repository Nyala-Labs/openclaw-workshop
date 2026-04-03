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

---

## Step 1: Clone the repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

Example (replace with your fork or upstream):

```bash
git clone https://github.com/Nyala-Labs/openclaw-workshop.git
cd openclaw-workshop
```

---

## Step 2: Install the CLI client

Install the **OpenClaw command-line tools** on your machine (the **TUI** and `openclaw` commands). This step only installs the **client interface** on your laptop — it does **not** start the agent **engine** or gateway. The engine runs in **Docker** later (Step 4).

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

Edit `.env` and add your **LLM API credentials**. The runtime reads these via `openclaw.yaml` (OpenAI-compatible clients are common; Mistral and others often use the same pattern with a provider-specific **base URL** and **model id**).

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key from **OpenAI**, **Mistral**, or another provider you use. |
| `LLM_BASE_URL` | Provider base URL (e.g. Mistral: `https://api.mistral.ai/v1` — confirm in current docs). Leave empty only if your default matches the client’s built-in default. |
| `LLM_MODEL` | Model id (e.g. `gpt-4o-mini`, `mistral-small-latest`, etc.). |
| `REQUIRE_EXEC_APPROVAL` | Keep **`true`** unless your facilitator explicitly enables otherwise in a trusted lab. |

Never commit `.env`. It is listed in `.gitignore`.

> **Security — `REQUIRE_EXEC_APPROVAL`**  
> Set `REQUIRE_EXEC_APPROVAL=true` in workshops and anywhere the agent can run code, touch the filesystem, or invoke tools. When enabled, high-risk actions should not proceed without explicit human approval in the control channel (e.g. TUI, dashboard). **Never** disable this in shared, internet-exposed, or untrusted-input scenarios.

---

## Step 4: Start the sandbox

From the repo root:

```bash
docker compose up -d
```

**What gets mounted** (host → container):

| Host path | Role |
|-----------|------|
| `./agent_workspace` | **Execution jail** — file skills default to this workspace. |
| `./skills` | Skill code (Python modules). |
| `./prompts` | System prompts / directives. |
| `./logs` | Audit and runtime logs. |

**Verify mounts** (optional but recommended):

```bash
docker compose ps
docker inspect openclaw-workshop-agent --format '{{json .Mounts}}' | jq
docker exec -it openclaw-workshop-agent sh -c 'ls -la /workspace /app/skills /app/prompts /var/log/openclaw /app/openclaw.yaml'
docker exec openclaw-workshop-agent printenv OPENCLAW_WORKSPACE_ROOT
# Expect: /workspace
```

---

## Step 5: Enter the TUI (connect to the Docker agent)

The **gateway** runs in **Docker**, not as a long-lived process on your host only. The **CLI** you installed in Step 2 talks to that gateway.

1. **Docker is running** and Step 4 completed (`docker compose up -d`).
2. **Port published** — `docker-compose.yml` maps **`18789:18789`** so a gateway inside the container can be reached at `localhost:18789` on your machine. Align with your facilitator if your gateway uses a different port.
3. **Start the gateway** inside the container (or your facilitator’s startup flow) so something listens on **18789** — e.g. `openclaw gateway start` *in the environment where the gateway runs*, per OpenClaw docs.
4. **On your host**, open the terminal UI: **ensure Docker is running, then run:**

   ```bash
   openclaw tui
   ```

   The CLI usually auto-detects a gateway on `localhost:18789`. If not, point the client at `http://127.0.0.1:18789` (or the URL your facilitator gives you).

If the TUI is offline, confirm the gateway is running and the port is mapped before retrying.

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
| `openclaw.yaml` | LLM env keys, security, skill paths. |
| `skills/local_file_io.py` | Sandboxed read/write skill. |
| `prompts/core_directive.md` | Example system prompt (policy separate from code). |
| `tests/test_local_file_io.py` | Unit tests for the sandbox boundary. |

---

## Appendix A: Optional — interactive install wizard

If you used `curl … install.sh` and OpenClaw walked you through questions, you can use **Quick Start**, pick your **model provider** and **model**, skip **search** and extra **API key** prompts if you already set keys in `.env` (Step 3), and skip **channel** setup for this workshop. Install skill dependencies when asked if your facilitator requires them. This is **not** required for the numbered steps above if you already have the CLI and `.env` configured.

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
