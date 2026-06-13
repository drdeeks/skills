# Distributed Training

## Data Parallelism
- **DDP (DistributedDataParallel)**: PyTorch native
- Each GPU has full model copy
- Gradients synchronized each step
- Best for: models fitting in single GPU VRAM

## Tensor Parallelism
- Split weight matrices across GPUs
- Each GPU computes partial matmul
- Requires high-bandwidth interconnect (NVLink)
- Best for: large models, single node

## Pipeline Parallelism
- Split layers across GPUs
- Micro-batches flow through pipeline
- Bubble overhead (idle time)
- Best for: very deep models

## ZeRO (Zero Redundancy Optimizer)
- **Stage 1**: Shard optimizer states
- **Stage 2**: + Shard gradients
- **Stage 3**: + Shard parameters (+ activations offload)
- DeepSpeed / FSDP implementation

## FSDP (Fully Sharded Data Parallel)
- PyTorch native ZeRO-3 equivalent
- Flexible sharding strategies
- CPU offload for massive models
- Activation checkpointing

## Multi-Node
- **Network**: InfiniBand, RoCE, or high-bandwidth Ethernet
- **Launcher**: torchrun, accelerate launch, deepspeed
- **Environment**: MASTER_ADDR, MASTER_PORT, WORLD_SIZE, RANK

## Launch Commands
```bash
# Single node, 4 GPUs
torchrun --nproc_per_node=4 train.py

# Multi-node (2 nodes, 4 GPUs each)
torchrun --nproc_per_node=4 --nnodes=2 --node_rank=0 --master_addr=10.0.0.1 train.py

# DeepSpeed
deepspeed --num_gpus=4 train.py --deepspeed_config ds_config.json

# Accelerate
accelerate launch --multi_gpu train.py
```

## Memory Optimization
- Gradient accumulation (simulate large batch)
- Activation checkpointing (recompute vs store)
- CPU offloading (ZeRO-3, FSDP)
- Mixed precision (FP16/BF16)
- Gradient checkpointing
