# Docker & Containerization Strategy

Complete containerization architecture for AMETHYST 2.0 production deployment.

---

## 🐳 Docker Overview

### Image Strategy

```
AMETHYST Docker Registry: registry.example.com/amethyst-*
│
├── amethyst-client:v2.0.0          # PyQt6 desktop app
│   ├── Base: python:3.11-slim
│   ├── Size: ~400MB (optimized)
│   ├── Platforms: windows/amd64, linux/amd64
│   └── Use: Internal distribution, testing
│
├── amethyst-server:v2.0.0          # FastAPI backend
│   ├── Base: python:3.11-slim
│   ├── Size: ~300MB
│   ├── Platforms: linux/amd64, linux/arm64
│   └── Use: Kubernetes deployment
│
├── amethyst-stt:v2.0.0             # STT microservice
│   ├── Base: python:3.11-slim
│   ├── Size: ~450MB (Whisper/Deepgram)
│   ├── Platforms: linux/amd64, linux/arm64
│   └── Use: Autoscaling STT processing
│
├── amethyst-response-gen:v2.0.0    # Response generation service
│   ├── Base: python:3.11-slim
│   ├── Size: ~350MB
│   ├── Platforms: linux/amd64, linux/arm64
│   └── Use: Autoscaling response generation
│
├── amethyst-question-detect:v2.0.0 # Question classification (optional)
│   ├── Base: python:3.11-slim
│   ├── Size: ~500MB (BERT model)
│   ├── Platforms: linux/amd64
│   └── Use: ML inference service
│
└── amethyst-analytics:v2.0.0       # Analytics processor
    ├── Base: python:3.11-slim
    ├── Size: ~300MB
    ├── Platforms: linux/amd64, linux/arm64
    └── Use: Event processing, analytics
```

---

## 📝 Dockerfile for FastAPI Server

### Production-Grade Dockerfile

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-server.txt .

# Build wheels
RUN pip install --user --no-cache-dir -r requirements-server.txt


# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy wheels from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY src/amethyst-relay/ .

# Update PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create necessary directories
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 9090

# Start application
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--loop", "uvloop", \
     "--log-config", "config/logging_config.yml"]
```

### Multi-Stage Build Benefits

| Benefit | Why |
|---------|-----|
| **Smaller images** | Only runtime deps in final image |
| **Faster deployment** | Build cache reuse across stages |
| **Security** | Remove build tools from runtime |
| **Consistency** | Same deps as local development |

---

## 📝 Dockerfile for PyQt6 Client

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /build

# Install build deps for PyQt6
RUN apt-get update && apt-get install -y \
    build-essential \
    qt6-base-dev \
    qt6-tools-dev \
    libqt6gui6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-client.txt .
RUN pip install --user --no-cache-dir -r requirements-client.txt


FROM python:3.11-slim

WORKDIR /app

# Install runtime deps for PyQt6
RUN apt-get update && apt-get install -y \
    libqt6gui6 \
    libqt6core6 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    pulseaudio \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy wheels
COPY --from=builder /root/.local /home/appuser/.local

# Copy code
COPY src/amethyst-client/ .

# Copy resources
COPY resources/ ./resources/

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/home/appuser/.local/lib/python3.11/site-packages/PyQt6/Qt6/plugins

# Permissions
RUN chown -R appuser:appuser /app

USER appuser

# For X11 display
ENV DISPLAY=:0

EXPOSE 5000

CMD ["python", "main.py"]
```

---

## 🐳 Docker Compose for Local Development

```yaml
version: '3.9'

services:
  # Database
  postgres:
    image: postgres:15-alpine
    container_name: amethyst-postgres
    environment:
      POSTGRES_DB: amethyst
      POSTGRES_USER: amethyst_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U amethyst_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: amethyst-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Server
  server:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.server
    container_name: amethyst-server
    ports:
      - "8000:8000"
      - "9090:9090"
    environment:
      DATABASE_URL: postgresql://amethyst_user:${DB_PASSWORD}@postgres:5432/amethyst
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: development
      LOG_LEVEL: DEBUG
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./src/amethyst-relay:/app
    command: >
      uvicorn main:app
      --host 0.0.0.0
      --port 8000
      --reload
      --log-level debug

  # STT Service
  stt:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.stt
    container_name: amethyst-stt
    ports:
      - "8001:8001"
    environment:
      REDIS_URL: redis://redis:6379
      DEEPGRAM_API_KEY: ${DEEPGRAM_API_KEY}
      ENVIRONMENT: development
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./src/services/stt:/app

  # Monitoring: Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: amethyst-prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./infrastructure/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Monitoring: Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: amethyst-grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infrastructure/monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus

  # Monitoring: Jaeger
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: amethyst-jaeger
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: :9411

  # Elasticsearch for logs
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    container_name: amethyst-elasticsearch
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  # Kibana for log visualization
  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    container_name: amethyst-kibana
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
  elasticsearch_data:

networks:
  default:
    name: amethyst-network
```

---

## 🚀 Docker Compose - Production

```yaml
version: '3.9'

services:
  server:
    image: registry.example.com/amethyst-server:${VERSION}
    container_name: amethyst-server
    restart: always
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      VAULT_ADDR: ${VAULT_ADDR}
      VAULT_TOKEN: ${VAULT_TOKEN}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🐳 Image Registry & Scanning

### Container Image Security

```bash
# Build with security scanning
docker build \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  --build-arg VERSION=2.0.0 \
  --label org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --label org.opencontainers.image.authors="AMETHYST Team" \
  --label org.opencontainers.image.url="https://github.com/amethyst/server" \
  --label org.opencontainers.image.documentation="https://docs.amethyst.io" \
  --label org.opencontainers.image.source="https://github.com/amethyst/server" \
  --label org.opencontainers.image.version="2.0.0" \
  --label org.opencontainers.image.revision=$(git rev-parse --short HEAD) \
  -t amethyst-server:2.0.0 \
  -f infrastructure/docker/Dockerfile.server .

# Scan with Trivy before push
trivy image amethyst-server:2.0.0

# Scan with Snyk
snyk container test amethyst-server:2.0.0

# Push to registry
docker push amethyst-server:2.0.0
```

### Registry Configuration

```yaml
# .docker/config.json
{
  "auths": {
    "registry.example.com": {
      "auth": "base64-encoded-token"
    }
  },
  "credStore": "pass",  # Use system credential store
  "experimental": "enabled",
  "features": {
    "buildkit": true
  }
}

# ECR authentication
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com
```

---

## 🐳 Docker Network & Storage

### Production Network Setup

```yaml
networks:
  amethyst-internal:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1500
    ipam:
      config:
        - subnet: 10.0.1.0/24

  amethyst-external:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.2.0/24
```

### Persistent Volume Strategy

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server.local,vers=4,soft,timeo=30
      device: ":/export/postgres"

  redis_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server.local,vers=4,soft
      device: ":/export/redis"

  elasticsearch_data:
    driver: local
    driver_opts:
      type: nfs
      device: ":/export/elasticsearch"
```

---

## 🔐 Security Best Practices

### Runtime Security

```dockerfile
# Use minimal base images
FROM python:3.11-slim

# Run as non-root
USER appuser

# Set security options
RUN chmod 755 /app

# Remove unnecessary packages
RUN apt-get remove curl wget --yes && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/apt/lists/*

# Use read-only filesystem where possible
RUN touch /app/.dockerenv && \
    chmod 444 /app/.dockerenv

# Scan secrets
RUN pip install --user git+https://github.com/Yelp/detect-secrets.git
```

### Secret Management

```bash
# Use Docker secrets (Swarm) or K8s secrets
# Never pass secrets as environment variables

# Instead, mount secret files:
docker run \
  --secret gemini_api_key \
  --secret db_password \
  amethyst-server:2.0.0
```

---

## 📊 Image Size Optimization

### Before & After

```
BEFORE (Unoptimized):
amethyst-server:v1  800MB
  └─ Python 3.11:     300MB
  └─ Dependencies:    400MB
  └─ Code:             20MB
  └─ Build tools:      80MB

AFTER (Optimized):
amethyst-server:v2  300MB
  └─ Python 3.11-slim: 125MB
  └─ Dependencies:    160MB (wheels only)
  └─ Code:             15MB
  └─ Build tools:    removed

Optimization techniques:
1. Multi-stage builds (remove build deps)
2. Slim base images (python:3.11-slim)
3. Pip cache cleanup
4. Layer caching strategy
5. Dependency pinning (reproducible builds)
```

---

## 🔄 Build & Push Pipeline

### GitHub Actions Workflow

```yaml
name: Build & Push Docker Images

on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        image:
          - name: amethyst-server
            dockerfile: Dockerfile.server
          - name: amethyst-stt
            dockerfile: Dockerfile.stt
          - name: amethyst-client
            dockerfile: Dockerfile.client
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to ECR
        uses: docker/login-action@v2
        with:
          registry: ${{ secrets.ECR_REGISTRY }}
          username: ${{ secrets.AWS_ACCESS_KEY_ID }}
          password: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./infrastructure/docker/${{ matrix.image.dockerfile }}
          push: true
          tags: |
            ${{ secrets.ECR_REGISTRY }}/amethyst-${{ matrix.image.name }}:latest
            ${{ secrets.ECR_REGISTRY }}/amethyst-${{ matrix.image.name }}:${{ github.sha }}
          cache-from: type=registry,ref=${{ secrets.ECR_REGISTRY }}/amethyst-${{ matrix.image.name }}:buildcache
          cache-to: type=registry,ref=${{ secrets.ECR_REGISTRY }}/amethyst-${{ matrix.image.name }}:buildcache,mode=max
      
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ secrets.ECR_REGISTRY }}/amethyst-${{ matrix.image.name }}:latest
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

**Status**: Production-Ready  
**Version**: 2.0 Enterprise  
**Last Updated**: March 5, 2026  
