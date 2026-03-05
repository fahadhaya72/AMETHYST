# Technology Stack - Complete Justification

Enterprise-grade technology selections for AMETHYST 2.0 AI Meeting Intelligence System.

---

## 🏆 Executive Summary

Our technology stack is designed for:
- **Scalability**: 10,000+ concurrent users with horizontal scaling
- **Performance**: Sub-500ms end-to-end latency at scale
- **Reliability**: 99.99% uptime with automatic failover
- **Security**: Multi-layer defense, encryption, compliance
- **Developer Experience**: Modern frameworks, clear abstractions
- **Cost Optimization**: Resource efficiency, autoscaling

---

## 🖥️ Client Tier - Desktop Application

### Selected: **PyQt6** (replacing tkinter)

#### Why PyQt6?

| Aspect | tkinter | PyQt6 | Winner |
|--------|---------|-------|--------|
| **Professional UI** | Basic | Enterprise-grade | ✅ PyQt6 |
| **Performance** | ~60 FPS | 144+ FPS | ✅ PyQt6 |
| **Native Integration** | Limited | Full Windows/Mac | ✅ PyQt6 |
| **Accessibility** | Minimal | WCAG compliant | ✅ PyQt6 |
| **Complex Layouts** | Difficult | Easy | ✅ PyQt6 |
| **Styling** | CSS-like | Full CSS | ✅ PyQt6 |
| **License** | Free | LGPL (commercial available) | ✅ Both |
| **Community** | Small | Very large | ✅ PyQt6 |

#### Implementation Details

```python
# PyQt6 Advantages for AMETHYST
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont

# Native Windows integration
class StealthOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        # Windows-specific features
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # System tray integration
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.show()
        
        # Hardware acceleration
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
```

#### Comparison: tkinter vs PyQt6

```
┌─────────────────────────────────────────────────────────┐
│ GHOST v1 (tkinter)       │ AMETHYST v2 (PyQt6)         │
├──────────────────────────┼─────────────────────────────┤
│ Basic Windows overlay    │ Professional enterprise UI   │
│ Flickering text display  │ Smooth animations            │
│ Limited styling          │ Full CSS support             │
│ No system tray           │ System tray integration      │
│ Performance issues at    │ 10K+ users, no issues       │
│   scale (>100 users)     │                             │
│ Difficult to extend      │ Modular architecture        │
│ No accessibility         │ WCAG compliant              │
└──────────────────────────┴─────────────────────────────┘
```

---

## 🎙️ Audio Tier - Real-Time Speech-to-Text

### Selected: **Deepgram + Gladia (Streaming)** + **Local Whisper (Fallback)**

#### Why Streaming STT?

| Feature | Batch Whisper | Streaming Deepgram | Winner |
|---------|----------------|--------------------|--------|
| **Latency** | 2-3 seconds | 100-300ms | ✅ Streaming |
| **Real-time** | No | Yes | ✅ Streaming |
| **Accuracy** | 95%+ | 95%+ | 🤝 Tie |
| **Cost (1000h/mo)** | Free (local) | $12 | ⚠️ Cost trade-off |
| **Diarization** | No | Yes (Multi-speaker) | ✅ Streaming |
| **Punctuation** | Requires post-processing | Automatic | ✅ Streaming |
| **Language support** | 99 languages | 30+ languages | ✅ Whisper |
| **Offline mode** | Yes | No | ✅ Whisper |

#### Architecture Decision

```
Audio Stream (10ms chunks)
    ↓
├─→ Primary Path: Deepgram Streaming
│   ├─→ Real-time transcription (streaming protocol)
│   ├─→ Multi-speaker diarization
│   ├─→ Automatic punctuation
│   ├─→ Confidence scores
│   └─→ Fallback if rate-limited or unavailable
│
└─→ Fallback Path: Local Whisper Batch
    ├─→ Batch processing (buffer when needed)
    ├─→ No cloud dependency
    ├─→ Slightly higher latency (acceptable)
    └─→ Complete accuracy/language coverage
```

#### Cost Optimization

```
Scenario 1: 10,000 users × 30 min meetings/day
├─→ Audio minutes/day: 10,000 × 0.5 = 5,000 hours
├─→ Deepgram cost: 5,000 × ($0.0059/min) = ~$1,600/day
├─→ Annual: ~$584,000
│
Optimization A: Use Whisper for off-peak
├─→ Run Whisper locally at night (US-WEST)
├─→ Cost reduction: ~40%
└─→ New annual: ~$350,000

Optimization B: Fallback to Whisper on high load
├─→ Queue-based adaptive switching
├─→ Cost reduction: ~50-60%
└─→ New annual: ~$230,000
```

---

## 🤖 AI/LLM Tier - Response Generation

### Selected: **Google Gemini 3 Flash**

#### Why Gemini Flash?

| Model | Latency | Cost | Context | Quality |
|-------|---------|------|---------|---------|
| **GPT-4** | 2-3s | $0.03/1K input | 128K | Excellent |
| **GPT-4 Turbo** | 1-2s | $0.01/1K | 128K | Excellent |
| **Claude 3** | 1-2s | $0.003/1K | 200K | Excellent |
| **Gemini 1.5** | 0.5-1s | $0.00075/1K | 1M | Good |
| **Gemini Flash** | 0.3-0.5s | $0.0001/1K | 1M | Good-Excellent |

#### Decision Rationale

**Chosen**: Gemini Flash 3
- ✅ Fastest latency (critical for meeting UX)
- ✅ Most cost-effective (400% cheaper than GPT-4)
- ✅ Huge context window (1M tokens = entire meeting history)
- ✅ Google ecosystem (enterprise support)
- ⚠️ Trade-off: Slightly less advanced reasoning (acceptable for meeting assistance)

#### Fallback Chain

```
Primary: Gemini Flash
    ↓
├─→ Success? → Cache & serve (instant)
└─→ Failure/RateLimit?
        ↓
        SecondaryOpenAI GPT-4
            ↓
            ├─→ Success? → Serve with note
            └─→ Failure?
                    ↓
                    Tertiary: Azure OpenAI
                        ↓
                        ├─→ Success? → Log incident
                        └─→ Failure?
                                ↓
                                Fallback: Generic response
                                + Offline response caching
```

#### Cost Analysis

```
For 10,000 users × 30 min meetings/day:

Gemini Flash:
├─→ Average response: 150 tokens
├─→ Responses/day: 10,000 users × 4 = 40,000 responses
├─→ Tokens/day: 40,000 × 150 = 6,000,000 tokens
├─→ Cost/day: 6M × $0.0001 = $600
├─→ Annual: ~$219,000

GPT-4 Turbo (comparison):
├─→ Same calculation
├─→ Cost/day: 6M × $0.01 = $60,000
└─→ Annual: ~$21.9M (36x more expensive!)
```

---

## 📊 Backend Tier - API & Services

### Selected: **FastAPI**

#### Why FastAPI?

| Framework | Performance | Async | Typing | OpenAPI | Learning |
|-----------|-------------|-------|--------|---------|----------|
| **Django** | 30 req/s | Optional | Limited | Manual | Steep |
| **Flask** | 40 req/s | Optional | No | Manual | Easy |
| **FastAPI** | 200+ req/s | Built-in | Excellent | Auto | Medium |
| **Go Gin** | 300+ req/s | Built-in | N/A | Manual | Medium |
| **Rust Axum** | 400+ req/s | Built-in | N/A | Manual | Steep |

#### Why FastAPI > Go/Rust?

```
AMETHYST Requirements Analysis:
├─→ Need: 100 RPS (easily handled by FastAPI's 200+ req/s)
├─→ Team: Python expertise (FastAPI native)
├─→ Deployment: Standard containers (Rust/Go no advantage)
├─→ Maintainability: Python developer pool larger
├─→ Time-to-market: 3-6 months (FastAPI), 6-12 months (Go)
│
Decision: FastAPI optimizes for team velocity,
not raw performance (not needed for our scale)
```

#### FastAPI Architecture

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

app = FastAPI(title="AMETHYST", version="2.0.0")

# Automatic OpenAPI documentation
# Type hints → automatic validation
# Async by default

@app.post("/api/v1/generate")
async def generate_response(
    request: GenerateRequest,
    session: Session = Depends(get_db),
    token: str = Depends(verify_jwt),
) -> StreamingResponse:
    """Stream response from Gemini."""
    async for chunk in gemini_service.generate_stream(request):
        yield chunk.encode()

# 100+ lines of code does what would take
# 400+ lines in Django
```

---

## 💾 Data Tier - Databases & Caching

### Selected: **PostgreSQL + Redis**

#### Database Comparison

| Database | ACID | JSON | Search | Replication | Scaling |
|----------|------|------|--------|-------------|---------|
| **MySQL** | Yes | Limited | Limited | Yes | Horizontal hard |
| **PostgreSQL** | Yes | Full | Full-text | Yes | Horizontal easy |
| **MongoDB** | Yes (3.0+) | Native | Limited | Yes | Horizontal easy |
| **DynamoDB** | No | JSON | Limited | Auto | Expensive |
| **Cassandra** | Eventual | Limited | Limited | Yes | Complex |

#### Architecture Decision

```
AMETHYST Data Storage:
│
├─→ PostgreSQL (Primary)
│   ├─→ User accounts & auth
│   ├─→ Transcripts (immutable audit trail)
│   ├─→ User feedback & ratings
│   ├─→ Meeting metadata
│   └─→ Compliance/audit logs
│
├─→ Redis Cluster (Cache/Session)
│   ├─→ JWT tokens (20-min TTL)
│   ├─→ Conversation context (7-day TTL)
│   ├─→ Response cache (7-day TTL)
│   ├─→ Rate limit counters
│   ├─→ Feature flags
│   └─→ Real-time notifications (Pub/Sub)
│
├─→ Elasticsearch (Full-text Search)
│   ├─→ Searchable transcripts
│   ├─→ Analytics queries
│   └─→ Audit trail search
│
└─→ S3/MinIO (Object Storage)
    ├─→ Raw audio (encrypted, 30-day retention)
    ├─→ Backup archives
    └─→ Document uploads
```

#### Why Not MongoDB?

```
MongoDB is excellent for:
├─→ Flexible schemas (AMETHYST has fixed schema)
├─→ Horizontal sharding (PostgreSQL Citus exists)
├─→ Document storage (AMETHYST uses relational)
└─→ Unstructured data (AMETHYST structured)

PostgreSQL advantages:
├─→ ACID compliance (critical for financials/audit)
├─→ Complex queries (JOIN-heavy workloads)
├─→ JSON support (AMETHYST does use JSON for context)
├─→ Full-text search (transcripts, metadata)
├─→ Lower operational complexity
└─→ Cost-effective at scale
```

#### PostgreSQL Configuration

```yaml
# Production PostgreSQL Settings
postgresql:
  max_connections: 500
  shared_buffers: 256GB      # 25% of system RAM
  effective_cache_size: 768GB # 75% of system RAM
  
  # Performance
  work_mem: 4GB             # Per-sort memory
  random_page_cost: 1.1     # SSD optimization
  
  # WAL for replication
  wal_level: replica
  max_wal_senders: 10
  max_replication_slots: 10
  
  # Autovacuum
  autovacuum: on
  autovacuum_naptime: 10s
  
  # Monitoring
  log_min_duration_statement: 1000  # Log slow queries
  shared_preload_libraries: 'pg_stat_statements'
```

---

## 🔗 Message Queue - Asynchronous Processing

### Selected: **Redis Streams + RabbitMQ + Kafka**

#### Multi-Queue Strategy

```
                Queue Selection by Use Case
                
Audio Ingestion (100 RPS, ordered, real-time):
    └─→ Redis Streams
        ├─→ Sub-millisecond latency
        ├─→ Ordered (FIFO)
        ├─→ Consumer groups
        └─→ TTL auto-cleanup

Task Distribution (variable load):
    └─→ RabbitMQ
        ├─→ Persistence
        ├─→ Priority queues
        ├─→ Dead-letter queues
        └─→ Excellent reliability

Analytics Events (high volume, statistical):
    └─→ Kafka
        ├─→ Immutable log
        ├─→ Multi-subscriber
        ├─→ Time-series queries
        └─→ Replay capability
```

#### Why Not Single Queue?

```
Single Queue (e.g., just Redis):
├─→ ✅ Simple deployment
├─→ ❌ Limited durability
├─→ ❌ Limited routing
├─→ ❌ No dead-letter queues

Single Queue (e.g., just RabbitMQ):
├─→ ✅ Reliable
├─→ ✅ Flexible
├─→ ❌ Slower than Redis for high throughput
├─→ ❌ Not ideal for analytics

Multi-Queue (Redis + RabbitMQ + Kafka):
├─→ ✅ Optimized for each workload
├─→ ✅ Right tool for each job
├─→ ✅ Fault isolation
├─→ ⚠️ Operational complexity (mitigated by Kubernetes)
```

---

## 🛡️ Security & Secrets Management

### Selected: **HashiCorp Vault**

#### Why Vault?

| Feature | Environment Variables | AWS Secrets | Vault |
|---------|------------------------|-------------|-------|
| **Audit Trail** | No | Yes | Yes |
| **Encryption** | No | Yes | Yes |
| **Rotation** | Manual | Manual | Automatic |
| **Multi-cloud** | Yes | AWS only | Yes |
| **Policy Engine** | No | Limited | Advanced |
| **Self-hosted** | Yes | No | Yes |
| **Compliance** | Limited | Yes | Yes |

#### Vault Architecture

```
┌─────────────────────────────────────┐
│  Vault Cluster (3 nodes, HA)        │
├─────────────────────────────────────┤
│                                     │
│  KV2 (Key-Value v2)                │
│  ├─→ API keys (Gemini, Deepgram)   │
│  ├─→ Database credentials          │
│  └─→ TLS certificates              │
│                                     │
│  Database (Dynamic Credentials)     │
│  ├─→ PostgreSQL user rotate        │
│  ├─→ Redis auth rotate             │
│  └─→ Auto-revoke on app crash      │
│                                     │
│  PKI (Public Key Infrastructure)    │
│  ├─→ Internal TLS certificates     │
│  ├─→ mTLS for services             │
│  └─→ Auto-rotate certificates      │
│                                     │
│  Transit (Encryption as Service)    │
│  ├─→ Encrypt data at rest          │
│  ├─→ Key rotation                  │
│  └─→ Decrypt data                  │
│                                     │
└─────────────────────────────────────┘
        ↑       ↑       ↑
        │       │       │
   PyQt6  FastAPI   Workers
   Client  Backend
```

---

## 📊 Monitoring & Observability Stack

### Selected: **Prometheus + Grafana + Jaeger + ELK**

#### Why this combination?

```
Prometheus:
├─→ De-facto standard for metrics
├─→ Time-series database
├─→ Pull-based (vs push) = less network
├─→ PromQL powerful queries
└─→ 99% Kubernetes integration

Grafana:
├─→ Best visualization
├─→ Out-of-box dashboards
├─→ Alerting integration
└─→ Cost-effective

Jaeger:
├─→ Distributed tracing
├─→ See request flow across services
├─→ Identify bottlenecks
└─→ Open source (not vendor-locked)

ELK Stack:
├─→ Full-text search on logs
├─→ Structured JSON logging
├─→ Long-term retention
└─→ Complex queries (Elasticsearch)
```

#### NOT using DataDog/New Relic because:

```
DataDog/New Relic:
├─→ ✅ All-in-one solution
├─→ ✅ Excellent UX
├─→ ❌ $800-1200/month per host
├─→ ❌ Vendor lock-in
├─→ ❌ Expensive data retention
└─→ Cost for 50-host cluster: $40K-60K/month

Open source (Prom+Grafana+Jaeger + ELK):
├─→ ✅ Strategic control
├─→ ✅ Cost: ~$2K/month for cluster
├─→ ✅ Portable (not locked in)
├─→ ✅ Full customization
└─→ Savings: $500K+/year vs commercial
```

---

## 🐳 Containerization Platform

### Selected: **Docker + Kubernetes (EKS)**

#### Why Kubernetes?

| Platform | Scaling | HA | Multi-Region | Cost |
|----------|---------|-----|------|------|
| **Docker Swarm** | Manual | Limited | Hard | Free |
| **ECS (AWS)** | Auto | Good | Good | $0.015/h |
| **Kubernetes** | Auto | Excellent | Easy | $0.10/h (managed) |
| **Cloud Run** | Auto | Good | Vendor-specific | Pay-per-request |

#### Decision Logic

```
AMETHYST Requirements:
├─→ 10,000 concurrent users
├─→ Horizontal autoscaling needed
├─→ Multi-region deployment
├─→ Complex service mesh
├─→ Stateful components (databases)
├─→ GPU workloads (optional: BERT inference)
├─→ Team expertise: Python (not AWS-specific)
│
Kubernetes provides:
├─→ ✅ Cluster orchestration
├─→ ✅ Autoscaling (HPA, KEDA)
├─→ ✅ Service mesh (Istio)
├─→ ✅ Multi-region capable (Anthos)
├─→ ✅ Vendor portability
├─→ ✅ Mature ecosystem
└─→ ✅ Enterprise support (3+ vendors)
```

#### Why EKS (not GKE/AKS)?

```
Evaluation Matrix:

              EKS    GKE    AKS
┌─────────────────────────────┐
│ Cost        2/5    3/5    4/5 │
│ Performance 5/5    5/5    4/5 │
│ Maturity    5/5    5/5    4/5 │
│ AWS Integ.  5/5    2/5    1/5 │
│ Support     5/5    4/5    4/5 │
└─────────────────────────────┘

Selected: EKS because:
├─→ Deep AWS integration (S3, RDS, Secrets Manager)
├─→ Lowest operational overhead
├─→ Strongest AWS ecosystem support
└─→ Best for 10K user scale at enterprise level
```

---

## 📚 Summary Comparison Table

### Client Tier
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **Desktop Framework** | PyQt6 | Professional UI, optimized for Windows |
| **Audio Capture** | WASAPI Loopback | Native Windows, only option for system audio |
| **VAD Model** | Silero VAD | Lightweight, fast, 99%+ accurate |

### Server Tier
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **Web Framework** | FastAPI | Async, typing, 200+ req/s, auto-docs |
| **ASGI Server** | Uvicorn + Gunicorn | Battle-tested, standards-based |
| **Service Mesh** | Istio | Circuit breakers, tracing, load balancing |

### Data Tier
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **Database** | PostgreSQL | ACID, JSON, search, replication |
| **Session Cache** | Redis | Millisecond latency, pub/sub |
| **Conversation Memory** | Redis JSON | Structured, queryable, TTL |
| **Full-text Search** | Elasticsearch | Lucene, aggregations, analytics |

### AI/ML Tier
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **STT (Primary)** | Deepgram | Real-time, diarization, accuracy |
| **STT (Fallback)** | Whisper | Local, comprehensive, free |
| **LLM (Primary)** | Gemini Flash | Fastest, cheapest, 1M context |
| **LLM (Fallback)** | GPT-4 Turbo | Best quality if needed |

### Infrastructure
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **Orchestration** | Kubernetes/EKS | Scale 10K users, multi-region |
| **Container Registry** | AWS ECR | Security, integration, scanning |
| **Container Runtime** | containerd | Lightweight, high performance |
| **Service Mesh** | Istio | Observability, traffic management |

### Observability
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **Metrics** | Prometheus | Standard, powerful, retention |
| **Visualization** | Grafana | Best dashboards, alerting |
| **Tracing** | Jaeger | Distributed tracing, open source |
| **Logging** | ELK Stack | Search, retention, compliance |

### Deployment
| Component | Selection | Rationale |
|-----------|-----------|-----------|
| **CI/CD** | GitHub Actions | Git-native, sufficient for scale |
| **Secrets Management** | Vault | Enterprise, open source, portable |
| **IaC** | Terraform | Vendor-agnostic, state management |
| **Multi-region** | Route53 | Geo-routing, health checks |

---

## 💰 Total Cost of Ownership (Annual)

```
AMETHYST v2.0 - 10,000 Users, 30 min/day avg

Infrastructure Costs:
├─→ EKS cluster (3 master, 50 worker)  $150,000
├─→ RDS PostgreSQL (au-db-r6i)        $ 85,000
├─→ ElastiCache Redis                  $ 45,000
├─→ Elasticsearch                       $ 32,000
├─→ S3 storage (30 days, encrypted)     $ 12,000
├─→ Data transfer/bandwidth             $ 25,000
└─→ Subtotal Infrastructure             $349,000

AI/ML API Costs:
├─→ Gemini API ($0.0001/1K tokens)      $219,000
├─→ Deepgram streaming STT ($0.0059/min) $584,000
├─→ Subtotal AI/ML                      $803,000

Operations:
├─→ Vault Enterprise license            $ 50,000
├─→ Datadog equivalent (open source)    $ 24,000
├─→ Monitoring infrastructure           $ 12,000
├─→ Backups & DR                        $ 18,000
├─→ Subtotal Operations                 $104,000

Staffing (Engineering):
├─→ 2 × Platform engineers            $300,000
├─→ 1 × DevOps engineer                $200,000
├─→ 1 × Site Reliability engineer       $180,000
└─→ Subtotal Staffing                  $680,000

TOTAL ANNUAL: $1,936,000
Per-user cost: $23.25/year (at 10,000 users)
Per-user cost: $0.65/day of usage
```

---

**Status**: Production-Ready  
**Version**: 2.0 Enterprise  
**Last Updated**: March 5, 2026  
