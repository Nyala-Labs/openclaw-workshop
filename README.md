*run Ctrl + Shift + V to render markdown file in ide*
# OpenClaw Workshop

A **2-hour** hands-on session for **OpenClaw**, an autonomous AI agent framework. You will set up the Docker-based sandbox and run **one** skill (`local_file_io`) during the workshop. The rest of the repo is **production-shaped** so you can study it afterward.

## Prerequisites

- Docker and Docker Compose v2
- Python 3.10+
- (Optional) Telegram account for bot exercises

## Intro

- What OpenClaw is: autonomous agent **runtime** + **skills** (tools) + **prompts** (policy and behavior), not a single monolithic script.
- Threat model: untrusted input → LLM → **your** skills → **your** data and systems.
- Learning outcomes: sandbox mental model, one safe skill, where production files live (`skills/`, `prompts/`, `tests/`, `openclaw.yaml`).
- Icebreaker: one example task students *wish* an agent could do — map it to “skill + approval + audit log.”

## Install the OpenClaw package
### use the official installation script, via curl
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### use npm
```bash
npm install -g openclaw@latest
```

### use pnpm
```bash
pnpm add -g openclaw@latest
pnpm approve-builds -g
```

## Then answer the questions
### Question 1: Understand the risks
Continue? Choose yes

### Question 2: Onboarding mode
Choose Quick Start

### Question 3: Model provider
Your own preference

### Question 4: Specific model
Your own preference

### Question 5: Choose a channel
telegram is default, simplest way
but skip this for now

### Question 6: Search provider
skip for now

### Question 7: Configure skills
click yes

### Question 8: install missing skill dependencies
choose clawhub

### Question 9: preferred node manager for skills
choose npm

### Questions 10 - 13
API keys, skip for now

### Question 14 - Hooks
skip for now

## Start gateway service
how to hatch bot? choose in tui (terminal user interface)

verify installation, ask are you online

## how to start convo
always use `openclaw tui` to go back to tui
if gateway not running, need to `openclaw gateway start` first

## Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Purpose |
|----------|---------|
| `LLM_API_KEY` | API key for your LLM provider (when you run model-backed flows). |
| `LLM_BASE_URL` | API default URL path |
| `LLM_MODEL` | Specific model name used |
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) on Telegram. |
| `TELEGRAM_CHAT_ID` | Numeric ID of the chat where the bot should listen/respond. |
| `REQUIRE_EXEC_APPROVAL` | Keep **`true`** unless your facilitator explicitly enables otherwise in a trusted lab. |

Never commit `.env`. It is listed in `.gitignore`.

> ## Security warning — `REQUIRE_EXEC_APPROVAL`
>
> **Set `REQUIRE_EXEC_APPROVAL=true` in `.env` for this workshop and for any environment where the agent can run code, touch the filesystem, or invoke tools.**  
> When this flag is enabled, destructive or high-risk actions (execution, broad writes, privilege changes) should not proceed without explicit human approval in the control channel (e.g. Telegram or dashboard).  
> **Never** disable this in shared, internet-exposed, or untrusted-input scenarios. Treat autonomous agents like privileged automation: default deny, explicit approve.

## Start the stack

From the repository root:

```bash
docker compose up -d
```

Volumes mapped into the container:

| Host path | Role |
|-----------|------|
| `./agent_workspace` | **Execution jail** — default workspace for file skills. |
| `./skills` | Skill code (Python modules). |
| `./prompts` | System prompts / directives (read by the agent runtime). |
| `./logs` | Audit and runtime logs. |

Verify mounts: shell into container or list paths; confirm `OPENCLAW_WORKSPACE_ROOT` matches `/workspace` in compose.

how to verify:
```bash
docker compose ps
# see the mapped directories on host
docker inspect openclaw-workshop-agent --format '{{json .Mounts}}' | jq
# shell into the container
docker exec -it openclaw-workshop-agent sh
# using shell, list all the files
ls -la /workspace /app/skills /app/prompts /var/log/openclaw /app/openclaw.yaml
# confirm OPENCLAW_WORKSPACE_ROOT
docker exec openclaw-workshop-agent printenv OPENCLAW_WORKSPACE_ROOT
# should print /workspace
```

## Telegram bot (optional)

1. Open Telegram, search for **@BotFather**, send `/newbot` (or use an existing bot). Follow the instructions to create your own bot.
2. Copy the **HTTP API token** into `TELEGRAM_BOT_TOKEN` in `.env`.
3. Start a chat with your bot and send `/start`.

must send some message.
<img src="public/CreatedBotConvo.png" alt="Screenshot of talking to your bot" />

4. Obtain your **chat ID**.

make api call to telegram's servers.
replace YOUR_BOT_TOKEN with your bot token, no spaces or other characters
go to <a href=https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates></a>
<img src="public/TelegramChatID.png" alt="Photo of Telegram Chat ID location">


5. Put it in `TELEGRAM_CHAT_ID`.

this telegram bot will connect to openclaw.yaml.

## Where to look next

- `curriculum.md` — full 120-minute schedule.
- `openclaw.yaml` — LLM, Telegram, security env keys, and skill paths.
- `skills/local_file_io.py` — example **sandboxed** read/write skill.
- `prompts/core_directive.md` — example **system prompt** (policy separate from code).
- `tests/test_local_file_io.py` — run `pytest` to verify the skill cannot escape the workspace.

## The “Aha!” File I/O Run

- Open `skills/local_file_io.py` — **read** path validation: realpath + commonprefix against workspace root.
- Run **one** skill invocation: write a small file under `agent_workspace/`, then read it back.
- Show `logs/` or audit trail if wired — tie to compliance narrative.
- **Deliberate failure:** attempt path outside workspace (should refuse). Connect to pytest in next section’s preview.
- **Checkpoint:** Students have created one file inside the jail only.

## Run tests (post-workshop)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pytest
pytest tests/ -v
```

## Security reminder

Keep **`REQUIRE_EXEC_APPROVAL=true`** in real deployments until you have a full trust and monitoring story. See the highlighted box in `curriculum.md`.
