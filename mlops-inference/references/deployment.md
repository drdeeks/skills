# Inference Deployment

## Docker
```dockerfile
FROM vllm/vllm-openai:latest
ENTRYPOINT ["python", "-m", "vllm.entrypoints.openai.api_server"]
CMD ["--model", "meta-llama/Llama-2-7b-chat-hf", "--port", "8000"]
```

## Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args: ["--model", "meta-llama/Llama-2-7b-chat-hf"]
        resources:
          limits:
            nvidia.com/gpu: 1
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: llm-inference
spec:
  selector:
    app: llm-inference
  ports:
  - port: 80
    targetPort: 8000
```

## Cloud Services
- **AWS**: SageMaker, Inferentia, Trainium
- **GCP**: Vertex AI, TPU
- **Azure**: ML, ND-series VMs
- **RunPod**: GPU cloud, per-second billing
- **Lambda Labs**: GPU cloud, competitive pricing

## Scaling
- **HPA**: Horizontal Pod Autoscaler (CPU/memory/custom)
- **KEDA**: Event-driven scaling (queue depth)
- **Custom Metrics**: Request latency, queue length

## Load Balancing
- **Round Robin**: Simple distribution
- **Least Connections**: Route to least busy
- **Consistent Hashing**: Session affinity
- **Token-Aware**: Route by prompt prefix

## Security
- **Authentication**: API keys, JWT, OAuth
- **Rate Limiting**: Per-client limits
- **Encryption**: TLS termination
- **Audit Logging**: Request/response logging
