# Docker Deployment Guide for File Processing Suite

## Quick Start

### Development Mode

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

### Production Mode

```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale API servers
docker-compose up -d --scale api=3

# View status
docker-compose ps
```

## Services

### API Server (Port 8000)

- REST API endpoints
- WebSocket support
- Plugin management
- <http://localhost:8000/docs>

### PostgreSQL (Port 5432)

- Primary data store
- User data, job history
- Plugin metadata

### Redis (Port 6379)

- Caching layer
- Session storage
- Rate limiting

### Kafka (Port 9092)

- Event streaming
- Async task queue
- Plugin events

### Prometheus (Port 9090)

- Metrics collection
- Time-series data
- <http://localhost:9090>

### Grafana (Port 3000)

- Dashboards
- Visualization
- <http://localhost:3000> (admin/admin)

### NGINX (Port 80/443)

- Reverse proxy
- Load balancing
- SSL termination

## Docker Commands

### Build Image

```bash
# Build API image
docker build -t fileprocessor:latest .

# Build with custom tag
docker build -t fileprocessor:7.0.0 .
```

### Run Single Container

```bash
# Run API only
docker run -p 8000:8000 fileprocessor:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  fileprocessor:latest

# Run with volume mounts
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/plugins:/app/plugins \
  fileprocessor:latest
```

### Manage Containers

```bash
# List running containers
docker-compose ps

# View logs
docker-compose logs api
docker-compose logs -f worker

# Execute commands in container
docker-compose exec api bash
docker-compose exec postgres psql -U user -d fileprocessor

# Restart service
docker-compose restart api

# Stop and remove
docker-compose down
docker-compose down -v  # Also remove volumes
```

## Configuration

### Environment Variables

Create `.env` file:

```env
APP_ENV=production
DATABASE_URL=postgresql://user:password@postgres:5432/fileprocessor
REDIS_URL=redis://redis:6379/0
KAFKA_BROKERS=kafka:9092
API_KEY_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### Volume Mounts

- `./uploads:/app/uploads` - Uploaded files
- `./plugins:/app/plugins` - Plugin directory
- `./logs:/app/logs` - Application logs
- `./cache:/app/cache` - Cache directory
- `./config:/app/config` - Configuration files

## Scaling

### Horizontal Scaling

```bash
# Scale API servers
docker-compose up -d --scale api=5

# Scale workers
docker-compose up -d --scale worker=10
```

### Resource Limits

Edit docker-compose.yml:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Monitoring

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check all services
docker-compose ps
```

### View Metrics

- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>

### Logs

```bash
# Follow all logs
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs api

# Inspect container
docker-compose ps
docker inspect fileprocessor-api
```

### Database connection issues

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U user -d fileprocessor

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Plugin not loading

```bash
# Check plugin directory
docker-compose exec api ls -la /app/plugins

# View plugin logs
docker-compose logs api | grep -i plugin
```

## Production Deployment

### SSL/TLS Setup

1. Get SSL certificates (Let's Encrypt)
2. Update nginx.conf with SSL config
3. Mount certificates:

```yaml
volumes:
  - ./certs:/etc/nginx/certs:ro
```

### Database Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U user fileprocessor > backup.sql

# Restore
docker-compose exec -T postgres psql -U user fileprocessor < backup.sql
```

### Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build

# Zero-downtime deployment (with multiple instances)
docker-compose up -d --no-deps --build api
```

## Security

### Best Practices

1. Use non-root user (already configured)
2. Set strong passwords in .env
3. Enable SSL/TLS in production
4. Regularly update images
5. Scan images for vulnerabilities:

```bash
docker scan fileprocessor:latest
```

### Network Isolation

```bash
# Create isolated network
docker network create fileprocessor-isolated

# Run with isolated network
docker-compose --network fileprocessor-isolated up
```

## Performance Tuning

### PostgreSQL

```bash
# Optimize configuration
docker-compose exec postgres psql -U user -c "
  ALTER SYSTEM SET shared_buffers = '256MB';
  ALTER SYSTEM SET effective_cache_size = '1GB';
"
```

### Redis

```bash
# Set memory limit
docker-compose exec redis redis-cli CONFIG SET maxmemory 512mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Kubernetes Deployment

For production Kubernetes deployment, see:

- `kubernetes/deployment.yaml`
- `kubernetes/service.yaml`
- `kubernetes/ingress.yaml`

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check status
kubectl get pods -n fileprocessor
```

---

**Version**: 7.0.0  
**Last Updated**: January 7, 2026
