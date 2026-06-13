# Training Frameworks

## PyTorch Lightning
- Structured training loops
- Distributed training (DDP, FSDP, DeepSpeed)
- Callbacks, loggers, profilers
- 16-bit precision (AMP)

## Hugging Face Transformers + Trainer
- Pre-trained model hub
- Trainer API for easy training
- PEFT integration (LoRA, QLoRA)
- Accelerate for multi-GPU

## Axolotl
- LLM fine-tuning focused
- YAML config-driven
- Supports LoRA, QLoRA, full fine-tune
- Multi-GPU with FSDP/DeepSpeed

## Unsloth
- 2-5x faster training
- Memory efficient
- Supports LLaMA, Mistral, Gemma
- QLoRA optimized

## TRL (Transformer Reinforcement Learning)
- PPO, DPO, GRPO trainers
- Reward modeling
- RLHF pipeline

## DeepSpeed
- ZeRO optimization (stage 1/2/3)
- Pipeline parallelism
- 1-bit Adam
- Megatron-LM integration

## FSDP (Fully Sharded Data Parallel)
- Native PyTorch
- Shard parameters, gradients, optimizer states
- CPU offloading
- Activation checkpointing
