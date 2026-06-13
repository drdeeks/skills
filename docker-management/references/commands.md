# Docker CLI Commands Quick Reference

## Container Lifecycle

| Command | Description |
|---------|-------------|
| `docker create` | Create a container without starting it |
| `docker run` | Create and start a container |
| `docker start` | Start a stopped container |
| `docker stop` | Stop a running container gracefully |
| `docker restart` | Restart a container |
| `docker pause` | Pause all processes in a container |
| `docker unpause` | Unpause a paused container |
| `docker rm` | Remove a container |
| `docker kill` | Kill a running container with a signal |

## Image Management

| Command | Description |
|---------|-------------|
| `docker build` | Build an image from a Dockerfile |
| `docker pull` | Pull an image from a registry |
| `docker push` | Push an image to a registry |
| `docker images` | List local images |
| `docker rmi` | Remove one or more images |
| `docker tag` | Create a tag for an image |
| `docker save` | Save an image to a tar archive |
| `docker load` | Load an image from a tar archive |

## Docker Compose

| Command | Description |
|---------|-------------|
| `docker compose up` | Create and start containers |
| `docker compose down` | Stop and remove containers |
| `docker compose ps` | List running containers |
| `docker compose logs` | View container output |
| `docker compose exec` | Execute a command in a running container |
| `docker compose build` | Build or rebuild services |
| `docker compose config` | Validate and view compose file |
