# Fine-Tuning Methods

## Full Fine-Tuning
- Update all parameters
- Highest quality, highest compute
- Requires: 2-4x model size in VRAM
- Use: When domain shift is large

## LoRA (Low-Rank Adaptation)
- Freeze base model, train adapters
- Rank r=8-64 typical
- 100-1000x fewer params
- Quality near full fine-tune

## QLoRA (Quantized LoRA)
- 4-bit base model + LoRA
- Fits 7B on 24GB, 70B on 48GB
- Minimal quality loss vs LoRA
- Default choice for most cases

## PEFT (Parameter-Efficient FT)
- LoRA, AdaLoRA, IA3, Prompt Tuning
- Hugging Face PEFT library
- Combinable methods
- Easy integration with Trainer

## Choosing Method
| Model Size | VRAM | Method |
|------------|------|--------|
| < 1B | 8GB | Full / LoRA |
| 1-7B | 16-24GB | QLoRA / LoRA |
| 7-13B | 24-48GB | QLoRA |
| 13-70B | 48-80GB | QLoRA (multi-GPU) |
| > 70B | 80GB+ | QLoRA + FSDP/DeepSpeed |

## Hyperparameters
- **LoRA rank**: 8 (efficient) - 64 (quality)
- **LoRA alpha**: 16-32 (typically 2x rank)
- **Learning rate**: 1e-4 (LoRA) - 2e-5 (full)
- **Batch size**: Max that fits VRAM
- **Epochs**: 1-3 (usually sufficient)
