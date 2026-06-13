# Docker Troubleshooting Guide

## Common Issues

### Container Won't Start

Check logs for errors:
```bash
docker logs <container_name>
```

Common causes:
- Missing environment variables
- Port already in use
- Volume mount permissions
- Image entrypoint errors

### Cannot Connect to Container

Verify container is running:
```bash
docker ps -a | grep <container_name>
```

Check network settings:
```bash
docker inspect <container_name> | grep -A 20 NetworkSettings
```

### Out of Disk Space

Check disk usage:
```bash
docker system df
```

Clean up resources:
```bash
docker system prune -a --volumes
```

### Container Uses Too Much Memory

Set memory limits:
```bash
docker run -m 512m --memory-swap 1g <image>
```

## Debugging Techniques

1. **Interactive shell**: `docker exec -it <container> /bin/sh`
2. **Logs streaming**: `docker logs -f <container>`
3. **Resource stats**: `docker stats`
4. **Process list**: `docker top <container>`
5. **Inspect**: `docker inspect <container>`
