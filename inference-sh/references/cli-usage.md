# inference.sh CLI Usage

## Installation
```bash
# Install CLI
pip install inference-sh
# or
curl -fsSL https://inference.sh/install.sh | sh
```

## Authentication
```bash
# Set API key
export INFERENCE_API_KEY="your-key"
# or
infsh auth login
```

## Basic Commands
```bash
# List available models
infsh models list

# Image generation
infsh generate image --prompt "a cat" --model flux

# Video generation
infsh generate video --prompt "dancing cat" --model wan

# LLM chat
infsh chat --model claude-3-opus --message "Hello"

# Search
infsh search "AI news" --engine tavily
```

## Advanced Usage
```bash
# Batch generation
infsh generate image --prompt-file prompts.txt --output-dir ./images

# Custom parameters
infsh generate image --prompt "cat" --width 1024 --height 1024 --steps 30

# Save to file
infsh generate image --prompt "cat" --output cat.png
```

## Configuration
```yaml
# ~/.config/inference/config.yaml
api_key: ${INFERENCE_API_KEY}
default_model: flux
output_dir: ./output
timeout: 120
```
