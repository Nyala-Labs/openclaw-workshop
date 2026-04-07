# OpenClaw gateway + Python for any workshop skills invoked by the runtime
# openclaw@latest requires Node.js v22.12+ (see container logs if gateway restarts)
# Gateway starts via Dockerfile CMD (`openclaw gateway run …`)
FROM node:22-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates git python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest \
@buape/carbon \
@larksuiteoapi/node-sdk \
@slack/web-api @slack/bolt @slack/logger \
@grammyjs/runner @grammyjs/transformer-throttler \
@whiskeysockets/baileys \
@slack/web-api @slack/bolt \
discord-api-types @discordjs/voice


ENV HOME=/app
WORKDIR /app

# overwritten with .openclaw_container mapping, but can keep for non-compose runs
RUN mkdir -p /app/.openclaw

# Foreground gateway; --bind lan listens beyond loopback so published ports work from the host.
CMD ["openclaw", "gateway", "run", "--port", "18789", "--bind", "lan"]