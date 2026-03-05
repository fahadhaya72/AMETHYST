# System Architecture Diagrams

Complete visual representations of the AMETHYST production architecture.

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph client["CLIENT TIER"]
        pyqt["PyQt6 Desktop App"]
        overlay["Transparent Overlay UI"]
        audio["WASAPI Audio Capture"]
    end
    
    subgraph network["NETWORK LAYER"]
        lb["Load Balancer"]
        apigw["API Gateway"]
        mesh["Service Mesh"]
    end
    
    subgraph api["API SERVICES"]
        auth["Auth Service"]
        stt["STT Service"]
        resp["Response Service"]
        ctx["Context Service"]
    end
    
    subgraph queue["MESSAGE QUEUE"]
        redis_q["Redis Streams"]
        rmq["RabbitMQ"]
        kafka["Kafka"]
    end
    
    subgraph data["DATA TIER"]
        pg["PostgreSQL"]
        redis["Redis Cache"]
        es["Elasticsearch"]
        s3["S3 Storage"]
    end
    
    subgraph external["EXTERNAL APIs"]
        gemini["Gemini Flash API"]
        deepgram["Deepgram STT"]
    end
    
    subgraph observability["MONITORING"]
        prom["Prometheus"]
        graf["Grafana"]
        jaeger["Jaeger Tracing"]
    end
    
    client -->|mTLS + JWT| lb
    lb --> apigw
    apigw --> mesh
    
    mesh --> auth
    mesh --> stt
    mesh --> resp
    mesh --> ctx
    
    stt --> redis_q
    resp --> rmq
    auth --> redis
    ctx --> redis
    
    auth --> pg
    resp --> pg
    ctx --> redis
    
    stt --> deepgram
    resp --> gemini
    
    stt, resp, auth, ctx -.->|metrics| prom
    prom --> graf
    prom --> jaeger
    
    style client fill:#e1f5ff
    style api fill:#c8e6c9
    style data fill:#fff9c4
    style external fill:#f8bbd0
    style observability fill:#e0bee7
```

---

## 2. Data Flow - Audio to Response

```mermaid
sequenceDiagram
    participant Client as PyQt6 Client
    participant Buffer as Audio Buffer
    participant VAD as Voice Activity Detect
    participant Queue as Redis Queue
    participant STT as STT Service
    participant Detect as Question Detector
    participant CTX as Context Service
    participant Gen as Response Generator
    participant Gemini as Gemini API
    participant Display as Overlay Display

    Client->>Buffer: Capture audio chunks (10ms)
    Buffer->>VAD: Check voice activity
    alt Voice detected
        VAD->>Queue: Batch 10 chunks (~100ms)
        Queue->>STT: Dequeue audio
        STT->>STT: Stream to Deepgram
        STT->>Detect: "Can you explain X?"
        
        Detect->>Detect: Classify: Question? Directed at me?
        Detect->>CTX: Get conversation context
        CTX->>CTX: Retrieve from Redis
        
        CTX->>Gen: Context + Question
        Gen->>Gen: Build prompt with system context
        Gen->>Gemini: Stream generation request
        Gemini->>Gen: Stream response chunks
        
        Gen->>Queue: Push to WebSocket queue
        Gen->>Display: Stream via WebSocket
        Display->>Client: Render in overlay
        Display->>Client: Text appears character-by-character
    else No voice
        VAD->>VAD: Discard silence
    end
```

---

## 3. Authentication & Authorization Flow

```mermaid
graph LR
    subgraph auth_flow["Authentication Flow"]
        client["Desktop Client"]
        oauth["OAuth2 Provider"]
        authsvc["Auth Service"]
        tokendb["Token Cache\nRedis"]
        api["Protected API"]
    end
    
    client -->|1. Request login| oauth
    oauth -->|2. Authorization Code| client
    client -->|3. Exchange code| authsvc
    authsvc -->|4. Validate + Create JWT| authsvc
    authsvc -->|5. Access token + Refresh token| client
    authsvc -->|6. Cache in Redis| tokendb
    
    client -->|7. API call + JWT| api
    api -->|8. Verify JWT| authsvc
    authsvc -->|9. Check in Redis cache| tokendb
    tokendb -->|10. Valid?| api
    api -->|11. Response| client
    
    style auth_flow fill:#e3f2fd
```

---

## 4. Scaling Architecture (10K Users)

```mermaid
graph TB
    subgraph load_dist["Load Distribution"]
        users["10,000 Users"]
        geolb["GeoDNS Router"]
    end
    
    subgraph region1["US-EAST (Primary)"]
        lb1["Load Balancer"]
        stt1["STT Service x20"]
        resp1["Response Service x10"]
        ctx1["Context Service x5"]
        pg1["PostgreSQL Primary"]
        redis1["Redis Cluster 9-node"]
    end
    
    subgraph region2["US-WEST (Secondary)"]
        lb2["Load Balancer"]
        stt2["STT Service x10"]
        resp2["Response Service x5"]
        ctx2["Context Service x3"]
        pg2["PostgreSQL Replica"]
        redis2["Redis Replica"]
    end
    
    subgraph region3["EU-WEST (GDPR)"]
        lb3["Load Balancer"]
        stt3["STT Service x5"]
        pg3["PostgreSQL GDPR"]
    end
    
    users --> geolb
    geolb -->|60% users| lb1
    geolb -->|20% users| lb2
    geolb -->|20% users| lb3
    
    lb1 --> stt1
    lb1 --> resp1
    lb1 --> ctx1
    stt1 --> redis1
    resp1 --> pg1
    ctx1 --> redis1
    
    lb2 --> stt2
    lb2 --> resp2
    ctx2 --> redis2
    
    lb3 --> stt3
    
    pg1 -.->|async repl| pg2
    pg1 -.->|GDPR repl| pg3
    redis1 -.->|cluster repl| redis2
    
    style region1 fill:#c8e6c9
    style region2 fill:#fff9c4
    style region3 fill:#ffccbc
```

---

## 5. Microservices Communication

```mermaid
graph TB
    subgraph client["Client"]
        pyqt["PyQt6 App"]
    end
    
    subgraph mesh["Service Mesh"]
        istio["Istio/Consul"]
    end
    
    subgraph services["Microservices"]
        auth["Auth Service\nPort: 8001"]
        stt["STT Service\nPort: 8002"]
        resp["Response Service\nPort: 8003"]
        ctx["Context Service\nPort: 8004"]
        question["Question Detector\nPort: 8005"]
        notify["Notification Service\nPort: 8006"]
    end
    
    subgraph communication["Communication Patterns"]
        rest["REST (HTTP/2)"]
        grpc["gRPC Streaming"]
        websock["WebSocket"]
        msgqueue["Message Queue"]
    end
    
    pyqt -->|REST + JWT| istio
    
    istio --> auth
    istio --> stt
    istio --> resp
    istio --> ctx
    
    stt -->|gRPC| question
    resp -->|gRPC| ctx
    stt -->|MsgQueue| msgqueue
    resp -->|MsgQueue| msgqueue
    
    msgqueue -.-> stt
    msgqueue -.-> resp
    
    ctx -->|WebSocket| notify
    notify -->|WebSocket| pyqt
    
    style mesh fill:#b3e5fc
    style services fill:#c8e6c9
    style communication fill:#fff9c4
```

---

## 6. CI/CD Pipeline

```mermaid
graph LR
    subgraph dev["Development"]
        code["Code Push"]
        branch["Git Branch"]
    end
    
    subgraph ci["CI Pipeline"]
        test["Unit Tests"]
        lint["Linting"]
        sast["SAST Scan"]
        build["Docker Build"]
        sec["Security Scan"]
    end
    
    subgraph deploy["Deployment"]
        ecr["Push to ECR"]
        staging["Deploy Staging"]
        e2e["E2E Tests"]
        aprove["Manual Approval"]
        prod["Deploy Production"]
    end
    
    subgraph monitor["Monitoring"]
        health["Health Check"]
        metrics["Metrics"]
        alert["Alerts"]
    end
    
    code --> branch
    branch -->|GitHub Actions| test
    test --> lint
    lint --> sast
    sast --> build
    build --> sec
    
    sec -->|Success| ecr
    ecr --> staging
    staging --> e2e
    e2e -->|Pass| aprove
    aprove -->|Manual| prod
    
    prod --> health
    health --> metrics
    metrics --> alert
    
    alert -->|Failure| code
    
    style dev fill:#e1f5ff
    style ci fill:#c8e6c9
    style deploy fill:#ffe0b2
    style monitor fill:#f8bbd0
```

---

## 7. Database Schema (Simplified)

```mermaid
erDiagram
    USERS ||--o{ SESSIONS : has
    USERS ||--o{ TRANSCRIPTS : creates
    USERS ||--o{ FEEDBACK : gives
    MEETINGS ||--o{ TRANSCRIPTS : contains
    MEETINGS ||--o{ QUESTIONS : has
    TRANSCRIPTS ||--o{ RESPONSES : has
    RESPONSES ||--o{ FEEDBACK : gets

    USERS {
        uuid user_id PK
        string email UK
        string password_hash
        json preferences
        timestamp created_at
        timestamp updated_at
    }

    SESSIONS {
        uuid session_id PK
        uuid user_id FK
        string access_token
        string refresh_token
        timestamp expires_at
        timestamp created_at
    }

    MEETINGS {
        uuid meeting_id PK
        uuid user_id FK
        string platform
        string meeting_type
        timestamp started_at
        timestamp ended_at
    }

    TRANSCRIPTS {
        uuid transcript_id PK
        uuid meeting_id FK
        string speaker
        string text
        float confidence
        timestamp created_at
    }

    QUESTIONS {
        uuid question_id PK
        uuid transcript_id FK
        float question_score
        float intent_score
        string question_type
    }

    RESPONSES {
        uuid response_id PK
        uuid question_id FK
        string response_text
        string model_used
        int tokens_used
        timestamp generated_at
    }

    FEEDBACK {
        uuid feedback_id PK
        uuid response_id FK
        uuid user_id FK
        int rating
        string comment
        timestamp created_at
    }
```

---

## 8. Kubernetes Deployment Architecture

```mermaid
graph TB
    subgraph cluster["EKS Cluster"]
        subgraph ns["amethyst namespace"]
            subgraph svc["Services"]
                apigw_svc["API Gateway Service"]
                stt_svc["STT Service"]
                resp_svc["Response Service"]
                ctx_svc["Context Service"]
            end
            
            subgraph deploy["Deployments with HPA"]
                stt_dep["STT Deployment\n(10-50 replicas)"]
                resp_dep["Response Deployment\n(5-30 replicas)"]
                ctx_dep["Context Deployment\n(3-20 replicas)"]
            end
            
            subgraph stateful["Stateful Sets"]
                pg_sts["PostgreSQL Primary"]
                redis_sts["Redis Cluster"]
            end
            
            subgraph config["Config & Secrets"]
                cm["ConfigMap"]
                secret["Secret"]
            end
            
            subgraph network["Network Policies"]
                netpol["Deny external\nAllow ingress"]
            end
        end
        
        subgraph ingress_tier["Ingress Tier"]
            ingress["Ingress Controller\n(Nginx)"]
            cert["SSL/TLS Cert\n(Let's Encrypt)"]
        end
    end
    
    subgraph external_lb["AWS"]
        elb["Elastic Load Balancer"]
        waf["Web Application Firewall"]
    end
    
    elb --> waf
    waf --> ingress
    ingress --> cert
    ingress --> apigw_svc
    
    apigw_svc --> stt_svc
    apigw_svc --> resp_svc
    apigw_svc --> ctx_svc
    
    stt_svc --> stt_dep
    resp_svc --> resp_dep
    ctx_svc --> ctx_dep
    
    stt_dep --> redis_sts
    resp_dep --> pg_sts
    ctx_dep --> redis_sts
    
    stt_dep, resp_dep, ctx_dep --> cm
    stt_dep, resp_dep, ctx_dep --> secret
    
    deploy --> netpol
    
    style cluster fill:#e0f2f1
    style ingress_tier fill:#fff9c4
    style external_lb fill:#ffccbc
```

---

## 9. Monitoring Stack Architecture

```mermaid
graph TB
    subgraph services["Services"]
        stt["STT Service"]
        resp["Response Service"]
        api["API Service"]
        db["Database"]
    end
    
    subgraph metrics["Metrics Collection"]
        prom_client["Prometheus Client\n(prom4j)"]
        otel["OpenTelemetry SDK"]
    end
    
    subgraph collection["Data Collection"]
        prom["Prometheus Server"]
        jaeger["Jaeger Collector"]
        els["Elasticsearch"]
    end
    
    subgraph processing["Processing"]
        wal["Prometheus WAL"]
        ts_db["Time Series DB"]
    end
    
    subgraph visualization["Visualization"]
        grafana["Grafana Dashboards"]
        kibana["Kibana Logs"]
        jaeger_ui["Jaeger UI"]
    end
    
    subgraph alerting["Alerting"]
        alertmgr["AlertManager"]
        slack["Slack/PagerDuty"]
    end
    
    stt --> prom_client
    resp --> prom_client
    api --> prom_client
    db --> otel
    
    prom_client --> prom
    otel --> jaeger
    otel --> els
    
    prom --> wal
    wal --> ts_db
    
    ts_db --> grafana
    els --> kibana
    jaeger --> jaeger_ui
    
    ts_db --> alertmgr
    alertmgr --> slack
    
    style services fill:#c8e6c9
    style metrics fill:#b3e5fc
    style collection fill:#ffccbc
    style visualization fill:#f8bbd0
    style alerting fill:#ffeb99
```

---

## 10. Security Layers

```mermaid
graph TB
    subgraph client_security["Client Layer"]
        cert_pin["Certificate Pinning"]
        token_enc["Encrypted Token Storage"]
        mem_secure["Secure Memory Cleanup"]
    end
    
    subgraph transport_security["Transport Layer"]
        tls["TLS 1.3"]
        mtls["mTLS Service-to-Service"]
        hsts["HSTS Headers"]
    end
    
    subgraph auth_security["Auth & Authz Layer"]
        oauth["OAuth2 + OIDC"]
        jwt["JWT Validation"]
        rbac["Role-Based Access Control"]
        mfa["Multi-Factor Auth"]
    end
    
    subgraph data_security["Data Layer"]
        aes256["AES-256 Encryption"]
        key_rotation["Key Rotation (30d)"]
        field_enc["Field-Level Encryption"]
    end
    
    subgraph infra_security["Infrastructure Layer"]
        waf["Web Application Firewall"]
        vpc["VPC Security Groups"]
        ddos["DDoS Protection"]
        vault["Secrets Vault"]
    end
    
    subgraph operational_security["Operational Layer"]
        siem["SIEM Monitoring"]
        audit_log["Immutable Audit Logs"]
        pentest["Regular Pentesting"]
        vuln_scan["Vulnerability Scanning"]
    end
    
    client_security --> auth_security
    transport_security --> auth_security
    auth_security --> data_security
    data_security --> infra_security
    infra_security --> operational_security
    
    style client_security fill:#ffebee
    style transport_security fill:#ffe0b2
    style auth_security fill:#fff9c4
    style data_security fill:#e0f2f1
    style infra_security fill:#f3e5f5
    style operational_security fill:#fce4ec
```

---

## 11. Disaster Recovery

```mermaid
graph TB
    subgraph primary["Primary Region\nUS-EAST"]
        pg_primary["PostgreSQL Primary"]
        redis_primary["Redis Primary"]
        app_primary["App Services"]
    end
    
    subgraph secondary["Secondary Region\nUS-WEST"]
        pg_replica["PostgreSQL Replica\nAsync Replication"]
        redis_replica["Redis Replica"]
        app_standby["App Services\nStandby"]
    end
    
    subgraph backup["Backup & Archive"]
        s3_backup["S3 Daily Backups"]
        glacier["Glacier Archive\n30 days"]
        backup_region["Backup Region"]
    end
    
    subgraph failover["Failover Process"]
        detect["Detect Failure\n(Health checks)"]
        promote["Promote Secondary\nto Primary"]
        update_dns["Update DNS\n(GeoDNS)"]
        notify["Notify Ops Team"]
    end
    
    app_primary -->|Streaming replication| pg_replica
    app_primary -->|Cluster replication| redis_replica
    
    pg_primary -->|Daily backup| s3_backup
    s3_backup -->|Archive| glacier
    s3_backup -->|3-region copy| backup_region
    
    app_primary -.->|Heartbeat missing| detect
    detect --> promote
    promote --> update_dns
    update_dns --> app_standby
    detect --> notify
    
    pg_replica -.->|Becomes primary| pg_primary
    
    style primary fill:#c8e6c9
    style secondary fill:#ffecb3
    style backup fill:#f8bbd0
    style failover fill:#ffccbc
```

---

## 12. Response Caching Strategy

```mermaid
graph LR
    subgraph request["Incoming Request"]
        q["User Question:\n'Explain databases'"]
    end
    
    subgraph cache["Cache Layer"]
        exact["Exact Match\nRedis Hash"]
        similar["Similar Match\nRedis Search"]
        ttl["TTL: 7 days"]
    end
    
    subgraph gen["Generation"]
        classify["Classify Question"]
        embed["Create Embedding\n(Vector)"]
        search["Vector Search\nElasticsearch"]
        gen_resp["Generate Response\nGemini"]
        format["Format & Score"]
    end
    
    subgraph storage["Storage"]
        store_cache["Store in Redis"]
        store_es["Store in Elasticsearch"]
        store_pg["Store in PostgreSQL"]
    end
    
    q -->|Hash lookup| exact
    
    exact -->|Hit!| store_cache
    exact -->|Miss| similar
    
    similar -->|Similar found| format
    similar -->|No match| classify
    
    classify --> embed
    embed --> search
    search -->|Found| format
    search -->|Not found| gen_resp
    
    gen_resp --> format
    format --> store_cache
    format --> store_es
    format --> store_pg
    
    store_cache -->|Response| q
    
    style request fill:#e3f2fd
    style cache fill:#fff9c4
    style gen fill:#c8e6c9
    style storage fill:#f8bbd0
```

---

All diagrams are Mermaid syntax and can be viewed in:
- GitHub markdown preview
- Mermaid Live Editor (mermaid.live)
- VS Code with Mermaid extension

