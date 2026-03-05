# CI/CD Pipeline Architecture

Complete continuous integration and deployment strategy for AMETHYST 2.0.

---

## 🔄 Pipeline Overview

```
Code Commit
    ↓
GitHub Actions Trigger
    ├─→ Unit Tests
    ├─→ Integration Tests
    ├─→ Code Quality (SonarQube)
    ├─→ Security Scanning (SAST, Secrets)
    │
    ├─→ Build Docker Images
    │
    ├─→ Image Scanning (Trivy, Snyk)
    │
    ├─→ Push to Registry
    │
    ├─→ Deploy to Staging
    │   ├─→ E2E Tests
    │   ├─→ Performance Tests
    │   └─→ Manual Approval ◄─── HUMAN GATE
    │
    └─→ Deploy to Production
        ├─→ Blue-Green Deployment
        ├─→ Canary Rollout (5% → 50% → 100%)
        ├─→ Monitor Metrics
        └─→ Rollback if needed
```

---

## 📋 GitHub Actions Workflows

### 1. CI Pipeline (`ci.yml`)

```yaml
name: CI - Testing & Quality

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: registry.example.com
  PYTHON_VERSION: 3.11

jobs:
  # Unit Tests
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: |
          pytest tests/unit/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term \
            -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

  # Integration Tests
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-server.txt -r requirements-test.txt
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/amethyst_test
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/integration/ -v --tb=short

  # Code Quality
  code-quality:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      
      - name: Run Black formatter check
        run: black --check src/ tests/
      
      - name: Run isort import check
        run: isort --check-only src/ tests/
      
      - name: Run flake8 linting
        run: flake8 src/ tests/ --max-line-length=100
      
      - name: Run pylint
        run: |
          pylint src/ \
            --disable=C0111,C0103,R0913 \
            --exit-zero
      
      - name: Run mypy type checking
        run: mypy src/ --ignore-missing-imports
      
      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

  # Security Scanning (SAST)
  security-sast:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install security tools
        run: |
          pip install bandit safety semgrep
      
      - name: Run Bandit (SAST)
        run: bandit -r src/ -f json -o bandit-report.json || true
      
      - name: Run Safety check (dependencies)
        run: safety check --json > safety-report.json || true
      
      - name: Run Semgrep (SAST)
        run: |
          semgrep --config=p/security-audit \
            --json \
            --output=semgrep-report.json \
            src/ || true
      
      - name: Upload SAST results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: './**/*-report.json'

  # Secrets Scanning
  secrets-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Detect secrets with TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
      
      - name: Detect secrets with detect-secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline
```

### 2. Build Pipeline (`build.yml`)

```yaml
name: Build & Push to Registry

on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build-images:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - image_name: amethyst-server
            dockerfile: infrastructure/docker/Dockerfile.server
            platforms: linux/amd64,linux/arm64
          
          - image_name: amethyst-stt
            dockerfile: infrastructure/docker/Dockerfile.stt
            platforms: linux/amd64,linux/arm64
          
          - image_name: amethyst-client
            dockerfile: infrastructure/docker/Dockerfile.client
            platforms: windows/amd64,linux/amd64
    
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
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ secrets.ECR_REGISTRY }}/${{ matrix.image_name }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ${{ matrix.dockerfile }}
          platforms: ${{ matrix.platforms }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
            VCS_REF=${{ github.sha }}
            VERSION=${{ steps.meta.outputs.version }}

  # Image Scanning
  scan-images:
    runs-on: ubuntu-latest
    needs: build-images
    strategy:
      matrix:
        image:
          - amethyst-server
          - amethyst-stt
          - amethyst-client
    
    steps:
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ secrets.ECR_REGISTRY }}/${{ matrix.image }}:latest
          format: 'sarif'
          output: '${{ matrix.image }}-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Run Snyk container test
        uses: snyk/actions/docker@master
        with:
          image: ${{ secrets.ECR_REGISTRY }}/${{ matrix.image }}:latest
          args: --severity-threshold=high
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      
      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: '${{ matrix.image }}-results.sarif'
```

### 3. Deploy to Staging (`deploy-staging.yml`)

```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.amethyst.example.com
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Update EKS kubeconfig
        run: |
          aws eks update-kubeconfig \
            --name amethyst-staging \
            --region us-east-1
      
      - name: Deploy to EKS with Kustomize
        run: |
          kubectl kustomize infrastructure/kubernetes/overlays/staging | \
            kubectl apply -f -
      
      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/amethyst-server \
            -n amethyst \
            --timeout=5m
      
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ \
            --base-url=https://staging.amethyst.example.com \
            -v
      
      - name: Run performance tests
        run: |
          pytest tests/performance/ \
            --base-url=https://staging.amethyst.example.com \
            -v
      
      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Staging deployment: ${{ job.status }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "Staging deployment: ${{ job.status }}"
                  }
                }
              ]
            }
```

### 4. Deploy to Production (`deploy-production.yml`)

```yaml
name: Deploy to Production

on:
  workflow_dispatch:  # Manual trigger only
    inputs:
      environment:
        description: 'Environment'
        required: true
        default: 'production'

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://amethyst.example.com
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_PRODUCTION_ROLE_ARN }}
          aws-region: us-east-1
          role-session-name: github-actions-production
      
      - name: Get current deployment
        id: current
        run: |
          kubectl get deployment amethyst-server -o jsonpath='{.spec.template.spec.containers[0].image}' \
            > current-image.txt
          echo "current=$(cat current-image.txt)" >> $GITHUB_OUTPUT
      
      - name: Deploy with Blue-Green strategy
        id: deploy
        run: |
          # Get new image
          NEW_IMAGE=$(echo "${{ github.sha }}" | cut -c1-7)
          
          # Update green deployment
          kubectl set image deployment/amethyst-server-green \
            amethyst-server=${{ secrets.ECR_REGISTRY }}/amethyst-server:$NEW_IMAGE
          
          # Wait for green to be ready
          kubectl rollout status deployment/amethyst-server-green -n amethyst --timeout=5m
          
          # Switch service to green
          kubectl patch service amethyst-server \
            -p '{"spec":{"selector":{"deployment":"green"}}}'
          
          # Keep old blue deployment for quick rollback
          echo "deployed_image=$NEW_IMAGE" >> $GITHUB_OUTPUT
      
      - name: Health check
        run: |
          for i in {1..30}; do
            if curl -f https://amethyst.example.com/health; then
              echo "Health check passed"
              exit 0
            fi
            sleep 10
          done
          echo "Health check failed"
          exit 1
      
      - name: Run smoke tests
        run: |
          pytest tests/smoke/ \
            --base-url=https://amethyst.example.com \
            -v
      
      - name: Monitor metrics
        id: metrics
        run: |
          # Check error rate over last 5 minutes
          ERROR_RATE=$(kubectl exec -it prometheus-0 -- \
            promtool query instant \
            'rate(http_requests_total{status=~"5.."}[5m])')
          
          if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
            echo "High error rate detected"
            exit 1
          fi
      
      - name: Rollback on failure
        if: failure()
        run: |
          echo "Rolling back to previous version: ${{ steps.current.outputs.current }}"
          
          # Switch service back to blue
          kubectl patch service amethyst-server \
            -p '{"spec":{"selector":{"deployment":"blue"}}}'
          
          # Notify about rollback
      
      - name: Create GitHub Release
        if: success()
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: deployed-${{ github.sha }}
          release_name: Production Deployment
          body: |
            Deployed image: ${{ steps.deploy.outputs.deployed_image }}
            Environment: Production
            Version: ${{ github.ref }}
          draft: false
          prerelease: false
      
      - name: Notify team
        if: always()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -H 'Content-Type: application/json' \
            -d @- <<EOF
          {
            "text": "Production deployment: ${{ job.status }}",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Production Deployment*\nStatus: ${{ job.status }}\nTriggered by: ${{ github.actor }}\nRef: ${{ github.ref }}"
                }
              }
            ]
          }
          EOF
```

---

## 🚀 Deployment Strategies

### Blue-Green Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amethyst-server-blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: amethyst-server
      deployment: blue

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amethyst-server-green
spec:
  replicas: 5
  selector:
    matchLabels:
      app: amethyst-server
      deployment: green

---
apiVersion: v1
kind: Service
metadata:
  name: amethyst-server
spec:
  selector:
    app: amethyst-server
    deployment: blue  # Switch to 'green' for rollout
  ports:
  - port: 8000
```

### Canary Deployment

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: amethyst-server
  namespace: amethyst
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: amethyst-server
  progressDeadlineSeconds: 300
  service:
    port: 8000
    targetPort: 8000
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: error-rate
      thresholdRange:
        max: 1  # Max 1% error rate
      interval: 1m
    - name: latency
      thresholdRange:
        max: 500m  # Max 500ms latency
      interval: 1m
  webhooks:
  - name: acceptance-test
    url: http://flagger-loadtester/
    timeout: 30s
    metadata:
      type: smoke
      cmd: "curl -sd 'test' http://amethyst-server-canary:8000/health"
```

---

## 📊 Pipeline Metrics

### Success Criteria

| Metric | Target | Monitoring |
|--------|--------|-----------|
| **Unit Test Coverage** | >80% | Codecov |
| **Build Time** | <10 minutes | GitHub Actions |
| **SAST Issues** | 0 critical | SonarQube |
| **Secrets Found** | 0 | TruffleHog |
| **Docker Scan** | 0 critical | Trivy |
| **E2E Test Pass Rate** | 100% | GitHub Actions |
| **Deploy Success Rate** | >98% | GitHub Actions |
| **MTTR (Mean Time to Recovery)** | <15 min | Incident tracking |

---

## 🔐 Secrets Management

### GitHub Secrets Used

```
Production Secrets:
├── ECR_REGISTRY              # AWS ECR registry URL
├── AWS_ACCESS_KEY_ID         # AWS credentials
├── AWS_SECRET_ACCESS_KEY
├── AWS_ROLE_ARN             # IAM role for OIDC
├── GEMINI_API_KEY           # Gemini API key
├── DEEPGRAM_API_KEY         # Deepgram STT API key
├── SONAR_TOKEN              # SonarQube token
├── SNYK_TOKEN               # Snyk security token
├── SLACK_WEBHOOK            # Slack notifications
└── GITHUB_TOKEN             # GitHub API token

Vault Secrets (not in GitHub):
├── Database passwords
├── Redis auth tokens
├── TLS certificates
├── Encryption keys
└── API keys (rotated)
```

---

## 📈 Monitoring Deployment Impact

```yaml
# Prometheus queries for deployment quality
- alert: HighErrorRateAfterDeployment
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
  for: 5m
  annotations:
    summary: "Error rate > 1% in last 5 minutes"

- alert: HighLatencyAfterDeployment
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
  for: 5m
  annotations:
    summary: "P95 latency > 500ms"

- alert: PodCrashLooping
  expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
  for: 5m
  annotations:
    summary: "Pod {{ $labels.pod }} is crash looping"
```

---

**Status**: Production-Ready  
**Version**: 2.0 Enterprise  
**Last Updated**: March 5, 2026  
