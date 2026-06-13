---
name: openclaw-hermes-docker-config-fix
description: Fix OpenClaw/Hermes multi-agent Docker setup when providers stop working due to hardcoded API keys or misconfigured custom_providers.

triggers:
- OpenClaw agents not functional
- Hermes custom_providers not working
- Mistral API key hardcoded
- Docker containers not using env vars
- Agents failing to authenticate

steps:
1. Diagnose the issue
   - Check agent logs for authentication errors:
     ```bash
     docker logs oc-<agent>
     ```
   - Look for hardcoded API keys in `config.yaml` files.
   - Verify if `custom_providers` is misconfigured (e.g., using `providers: {}` instead of `custom_providers`).

2. Update `config.yaml` for all agents
   - Replace hardcoded API keys with environment variable placeholders:
     ```yaml
     model:
       default: devstral-latest
       provider: mistral
       base_url: https://api.mistral.ai/v1
       api_key: ${MISTRAL_API_KEY}  # or ${OLLAMA_API_KEY}, etc.
       api_mode: chat_completions
     ```
   - Ensure `custom_providers` is used instead of `providers` or `fallback_providers`:
     ```yaml
     custom_providers:
       - name: local
         base_url: http://localhost:11434/v1
         api_mode: chat_completions
         key_env: OLLAMA_API_KEY
         model: qwen3:0.6b
       - name: mistral
         base_url: https://api.mistral.ai/v1
         api_mode: chat_completions
         key_env: MISTRAL_API_KEY
         model: devstral-latest
       - name: codestral
         base_url: https://codestral.mistral.ai/v1
         api_mode: chat_completions
         key_env: CODESTRAL_API_KEY
     ```

3. Create `.env` files for each agent
   - Create a `.env` file in each agent’s directory (e.g., `${OPENCLAW_DIR:-~/.openclaw}/agents/<agent>/.env`):
     ```bash
     echo "MISTRAL_API_KEY=your_key_here" > ${OPENCLAW_DIR:-~/.openclaw}/agents/<agent>/.env
     echo "OLLAMA_API_KEY=your_key_here" >> ${OPENCLAW_DIR:-~/.openclaw}/agents/<agent>/.env
     echo "CODESTRAL_API_KEY=your_key_here" >> ${OPENCLAW_DIR:-~/.openclaw}/agents/<agent>/.env
     ```
   - Ensure the file is readable by the Docker container (no restrictive permissions).

4. Update Docker Compose to pass `.env` files
   - Add `env_file` and environment variables to each agent’s service in `docker-compose.yml`:
     ```yaml
     services:
       <agent>:
         environment:
           - MISTRAL_API_KEY=${MISTRAL_API_KEY}
           - OLLAMA_API_KEY=${OLLAMA_API_KEY}
           - CODESTRAL_API_KEY=${CODESTRAL_API_KEY}
         env_file:
           - ${OPENCLAW_DIR:-~/.openclaw}/agents/<agent>/.env
     ```

5. Rebuild and restart containers
   - Apply changes:
     ```bash
     cd ${OPENCLAW_DIR:-~/.openclaw}/docker
     docker-compose down && docker-compose up -d --build
     ```
   - Verify logs for authentication errors:
     ```bash
     docker logs oc-<agent>
     ```

6. Verify functionality
   - Test each agent’s connectivity to providers:
     ```bash
     docker exec -it oc-<agent> bash
     echo $MISTRAL_API_KEY
     curl -H "Authorization: Bearer $MISTRAL_API_KEY" https://api.mistral.ai/v1/models
     ```

pitfalls:
- **Hardcoded keys**: Never hardcode API keys in `config.yaml`. Always use `key_env` and `.env` files.
- **Permissions**: Ensure `.env` files are readable by Docker (e.g., `chmod 644 ${OPENCLAW_DIR:-~/.openclaw}/agents/<agent>/.env`).
- **Docker Compose**: Use `env_file` to pass environment variables. Do not rely on host environment alone.
- **Hermes alignment**: Hermes must use `custom_providers` instead of `providers` or `fallback_providers`.
- **Gateway configuration**: If agents still fail, check gateway ports and network isolation.

verification:
- All agents start without authentication errors.
- Providers resolve correctly (e.g., Mistral, Ollama, Codestral).
- Logs show no `401 Unauthorized` or `429 Too Many Requests` errors.
