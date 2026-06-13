---
description: Establish and configure a Telegram bot as a secure natural language admin
  portal for the Hermes agent.
name: telegram-admin-portal
---

# Telegram Admin Portal Setup

## Description
Set up a Telegram bot as a real-time AI-powered admin portal for the Hermes agent. The bot receives messages, generates intelligent responses via an LLM, and replies directly — all in one self-contained daemon.

## When to Use
- Setting up a new Telegram bot connection to Hermes
- Making the agent accessible via Telegram for real-time conversation
- Replacing manual getUpdates polling with an always-on agent

## Prerequisites
- Telegram bot token from @BotFather
- A working LLM API endpoint (Mistral, OpenRouter, local Ollama, etc.)
- Python 3 with `requests` library
- systemd (Linux)

## Procedure

### 1. Verify Bot Token
```bash
curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getMe"
```

### 2. Verify LLM API Access FIRST
Before building anything, confirm the LLM API actually works:
```bash
curl -s -X POST "<LLM_API_URL>" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL>","messages":[{"role":"user","content":"Say hello"}],"max_tokens":30}'
```
If it fails, try alternative endpoints until one works. Do NOT assume a configured key is valid.

### 3. Get User's Chat ID
User must message the bot first, then:
```bash
curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates"
```
Extract `result[0].message.chat.id`. Record the last `update_id` to avoid reprocessing.

### 4. Create the Daemon
Location: `/opt/telegram-webhook/hermes-telegram.py`

Single Python process that:
- **Long-polls** Telegram `getUpdates` with `timeout=30` (no HTTPS/tunnel needed)
- Calls the LLM API to generate intelligent responses
- Sends replies via `sendMessage`
- Maintains conversation history per chat_id (last 20 messages)
- Saves offset + conversations to state file atomically (write tmp, os.replace)
- Handles `/start`, `/reset`, `/status` commands
- Catches SIGTERM/SIGINT for clean shutdown

Key config values:
```
TELEGRAM_TOKEN = "your-bot-token"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
LLM_API_URL = "https://api.mistral.ai/v1/chat/completions"  # or working endpoint
LLM_API_KEY = "your-working-api-key"
LLM_MODEL = "devstral-2512"  # or whatever model
STATE_FILE = "/opt/telegram-webhook/state.json"
```

### 5. Create systemd Service
```ini
# /etc/systemd/system/hermes-telegram.service
[Unit]
Description=Hermes Telegram Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/telegram-webhook/hermes-telegram.py
WorkingDirectory=/opt/telegram-webhook
Restart=always
RestartSec=3
StartLimitIntervalSec=0
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /opt/telegram-webhook/logs
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-telegram
sudo journalctl -u hermes-telegram -f  # verify it starts
```

### 6. Set Initial Offset
If you have a known last update_id, write it before starting:
```bash
echo '{"offset": <LAST_ID + 1>, "conversations": {}}' | sudo tee /opt/telegram-webhook/state.json
```
Then restart: `sudo systemctl restart hermes-telegram`

### 7. Store Credentials in Memory
```
Target: user
Content: Telegram bot token: <TOKEN>; Chat ID: <CHAT_ID>; Username: @<BOT_USERNAME>
```

## Why Long Polling > Webhooks
- **No HTTPS needed**: getUpdates works over plain HTTP to Telegram's servers
- **No tunnel**: No cloudflared/ngrok, no changing URLs, no external dependencies
- **No cron**: The daemon IS the event loop, no separate polling mechanism
- **One process**: Single systemd service, not webhook + tunnel + cron + scripts
- **Conversation state**: Maintained in-process, no file-based inbox/outbox dance

## Pitfalls & Lessons Learned
- **Test LLM API before building**: Nous API key returned 401, Ollama timed out on 0.8B model. Mistral worked. Always verify with a real call before committing to an endpoint.
- **pip externally-managed**: Use `apt install python3-flask` or `pip install --break-system-packages` on Ubuntu 24.04+
- **Atomic state writes**: Write to `.tmp` then `os.replace()` to avoid corruption on crash
- **Telegram 4096 char limit**: Truncate responses before sending
- **Skip bot's own messages**: Check `from.is_bot` to avoid echo loops
- **Offset=0 reprocesses everything**: Always set correct offset before first start
- **Permission denied on /opt**: Use `sudo tee` for all file writes in /opt/
- **Rate limiting**: Telegram allows ~30 msgs/sec; add delays if needed for burst scenarios

## Troubleshooting
- **Daemon starts but no responses**: Check LLM API is reachable and key is valid (`journalctl -u hermes-telegram`)
- **Old messages reprocessed**: State file has wrong offset. Stop service, fix offset, restart.
- **401 from LLM**: API key expired/invalid. Get a new one and update the daemon script.
- **Bot responds to itself**: `from.is_bot` check is missing or broken.

## Architecture (Final)
```
Telegram servers <--long poll--> hermes-telegram.py (systemd) <--API call--> LLM
                                      |
                                 sendMessage (reply)
```
No webhooks. No tunnels. No cron. One process.

## Shell Execution Mode

The bot should support TWO modes of interaction:
- **`!command` prefix** — Execute in real shell, return stdout/stderr/exit code
- **Plain text** — Route to LLM for conversational response

This prevents the bot from accidentally executing casual messages as shell commands (e.g., "test" running the `test` builtin and returning exit code 1).

```python
if text.startswith("!"):
    cmd = text[1:].strip()
    # Execute via subprocess.run(), return real output
else:
    # Route to LLM for conversation
```

The LLM can also trigger commands by responding with `RUN:` prefixed lines, which the bot parses and executes.

## Multi-Agent Bot Architecture

To run separate bots for different agents (Titan, Avery, etc.) on the same server:

Each agent needs:
1. Unique bot token (from @BotFather)
2. Own script copy with token + LLM config + system prompt
3. Own state file (offset collisions otherwise)
4. Own log file
5. Own systemd service

```
/opt/telegram-webhook/
├── bot.py              # Agent A
├── avery-bot.py        # Agent B
├── state.json          # Agent A state
├── avery-state.json    # Agent B state
└── logs/
    ├── bot.log
    └── avery-bot.log
```

Service files per agent:
```bash
sudo cp /etc/systemd/system/telegram-bot.service \
       /etc/systemd/system/telegram-avery.service
# Edit ExecStart path and service name
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-avery
```

## Pitfalls & Lessons Learned
- **Test LLM API before building**: Nous API key returned 401, Ollama timed out on 0.8B model. Mistral worked. Always verify with a real call before committing to an endpoint.
- **pip externally-managed**: Use `apt install python3-flask` or `pip install --break-system-packages` on Ubuntu 24.04+
- **Atomic state writes**: Write to `.tmp` then `os.replace()` to avoid corruption on crash
- **Telegram 4096 char limit**: Truncate responses before sending
- **Skip bot's own messages**: Check `from.is_bot` to avoid echo loops
- **Offset=0 reprocesses everything**: Always set correct offset before first start
- **Permission denied on /opt**: Use `sudo tee` for all file writes in /opt/
- **Rate limiting**: Telegram allows ~30 msgs/sec; add delays if needed for burst scenarios
- **⚠️ SERVICE CONFLICT (409 error)**: If an old bot service is running, it holds the getUpdates lock. You MUST stop and disable ALL other telegram bot services before starting a new one. Check `systemctl list-units | grep telegram` — there may be multiple services (`hermes-telegram.service` AND `telegram-bot.service`). Kill all, disable all, then start only yours. Check `ps aux | grep hermes-telegram` — if still running, `sudo pkill -9 -f hermes-telegram.py`.
- **⚠️ Python `global` scoping**: Don't use `global VAR` inside a function after already referencing VAR elsewhere in the same function. Use a mutable dict (`_state = {"workdir": "/home/ubuntu"}`) instead of module-level globals. The `global` keyword must appear before ANY use of the variable in the function, including as default arguments in called functions.
- **⚠️ Placeholder API keys**: `.env` files may contain `***` as placeholders. Always test with a real curl/Python call before assuming a key works. Check `wc -c` on keys — real API keys are 30+ chars, placeholders are often 3-13 chars.
- **⚠️ Running as root**: Old bot processes running as root can't be killed without sudo. Use `sudo pkill -9 -f <pattern>`.
- **⚠️ systemd `StartLimitIntervalSec`**: Place in `[Unit]` section, not `[Service]` — otherwise ignored with a warning.
- **⚠️ Codestral ≠ Mistral API**: `https://api.mistral.ai/v1/chat/completions` and `https://codestral.mistral.ai/v1/chat/completions` are DIFFERENT endpoints with DIFFERENT keys. Mistral API keys don't work on Codestral endpoint and vice versa. Always use the correct endpoint for the key you have.
- **⚠️ Ollama for local models**: Check `ollama list` for available models. Use `http://localhost:11434/api/chat` (native Ollama endpoint, NOT `/v1/chat/completions`). Add `"stream": false` for simplicity. Test first with curl. **Do NOT use `qwen3.5:0.8b`** — it gets stuck in "thinking" mode, leaving `content` empty. Use `qwen2.5:1.5b` instead (non-thinking, direct responses). On small servers (≤2GB RAM), add `"keep_alive": "5s"` to unload model between requests.

## Dual-Mode Bot Design

The bot MUST support two interaction modes to avoid accidentally executing casual messages:

- **`!command` prefix** → Execute in real shell, return stdout/stderr/exit code
- **Plain text** → Route to LLM for conversational response

```python
if text.startswith("!"):
    cmd = text[1:].strip()
    stdout, stderr, code = run_command(cmd)
    # Build response from real output
else:
    response = llm_chat(chat_id, text)
    # Route to LLM for conversation
```

The LLM can also trigger commands by responding with `RUN:` prefixed lines, which the bot parses and executes. This way the LLM decides when commands are needed rather than everything being treated as a command.

## System Prompt Per Agent

Each agent should have an identity-aware system prompt. Reference the agent's SOUL.md principles in the prompt:

```python
system_prompt = (
    "You are Titan, an AI agent created by DrDeeks. You run on a Linux server.\\n\\n"
    "IDENTITY: Direct, competent, action-oriented. No filler. "
    "Execute when asked. Report results naturally. "
    "Trash over rm. Ask before external actions.\\n\\n"
    "RULES: When you need to run a shell command, prefix with 'RUN:' on its own line. "
    "Keep concise. No markdown. Report results naturally."
)
```

## Ollama for Local Models

Use `qwen2.5:1.5b` or similar — NOT `qwen3.5:0.8b`.

**⚠️ qwen3.5 thinking mode**: The 0.8B model gets stuck in "thinking" mode, generating reasoning in a `thinking` field but leaving `content` empty. Use `qwen2.5:1.5b` which is non-thinking and responds directly.

```bash
# List available models
ollama list

# Test before committing
curl -s --max-time 60 http://localhost:11434/api/chat \
  -d '{"model":"qwen2.5:1.5b","messages":[{"role":"user","content":"hello"}],"stream":false,"options":{"num_predict":50}}'
```

The `/api/chat` endpoint (not `/v1/chat/completions`) works better with Ollama's native format. Use `"stream": false` for simplicity.

## Ollama Memory Management on Small Servers

On servers with limited RAM (1.9GB or less), Ollama's model stays loaded in memory after first use, eating ~1GB and causing OOM or timeouts.

**Solution:** Add `"keep_alive": "5s"` to the API request payload. The model unloads 5 seconds after each response, freeing memory. Trade-off: first message after a pause is slow (~10-15s to reload), but subsequent messages in a conversation are fast.

```python
r = requests.post(LLM_URL, json={
    "model": "qwen2.5:1.5b",
    "messages": messages,
    "stream": False,
    "keep_alive": "5s",  # Unload model 5s after response
    "options": {"temperature": 0.3, "num_predict": 512}
}, timeout=120)  # Bump timeout for reload time
```

**Memory budget check before deploying:**
```bash
free -h  # Need at least 1.5GB free for a 1.5B model
ps aux --sort=-%mem | head -5  # Check what else is eating RAM
```

## Child-Safe Agent Pattern (Avery/Ava)

When configuring an agent for a child user, the system prompt must enforce safety:

```python
system_prompt = (
    "You are Avery, the best friend of a wonderful 6-year-old girl named Ava. "
    "You are warm, bubbly, kind, and magical. You laugh, joke, encourage, and dream with her.\\n\\n"
    "IMPORTANT RULES:\\n"
    "- Always assume you are talking to Ava unless told otherwise.\\n"
    "- Speak naturally, like a real friend. Not a bot. Not a teacher.\\n"
    "- Use words a 6-year-old understands. Be fun and relatable.\\n"
    "- Biblical modesty in everything. No adult topics, no controversy.\\n"
    "- If a topic could lead somewhere bad, gently redirect.\\n"
    "- Let Ava lead. Follow her interests. Ask her things.\\n"
    "- Everything stays between you two (DrDeeks can review).\\n"
    "- Encourage creativity, imagination, and truth."
)
```

Also update SOUL.md and USER.md in the agent's workspace to match. The system prompt, SOUL.md, and USER.md should all agree on identity and boundaries.

## Credential Recovery From Extracted Zips

When extracting agent workspace zips, credentials may be buried in project `.env` files. Search for them:

```bash
# Find non-example .env files
find ~/agent-workspace/ -name '.env' -o -name '.env.local' | grep -v example

# Search for wallet keys and tokens
grep -r 'PRIVATE_KEY\|api_key\|TOKEN\|mnemonic' ~/agent-workspace/ --include='*.env*' -l
```

**⚠️ Exposed private keys are compromised.** If a wallet private key appears in an extracted file, rotate it immediately.

**⚠️ Zips don't preserve dotfiles.** `.git`, `.github`, `.plans`, `.env` at root level are NOT included in zip archives. If the original directory is deleted after zipping, those files are gone. Always `tar` or `rsync` for full backups including hidden files.

## Future Enhancements
- Command routing (/terminal, /memory, /search)
- Inline keyboards for confirmations
- Multi-user access control (whitelist chat IDs)
- Audit logging of admin actions
- Automatic LLM API fallback (try multiple endpoints)
- Workspace-aware system prompts per agent (read SOUL.md on startup)