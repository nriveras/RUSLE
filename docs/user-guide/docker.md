# Docker Deployment

Deploy RUSLE as a containerized application using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)
- Google Earth Engine credentials (authenticated locally)

## Quick Start

```bash
# Authenticate GEE on host machine first
earthengine authenticate

# Start the application
docker-compose up -d
```

Access at **[http://localhost:8000/app](http://localhost:8000/app)**

## Configuration

### Environment Variables

Create a `.env` file or set variables in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSLE_GEE_PROJECT` | `ee-nriveras` | Google Earth Engine project ID |
| `RUSLE_DEBUG` | `false` | Enable debug logging |
| `RUSLE_MAX_UPLOAD_SIZE_MB` | `50` | Maximum file upload size |
| `RUSLE_MAX_AOI_AREA_KM2` | `50000` | Maximum area of interest |
| `RUSLE_DEFAULT_EXPORT_SCALE` | `90` | Default export resolution (meters) |

### docker-compose.yml

```yaml
services:
  rusle-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rusle-web
    ports:
      - "8000:8000"
    environment:
      - RUSLE_GEE_PROJECT=${RUSLE_GEE_PROJECT:-ee-nriveras}
      - RUSLE_DEBUG=${RUSLE_DEBUG:-false}
    volumes:
      # GEE credentials (required)
      - ~/.config/earthengine:/home/appuser/.config/earthengine:ro
      # Data persistence
      - ./data/uploads:/app/data/uploads
      - ./data/output:/app/data/output
    restart: unless-stopped
```

## Volume Mounts

| Mount | Purpose |
|-------|---------|
| `~/.config/earthengine` | GEE authentication credentials (read-only) |
| `./data/uploads` | Uploaded shapefiles and GeoJSON |
| `./data/output` | Generated outputs and exports |

!!! warning "Credentials Required"
    The container requires GEE credentials mounted from the host. Always authenticate with `earthengine authenticate` before running.

## Building the Image

### Using Docker Compose

```bash
# Build and start
docker-compose up --build

# Build only
docker-compose build
```

### Using Docker Directly

```bash
# Build image
docker build -t rusle-app .

# Run container
docker run -d \
  -p 8000:8000 \
  -v ~/.config/earthengine:/home/appuser/.config/earthengine:ro \
  -v $(pwd)/data:/app/data \
  -e RUSLE_GEE_PROJECT=your-project-id \
  --name rusle-web \
  rusle-app
```

## Production Deployment

### With Nginx Reverse Proxy

```yaml
# docker-compose.prod.yml
services:
  rusle-app:
    build: .
    expose:
      - "8000"
    environment:
      - RUSLE_DEBUG=false

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - rusle-app
```

### Health Checks

The application exposes a health endpoint:

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Container Won't Start

Check logs:

```bash
docker-compose logs -f rusle-app
```

Common issues:

- **Credentials not mounted**: Ensure `~/.config/earthengine` exists
- **Port in use**: Change the port mapping in `docker-compose.yml`

### GEE Authentication Errors

```bash
# Re-authenticate on host
earthengine authenticate --force

# Restart container
docker-compose restart
```

### Permission Errors

If the container can't write to data directories:

```bash
# Fix permissions
chmod -R 777 data/
```

## Updating

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build -d
```
