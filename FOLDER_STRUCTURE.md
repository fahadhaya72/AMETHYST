# Enterprise Folder Structure - AMETHYST 2.0

This document defines the production-grade folder structure for AMETHYST, an AI Meeting Intelligence System at enterprise scale.

---

## 📁 Complete Directory Tree

```
amethyst/                                    # Project root
│
├── 📁 .github/
│   ├── workflows/
│   │   ├── ci.yml                         # Unit tests, linting, security scans
│   │   ├── build.yml                      # Docker build & push to ECR
│   │   ├── deploy-staging.yml             # Deploy to staging K8s cluster
│   │   ├── deploy-production.yml          # Deploy to production (manual approval)
│   │   └── security-scan.yml              # SAST, dependency scanning
│   │
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── feature_request.md
│       └── security_vulnerability.md
│
├── 📁 docs/
│   ├── ARCHITECTURE.md                    # System design & decisions
│   ├── API_SPEC.md                        # OpenAPI/gRPC specifications
│   ├── DATABASE_SCHEMA.md                 # PostgreSQL schema & migrations
│   ├── SECURITY_HARDENING.md              # Security checklist
│   ├── DEPLOYMENT_GUIDE.md                # Step-by-step deployment
│   ├── MONITORING_SETUP.md                # Observability stack config
│   ├── SCALING_PLAYBOOK.md                # How to scale components
│   ├── DISASTER_RECOVERY.md               # RTO/RPO procedures
│   ├── TROUBLESHOOTING.md                 # Common issues & solutions
│   │
│   ├── diagrams/
│   │   ├── system-architecture.drawio     # System overview (draw.io)
│   │   ├── data-flow.drawio                # Data flow (draw.io)
│   │   ├── deployment.drawio               # K8s deployment (draw.io)
│   │   ├── streaming-flow.png              # STT streaming sequence
│   │   └── authentication-flow.png         # Auth flow diagram
│   │
│   ├── api/
│   │   ├── openapi.yaml                   # OpenAPI 3.0 spec
│   │   ├── server.proto                   # gRPC protocol definitions
│   │   └── webhooks.md                    # Webhook events & formats
│   │
│   └── guides/
│       ├── getting-started.md              # Quick start guide
│       ├── development-setup.md            # Local development env
│       ├── testing-guide.md                # Testing strategy
│       └── release-process.md              # Release procedures
│
├── 📁 src/
│   │
│   ├── 📁 amethyst-client/                # PyQt6 Desktop Application
│   │   ├── main.py
│   │   │
│   │   ├── 📁 ui/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py             # Main PyQt6 window
│   │   │   ├── overlay.py                 # Transparent response overlay
│   │   │   ├── settings_dialog.py         # Settings/preferences
│   │   │   ├── tray_icon.py               # System tray integration
│   │   │   ├── styles.py                  # PyQt6 stylesheets (dark/light theme)
│   │   │   └── widgets/
│   │   │       ├── response_display.py    # Streaming response widget
│   │   │       ├── transcript_view.py     # Transcript history
│   │   │       ├── waveform.py            # Audio visualization
│   │   │       └── status_bar.py          # Status indicator
│   │   │
│   │   ├── 📁 audio/
│   │   │   ├── __init__.py
│   │   │   ├── capture.py                 # WASAPI loopback capture
│   │   │   ├── buffer.py                  # Circular audio buffer (streaming)
│   │   │   ├── vad.py                     # Voice Activity Detection (Silero)
│   │   │   ├── preprocessor.py            # MFCC, Mel-spectrogram extraction
│   │   │   └── device_manager.py          # Audio device detection
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── __init__.py
│   │   │   ├── api_client.py              # REST API client + WebSocket
│   │   │   ├── auth_manager.py            # OAuth2 + JWT token management
│   │   │   ├── session_manager.py         # User session handling
│   │   │   ├── config_manager.py          # Settings persistence
│   │   │   └── crash_handler.py           # Exception handling & reporting
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                  # Configuration defaults
│   │   │   ├── constants.py               # Application constants
│   │   │   ├── logger.py                  # Structured logging
│   │   │   └── version.py                 # Version info
│   │   │
│   │   ├── resources/
│   │   │   ├── icons/
│   │   │   │   ├── app_icon.png
│   │   │   │   ├── listening.png
│   │   │   │   ├── processing.png
│   │   │   │   └── error.png
│   │   │   │
│   │   │   ├── sounds/
│   │   │   │   ├── notification.wav
│   │   │   │   └── error.wav
│   │   │   │
│   │   │   └── styles/
│   │   │       ├── dark.qss             # PyQt stylesheet
│   │   │       └── light.qss
│   │   │
│   │   └── requirements-client.txt       # pip dependencies
│   │
│   ├── 📁 amethyst-relay/                # FastAPI Backend Services
│   │   ├── main.py                       # FastAPI app initialization
│   │   │
│   │   ├── 📁 api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py             # Main endpoints
│   │   │   │   ├── auth.py               # Auth endpoints
│   │   │   │   ├── health.py             # Health check endpoints
│   │   │   │   └── dependencies.py       # FastAPI dependencies
│   │   │   │
│   │   │   ├── v2/                       # Future API version
│   │   │   │   ├── __init__.py
│   │   │   │   └── routes.py
│   │   │   │
│   │   │   └── middleware/
│   │   │       ├── auth_middleware.py    # JWT validation
│   │   │       ├── logging_middleware.py # Request/response logging
│   │   │       ├── error_middleware.py   # Exception handling
│   │   │       ├── rate_limit_middleware.py
│   │   │       └── cors_middleware.py
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── __init__.py
│   │   │   ├── stt_service.py            # Streaming STT (Deepgram/Gladia)
│   │   │   ├── gemini_service.py         # Gemini API integration
│   │   │   ├── fallback_service.py       # OpenAI/Azure fallback
│   │   │   ├── context_service.py        # Conversation context (Redis)
│   │   │   ├── question_detector.py      # Question classification (ML)
│   │   │   ├── speaker_detector.py       # Speaker intent detection
│   │   │   ├── prompt_builder.py         # Dynamic prompt construction
│   │   │   ├── response_cache.py         # Redis-backed cache
│   │   │   └── feedback_service.py       # User feedback processing
│   │   │
│   │   ├── 📁 models/
│   │   │   ├── __init__.py
│   │   │   ├── request.py                # Pydantic request models
│   │   │   ├── response.py               # Pydantic response models
│   │   │   ├── database.py               # SQLAlchemy ORM models
│   │   │   └── schemas.py                # Database schemas
│   │   │
│   │   ├── 📁 repositories/
│   │   │   ├── __init__.py
│   │   │   ├── user_repo.py              # User data access
│   │   │   ├── transcript_repo.py        # Transcript storage
│   │   │   ├── feedback_repo.py          # Feedback storage
│   │   │   └── base_repo.py              # Base repository class
│   │   │
│   │   ├── 📁 config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py               # Configuration management
│   │   │   ├── logging_config.py         # Logging setup
│   │   │   └── database_config.py        # Database connection pool
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py                 # Structured JSON logging
│   │   │   ├── exceptions.py             # Custom exceptions
│   │   │   ├── security.py               # Security utilities
│   │   │   ├── validators.py             # Input validation
│   │   │   └── constants.py              # Constants
│   │   │
│   │   ├── 📁 utils/
│   │   │   ├── __init__.py
│   │   │   ├── cache_manager.py          # Redis cache utilities
│   │   │   ├── queue_manager.py          # Queue operations (RabbitMQ/SQS)
│   │   │   ├── stream_handler.py         # Streaming response handling
│   │   │   ├── validators.py             # Validation helpers
│   │   │   └── formatters.py             # Output formatting
│   │   │
│   │   ├── 📁 workers/
│   │   │   ├── __init__.py
│   │   │   ├── stt_worker.py             # Async STT processing
│   │   │   ├── response_worker.py        # Async response generation
│   │   │   ├── analytics_worker.py       # Analytics & feedback
│   │   │   └── cleanup_worker.py         # Maintenance & cleanup
│   │   │
│   │   └── requirements-server.txt       # pip dependencies
│   │
│   ├── 📁 services/                      # Microservices (modular deployment)
│   │   │
│   │   ├── 📁 question-detector/        # Standalone question detection ML service
│   │   │   ├── main.py
│   │   │   ├── model.py                  # BERT fine-tuned model
│   │   │   ├── Dockerfile
│   │   │   └── requirements.txt
│   │   │
│   │   ├── 📁 speaker-detector/         # Speaker diarization service
│   │   │   ├── main.py
│   │   │   ├── pyannote_handler.py
│   │   │   ├── Dockerfile
│   │   │   └── requirements.txt
│   │   │
│   │   ├── 📁 analytics/                # Analytics event processor
│   │   │   ├── main.py
│   │   │   ├── event_processor.py
│   │   │   ├── Dockerfile
│   │   │   └── requirements.txt
│   │   │
│   │   └── 📁 notification/             # WebSocket notification service
│   │       ├── main.py
│   │       ├── socket_handler.py
│   │       ├── Dockerfile
│   │       └── requirements.txt
│   │
│   └── 📁 shared/                        # Shared code between services
│       ├── __init__.py
│       ├── proto/                        # Protocol Buffers for gRPC
│       │   ├── common.proto
│       │   ├── stt.proto
│       │   ├── response.proto
│       │   └── build_protos.sh           # Compile proto files
│       │
│       ├── models/
│       │   ├── audio.py                  # Audio data structures
│       │   ├── transcript.py             # Transcription structures
│       │   └── response.py               # Response structures
│       │
│       ├── utils/
│       │   ├── logger.py                 # Logging utilities
│       │   ├── metrics.py                # Prometheus metrics
│       │   └── tracing.py                # Jaeger integration
│       │
│       └── constants/
│           ├── __init__.py
│           ├── audio_constants.py
│           ├── api_constants.py
│           └── config_constants.py
│
├── 📁 tests/
│   │
│   ├── 📁 unit/
│   │   ├── test_audio_buffer.py
│   │   ├── test_vad.py
│   │   ├── test_api_client.py
│   │   ├── test_stt_service.py
│   │   ├── test_response_generation.py
│   │   ├── test_context_service.py
│   │   ├── test_authentication.py
│   │   └── conftest.py                   # pytest fixtures
│   │
│   ├── 📁 integration/
│   │   ├── test_audio_to_response.py      # Full pipeline test
│   │   ├── test_api_endpoints.py
│   │   ├── test_database_operations.py
│   │   ├── test_redis_cache.py
│   │   └── conftest.py
│   │
│   ├── 📁 e2e/
│   │   ├── test_user_flow.py              # Complete user workflow
│   │   ├── test_video_call_integration.py # Zoom/Teams/Meet integration
│   │   └── fixtures/
│   │       ├── sample_audio.wav           # Test audio files
│   │       └── mock_responses.json
│   │
│   ├── 📁 performance/
│   │   ├── load_test.py                   # k6 load testing
│   │   ├── benchmark.py                   # Performance benchmarks
│   │   └── profiling/
│   │       ├── memory_profile.py
│   │       └── cpu_profile.py
│   │
│   └── 📁 security/
│       ├── test_authentication.py
│       ├── test_authorization.py
│       ├── test_encryption.py
│       ├── test_sql_injection.py
│       └── test_xss_prevention.py
│
├── 📁 infrastructure/
│   │
│   ├── 📁 docker/
│   │   ├── Dockerfile.client             # PyQt6 app container
│   │   ├── Dockerfile.server             # FastAPI app container
│   │   ├── Dockerfile.stt                # STT service container
│   │   ├── Dockerfile.response-gen       # Response generation service
│   │   ├── docker-compose.yml            # Local development
│   │   ├── docker-compose.staging.yml    # Staging environment
│   │   └── .dockerignore
│   │
│   ├── 📁 kubernetes/
│   │   ├── base/
│   │   │   ├── namespace.yaml
│   │   │   ├── configmap.yaml            # Non-secret config
│   │   │   ├── secrets.yaml              # Secret template (don't commit)
│   │   │   ├── pvc.yaml                  # Persistent volumes
│   │   │   ├── services.yaml             # K8s services
│   │   │   └── ingress.yaml              # Ingress controller
│   │   │
│   │   ├── deployments/
│   │   │   ├── api-gateway.yaml
│   │   │   ├── stt-service.yaml          # HPA enabled
│   │   │   ├── response-service.yaml     # HPA enabled
│   │   │   ├── context-service.yaml      # HPA enabled
│   │   │   ├── postgres-statefulset.yaml
│   │   │   └── redis-statefulset.yaml
│   │   │
│   │   ├── monitoring/
│   │   │   ├── prometheus-deployment.yaml
│   │   │   ├── grafana-deployment.yaml
│   │   │   ├── jaeger-deployment.yaml
│   │   │   ├── prometheus-service.yaml
│   │   │   └── grafana-service.yaml
│   │   │
│   │   ├── network-policy/
│   │   │   ├── allow-ingress.yaml        # Allow API gateway only
│   │   │   ├── deny-external.yaml        # Deny other external traffic
│   │   │   └── allow-internal.yaml       # Allow service-to-service
│   │   │
│   │   ├── rbac/
│   │   │   ├── service-accounts.yaml
│   │   │   ├── roles.yaml                # API reader, metrics reader
│   │   │   ├── role-bindings.yaml
│   │   │   └── cluster-roles.yaml
│   │   │
│   │   ├── storage/
│   │   │   ├── postgres-pvc.yaml
│   │   │   ├── redis-pvc.yaml
│   │   │   └── storage-class.yaml        # EBS/GCE persistent storage
│   │   │
│   │   └── overlays/
│   │       ├── dev/
│   │       │   └── kustomization.yaml    # Dev overrides (1 replica)
│   │       ├── staging/
│   │       │   └── kustomization.yaml    # Staging overrides (3 replicas)
│   │       └── production/
│   │           └── kustomization.yaml    # Prod overrides (10+ replicas)
│   │
│   ├── 📁 terraform/
│   │   ├── main.tf                       # Main infrastructure
│   │   ├── variables.tf                  # Input variables
│   │   ├── outputs.tf                    # Output values
│   │   ├── vpc.tf                        # VPC & networking
│   │   ├── rds.tf                        # RDS PostgreSQL
│   │   ├── elasticache.tf                # Redis cluster
│   │   ├── eks.tf                        # EKS cluster
│   │   ├── s3.tf                         # S3 buckets
│   │   ├── iam.tf                        # IAM roles
│   │   │
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   │   ├── terraform.tfvars      # Dev config
│   │   │   │   └── backend.tf
│   │   │   ├── staging/
│   │   │   │   ├── terraform.tfvars
│   │   │   │   └── backend.tf
│   │   │   └── production/
│   │   │       ├── terraform.tfvars
│   │   │       └── backend.tf
│   │   │
│   │   └── modules/
│   │       ├── networking/
│   │       ├── database/
│   │       ├── kubernetes/
│   │       ├── monitoring/
│   │       └── security/
│   │
│   ├── 📁 scripts/
│   │   ├── deploy.sh                     # Deployment script
│   │   ├── scale-up.sh                   # Manual scaling
│   │   ├── health-check.sh               # Health verification
│   │   ├── backup-database.sh            # Database backup
│   │   ├── restore-database.sh           # Database restore
│   │   ├── db-migration.sh               # Database migrations
│   │   └── cleanup.sh                    # Cleanup resources
│   │
│   └── 📁 monitoring/
│       ├── prometheus.yml                # Prometheus config
│       ├── grafana-dashboards/
│       │   ├── system-health.json
│       │   ├── stt-performance.json
│       │   ├── api-metrics.json
│       │   ├── database-metrics.json
│       │   └── business-metrics.json
│       │
│       ├── alerting-rules.yml            # AlertManager rules
│       └── jaeger-config.yml             # Jaeger tracing config
│
├── 📁 config/
│   ├── .env.template                    # Environment template
│   ├── .env.development                 # Dev environment (DON'T COMMIT)
│   ├── .env.staging                     # Staging (use Vault)
│   ├── .env.production                  # Prod (use Vault)
│   ├── logging-config.yml               # Logging configuration
│   ├── feature-flags.yml                # Feature flag definitions
│   └── secrets.enc                      # Encrypted secrets (Vault)
│
├── 📁 scripts/
│   ├── setup-dev.sh                     # Dev environment setup
│   ├── setup-db.sh                      # Database initialization
│   ├── run-tests.sh                     # Test runner
│   ├── run-linting.sh                   # Code quality checks
│   ├── generate-docs.sh                 # Generate API documentation
│   └── migration.py                     # Database migration tool
│
├── 📁 migrations/
│   ├── versions/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_transcripts.sql
│   │   ├── 003_add_feedback.sql
│   │   ├── 004_add_indices.sql
│   │   └── 005_add_audit_table.sql
│   │
│   └── init.sql                         # Initial schema
│
├── .gitignore                            # Git ignore rules
├── .gitattributes                        # Git attributes
├── .env.example                          # Environment example
├── Makefile                              # Build automation
├── setup.py                              # Python package setup
├── pyproject.toml                        # Python project metadata
├── poetry.lock                           # Dependency lock file
├── requirements-dev.txt                  # Development dependencies
├── requirements-test.txt                 # Testing dependencies
│
├── README.md                             # Project overview
├── PRODUCTION_ARCHITECTURE.md            # This architecture doc
├── FOLDER_STRUCTURE.md                   # This file
├── CONTRIBUTING.md                       # Contribution guidelines
├── CODE_OF_CONDUCT.md                    # Community guidelines
├── LICENSE                               # MIT or Apache 2.0
│
└── CHANGELOG.md                          # Release history
```

---

## 📊 Module Descriptions

### Client-Side Modules (PyQt6)

| Module | Purpose | Components |
|--------|---------|------------|
| `ui/` | User interface | Main window, overlay, settings, widgets |
| `audio/` | Audio capture | WASAPI loopback, VAD, buffering |
| `services/` | API communication | REST/WebSocket client, auth, session |
| `core/` | Configuration | Settings, logging, constants |

### Server-Side Modules (FastAPI)

| Module | Purpose | Components |
|--------|---------|------------|
| `api/` | API endpoints | Routes, auth, versioning |
| `services/` | Business logic | STT, Gemini, context, cache |
| `models/` | Data structures | Request/response models, ORM |
| `repositories/` | Data access | Database operations |
| `workers/` | Background jobs | Async tasks, queue processing |

### Microservices (Optional Modular Deployment)

| Service | Purpose | Can Scale Independently |
|---------|---------|------------------------|
| `question-detector/` | ML question classification | Yes (via queue) |
| `speaker-detector/` | Speaker diarization | Yes (via queue) |
| `analytics/` | Event processing | Yes (Kafka consumer) |
| `notification/` | WebSocket broadcast | Yes (pub/sub) |

### Infrastructure

| Component | Purpose | Technology |
|-----------|---------|------------|
| `docker/` | Containerization | Docker, docker-compose |
| `kubernetes/` | Orchestration | K8s manifests, Kustomize |
| `terraform/` | IaC | AWS resources |
| `scripts/` | Automation | Bash, Python |
| `monitoring/` | Observability | Prometheus, Grafana, Jaeger |

---

## 🔄 Development Workflow

```
Local Development
    ├─→ Branch: feature/xxx
    ├─→ Code changes
    ├─→ Run tests locally: make test
    ├─→ Lint: make lint
    │
    └─→ Commit & Push
            │
            └─→ GitHub Actions CI
                    ├─→ Unit tests
                    ├─→ Integration tests
                    ├─→ Security scan
                    ├─→ Build Docker image
                    │
                    └─→ Deploy to Staging
                            ├─→ E2E tests
                            ├─→ Performance tests
                            │
                            └─→ Ready for Production? (manual review)
                                    │
                                    └─→ Deploy to Production
                                        ├─→ Blue-green deployment
                                        ├─→ Canary rollout (5% → 100%)
                                        └─→ Monitor metrics
```

---

## 📦 Dependency Management

- **Python**: `poetry.lock` + `requirements-*.txt`
- **Docker images**: Public registries (Python, Redis, Postgres)
- **Kubernetes**: Helm charts for databases (Bitnami)
- **Terraform**: Provider versions locked in `providers.tf`
- **Node modules**: None (pure Python backend & PyQt6 client)

---

## 🔐 Secrets Management

```
Directory Structure for Secrets:
/
├── .env                    # Local development (NOT committed)
├── .env.template           # Template for documentation
│
├── kubernetes/
│   └── secrets.yaml       # K8s secret manifest (encrypted)
│
├── terraform/
│   └── main.tf            # References AWS Secrets Manager
│
└── infrastructure/
    └── vault-config/      # HashiCorp Vault configuration
        ├── kv-engine.hcl
        └── policies/
            ├── client.hcl
            ├── server.hcl
            └── admin.hcl
```

**Important**: All sensitive data stored in HashiCorp Vault in production, not in environment variables.

---

## 📈 File Size Guidelines

| Component | Target Size |
|-----------|-------------|
| Docker image (client) | <500MB |
| Docker image (server) | <300MB |
| Single Python file | <500 lines (refactor if larger) |
| Database per table | <10GB (partition if larger) |
| Redis memory | <80% utilization |

---

## 🎯 Key Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Scalability**: Stateless services that scale horizontally
3. **Testability**: Unit, integration, and E2E test coverage
4. **Observability**: Extensive logging, metrics, and tracing
5. **Security**: Defense in depth, encrypt everything
6. **Maintainability**: Clear structure, documented code
7. **Automation**: CI/CD, infrastructure as code
8. **Reliability**: Redundancy, failover, disaster recovery

---

**Version**: 2.0 Enterprise  
**Last Updated**: March 5, 2026  
**Maintainer**: Architecture Team  
