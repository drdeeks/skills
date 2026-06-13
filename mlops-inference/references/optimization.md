# Inference Optimization

## Quantization
- **INT8**: 2x memory reduction, minimal quality loss
- **INT4**: 4x memory reduction, some quality loss
- **GPTQ**: Post-training quantization for LLMs
- **AWQ**: Activation-aware weight quantization
- **BitsAndBytes**: 4-bit/8-bit loading

## Batching
- **Continuous Batching**: Dynamic batch scheduling (vLLM)
- **Static Batching**: Fixed batch size
- **Batch Size Tuning**: Balance latency vs throughput

## Parallelism
- **Tensor Parallelism**: Split model across GPUs
- **Pipeline Parallelism**: Split layers across GPUs
- **Data Parallelism**: Replicate model, split data

## Caching
- **KV Cache**: Attention key/value caching
- **Prefix Caching**: Shared prompt prefixes
- **Speculative Decoding**: Small model predicts, large verifies

## Hardware
- **GPU**: NVIDIA H100, A100, A10G, T4
- **TPU**: Google Cloud TPU v4/v5
- **CPU**: Intel AMX, AMD AVX-512
- **Specialized**: Groq LPU, Cerebras

## Monitoring
- **Latency**: p50, p95, p99
- **Throughput**: tokens/sec, requests/sec
- **GPU Utilization**: Compute, memory
- **Queue Depth**: Pending requests
