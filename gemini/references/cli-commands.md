# Gemini CLI Commands Reference

## Basic Usage

### One-shot Queries
```bash
gemini "What is the capital of France?"
gemini --model gemini-pro "Explain quantum computing"
```

### Output Formats
```bash
gemini --output-format json "Return a JSON object with user info"
gemini --output-format text "Simple text response"
```

## Model Selection

### Available Models
- `gemini-pro` - Balanced performance
- `gemini-pro-vision` - Multimodal support
- `gemini-ultra` - Highest capability (limited access)

### Model Selection
```bash
gemini --model gemini-pro-vision "Describe this image"
```

## Extensions

### List Extensions
```bash
gemini --list-extensions
```

### Manage Extensions
```bash
gemini extensions list
gemini extensions install <extension-id>
gemini extensions remove <extension-id>
```

## Advanced Options

### Temperature Control
```bash
gemini --temperature 0.7 "Creative writing prompt"
```

### Max Tokens
```bash
gemini --max-tokens 1024 "Detailed explanation"
```

## Authentication

### Initial Setup
```bash
gemini  # Run interactively for first-time auth
```

### API Key
```bash
export GEMINI_API_KEY="your-api-key"
gemini "Authenticated query"
```

## Troubleshooting

### Common Issues
- **Auth required**: Run `gemini` once interactively
- **Model not found**: Check available models with `gemini --list-models`
- **Rate limiting**: Implement exponential backoff