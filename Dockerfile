# OpenClaw gateway + Python for any workshop skills invoked by the runtime
# openclaw@latest requires Node.js v22.12+ (see container logs if gateway restarts)
# Gateway starts via Dockerfile CMD (`openclaw gateway run …`)
FROM node:22-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest

ENV HOME=/app
WORKDIR /app

RUN mkdir -p /app/.openclaw

# Foreground gateway; --bind lan listens beyond loopback so published ports work from the host.
# --allow-unconfigured avoids hard-failing when local dev config is minimal (see OpenClaw docs).
CMD ["openclaw", "gateway", "run", "--port", "18789", "--bind", "lan", "--allow-unconfigured"]
