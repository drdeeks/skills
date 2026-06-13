# nano-pdf API Reference

## CLI Commands

### nano-pdf edit
Edit a PDF page with natural language instructions.

**Syntax:**
```bash
nano-pdf edit <input.pdf> <page> <instruction> [options]
```

**Options:**
- `--output <file>` - Output file (default: input-edited.pdf)
- `--model <model>` - LLM model to use
- `--dry-run` - Preview changes without applying

### nano-pdf preview
Preview changes without applying.

**Syntax:**
```bash
nano-pdf preview <input.pdf> <page> <instruction>
```

## Environment Variables

- `NANO_PDF_MODEL` - Default model to use
- `NANO_PDF_API_KEY` - API key for LLM provider
