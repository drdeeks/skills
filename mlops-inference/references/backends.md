# Inference Backends

## vLLM
- **Description**: High-throughput LLM inference
- **Features**: PagedAttention, continuous batching, quantization
- **Models**: LLaMA, Mistral, Falcon, MPT, etc.
- **API**: OpenAI-compatible
- **Deploy**: Docker, Kubernetes, bare metal

## TGI (Text Generation Inference)
- **Description**: Hugging Face's production inference
- **Features**: Tensor parallelism, quantization, streaming
- **Models**: All HF transformers models
- **API**: OpenAI-compatible
- **Deploy**: Docker, Kubernetes

## Triton Inference Server
- **Description**: NVIDIA's multi-framework server
- **Features**: Model pipelining, ensemble, multi-GPU
- **Frameworks**: TensorFlow, PyTorch, ONNX, TensorRT
- **API**: gRPC, HTTP
- **Deploy**: Docker, Kubernetes, Triton Model Repository

## TorchServe
- **Description**: PyTorch native model serving
- **Features**: Multi-model, batching, metrics
- **Models**: PyTorch, TorchScript
- **API**: REST, gRPC
- **Deploy**: Docker, Kubernetes, bare metal

## Comparison
| Backend | Best For | Latency | Throughput | Ease of Use |
|---------|----------|---------|------------|-------------|
| vLLM | LLM serving | Low | Very High | Medium |
| TGI | HF models | Low | High | High |
| Triton | Multi-framework | Low | High | Medium |
| TorchServe | PyTorch | Medium | Medium | High |
