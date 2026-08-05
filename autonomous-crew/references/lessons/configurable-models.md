---
title: Configurable Models — Never Hardcode
category: configuration
date: 2026-07-09
failure: >
  Agents hardcoded specific model names (e.g. "qwen-plus-latest") as
  defaults, which breaks for any user on a different provider (OpenAI,
  Anthropic, local models) or without that specific quota.
root_cause: >
  Model selection was written directly into scripts instead of being read
  from a configuration file with environment-based provider auto-detection.
resolution: >
  Introduced config/providers.json with per-provider model lists, an
  env-var-based auto-detection pass (DASHSCOPE_API_KEY, OPENAI_API_KEY,
  ANTHROPIC_API_KEY), and a role_model_mapping layer so callers request a
  role ("reasoning", "creative") rather than a specific model name.
prevention: >
  Always fall back to an explicit "model-not-configured" sentinel rather
  than a real model name as the default — a silent wrong-provider default
  is worse than a loud missing-configuration error.
verified: true
---

# Configurable Models — Never Hardcode

## The Rule

**NEVER hardcode model names in scripts.** Models must be configurable via `config/providers.json` or similar configuration files.

## Why

- Different users have different providers (DashScope, OpenAI, Anthropic, local)
- Different users have different model access/quotas
- Hardcoding breaks portability
- Quotas are per-model, not per-API-key

## Implementation

### 1. Create providers.json

```json
{
  "providers": {
    "dashscope": {
      "name": "DashScope",
      "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "env_key": "DASHSCOPE_API_KEY",
      "models": {
        "text": ["qwen-plus-latest", "qwen3-235b-a22b-thinking-2507"],
        "vision": ["qwen-vl-plus-latest"],
        "embedding": ["text-embedding-v3"]
      }
    }
  },
  "defaults": {
    "primary_model": "model-not-configured",
    "reasoning_model": "model-not-configured"
  },
  "role_model_mapping": {
    "lead": "reasoning_model",
    "creative": "creative_model",
    "general": "primary_model"
  }
}
```

### 2. Auto-detect from Environment

```python
def _detect_available_models(self):
    env_checks = {
        "DASHSCOPE_API_KEY": "dashscope",
        "OPENAI_API_KEY": "openai",
        "ANTHROPIC_API_KEY": "anthropic"
    }
    # Detect which providers are available
    # Load their models from providers.json
    # Fall back to defaults if none found
```

### 3. Select Model by Role

```python
def _select_model_for_role(self, role):
    # Map role to model type via role_model_mapping
    # Get available models for that type
    # Return first available or "model-not-configured"
```

## Pitfall

Many agents hardcode "qwen-plus-latest" or similar as defaults. This breaks when:
- User doesn't have DashScope
- User is on OpenAI/Anthropic
- User is running local models

Always use "model-not-configured" as the fallback and require explicit configuration.
