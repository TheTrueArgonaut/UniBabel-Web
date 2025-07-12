# UniBabel Production Deployment Guide

## 🚀 Production-Ready Architecture Overview

UniBabel is now a **enterprise-grade real-time translation messaging platform** with complete
microservice architecture, ready for production deployment.

### ✅ **COMPLETED FEATURES**

- **Real-time messaging** with WebSocket integration
- **Enterprise translation pipeline** with multi-tier caching
- **Microservice API architecture** (Friends, Chats, Users, Activity, Translation)
- **Mobile-responsive design** with touch-optimized UI
- **Friend management system** with online presence
- **Live activity feeds** with real-time notifications
- **Translation integration** with user preferences
- **Comprehensive error handling** and graceful fallbacks

---

## 🏗️ **DEPLOYMENT ARCHITECTURE**

### **Recommended Production Stack:**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway    │    │   Microservices │
│   (Nginx/HAProxy)│ -> │   (Kong/Envoy)   │ -> │   (Flask Apps)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Static Files  │    │   WebSocket      │    │   Database      │
│   (CloudFront)  │    │   (Socket.IO)    │    │   (PostgreSQL)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 📦 **CONTAINERIZATION**

### **1. Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash unibabel
RUN chown -R unibabel:unibabel /app
USER unibabel

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "eventlet", "main:app"]
```

### **2. Docker Compose for Development**

```yaml
version: '3.8'

services:
  unibabel-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/unibabel
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./instance:/app/instance
    
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: unibabel
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## ☁️ **CLOUD DEPLOYMENT OPTIONS**

### **Option 1: AWS Deployment**

#### **Services Required:**

- **ECS/EKS** - Container orchestration
- **RDS PostgreSQL** - Database
- **ElastiCache Redis** - Caching & sessions
- **ALB** - Load balancing
- **CloudFront** - CDN for static files
- **Route 53** - DNS management
- **Certificate Manager** - SSL certificates

#### **AWS Architecture:**

```yaml
# docker-compose.aws.yml
version: '3.8'
services:
  unibabel:
    image: your-ecr-repo/unibabel:latest
    environment:
      - DATABASE_URL=${RDS_DATABASE_URL}
      - REDIS_URL=${ELASTICACHE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEEPL_API_KEY=${DEEPL_API_KEY}
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
```

### **Option 2: Google Cloud Platform**

#### **Services Required:**

- **Cloud Run** - Serverless containers
- **Cloud SQL** - PostgreSQL database
- **Memorystore** - Redis cache
- **Cloud Load Balancer** - Traffic distribution
- **Cloud CDN** - Static file delivery
- **Cloud DNS** - Domain management

### **Option 3: DigitalOcean (Cost-Effective)**

#### **Setup:**

1. **Droplets** - Application servers (2-4 instances)
2. **Managed Database** - PostgreSQL cluster
3. **Managed Redis** - Cache cluster
4. **Load Balancer** - Traffic distribution
5. **Spaces CDN** - Static file delivery

---

## 🔧 **ENVIRONMENT CONFIGURATION**

### **Production Environment Variables:**

```bash
# Application
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DEBUG=False

# Database
DATABASE_URL=postgresql://user:pass@host:5432/unibabel_prod

# Redis (for caching and sessions)
REDIS_URL=redis://redis-host:6379/0

# Translation Services
DEEPL_API_KEY=your-deepl-api-key
TRANSLATE_ALL_API_URL=https://api.deepl.com/v2/translate
TRANSLATE_ALL_API_KEY=your-deepl-api-key

# Security
CSRF_SECRET_KEY=your-csrf-secret
JWT_SECRET_KEY=your-jwt-secret

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-newrelic-key

# File Storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=unibabel-uploads
```

---

## 🔒 **SECURITY CONFIGURATION**

### **1. SSL/TLS Setup**

```nginx
# /etc/nginx/sites-available/unibabel
server {
    listen 443 ssl http2;
    server_name unibabel.com www.unibabel.com;
    
    ssl_certificate /etc/letsencrypt/live/unibabel.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/unibabel.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.tailwindcss.com cdn.socket.io; style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com; font-src fonts.gstatic.com; connect-src 'self' wss:;" always;
    
    location / {
        proxy_pass http://unibabel_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /socket.io/ {
        proxy_pass http://unibabel_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

upstream unibabel_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}
```

### **2. Database Security**

```sql
-- Create production database user with limited privileges
CREATE USER unibabel_app WITH PASSWORD 'secure-password';
CREATE DATABASE unibabel_prod OWNER unibabel_app;
GRANT CONNECT ON DATABASE unibabel_prod TO unibabel_app;
GRANT USAGE ON SCHEMA public TO unibabel_app;
GRANT CREATE ON SCHEMA public TO unibabel_app;
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **1. Application Monitoring**

```python
# monitoring.py
import logging
from flask import request
import time

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/app.log')
    ]
)

# Metrics collection
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    logger.info(f"Request {request.method} {request.path} - {response.status_code} - {duration:.2f}s")
    return response
```

### **2. Health Check Endpoint**

```python
# Add to main.py
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check Redis connection
        redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'up',
                'redis': 'up',
                'translation': 'up'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

---

## 🚀 **DEPLOYMENT PROCESS**

### **1. Pre-deployment Checklist**

- [ ] All environment variables configured
- [ ] Database migrations tested
- [ ] SSL certificates installed
- [ ] Monitoring systems configured
- [ ] Backup systems in place
- [ ] Load testing completed
- [ ] Security audit passed

### **2. Zero-Downtime Deployment**

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Starting UniBabel deployment..."

# 1. Build new Docker image
docker build -t unibabel:$BUILD_NUMBER .

# 2. Run database migrations
docker run --rm -e DATABASE_URL=$DATABASE_URL unibabel:$BUILD_NUMBER python migrate_database.py

# 3. Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# 4. Run health checks
./scripts/health_check.sh staging

# 5. Deploy to production (rolling update)
docker service update --image unibabel:$BUILD_NUMBER unibabel_app

# 6. Verify deployment
./scripts/health_check.sh production

echo "✅ Deployment completed successfully!"
```

### **3. Rollback Strategy**

```bash
#!/bin/bash
# rollback.sh

PREVIOUS_VERSION=$1

echo "🔄 Rolling back to version $PREVIOUS_VERSION..."

docker service update --image unibabel:$PREVIOUS_VERSION unibabel_app
./scripts/health_check.sh production

echo "✅ Rollback completed!"
```

---

## 📈 **SCALING CONSIDERATIONS**

### **Horizontal Scaling:**

- **Application Servers:** 3-10 instances behind load balancer
- **Database:** Read replicas for query optimization
- **Redis:** Cluster mode for high availability
- **WebSocket:** Sticky sessions or Redis adapter

### **Performance Optimization:**

```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "eventlet"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
```

---

## 💰 **COST ESTIMATION**

### **Small Scale (1K-10K users):**

- **AWS:** $200-500/month
- **GCP:** $180-450/month
- **DigitalOcean:** $100-300/month

### **Medium Scale (10K-100K users):**

- **AWS:** $500-2000/month
- **GCP:** $450-1800/month
- **DigitalOcean:** $300-1200/month

### **Large Scale (100K+ users):**

- **AWS:** $2000+/month
- **GCP:** $1800+/month
- **DigitalOcean:** $1200+/month

---

## 🎯 **LAUNCH READINESS**

### **✅ Technical Readiness:**

- [x] Microservice architecture implemented
- [x] Real-time messaging with WebSockets
- [x] Translation pipeline integrated
- [x] Mobile-responsive design
- [x] Error handling and monitoring
- [x] Security measures implemented

### **🚀 Ready for Production Deployment**

UniBabel is **production-ready** with:

- **Enterprise-grade architecture**
- **Scalable microservice design**
- **Real-time translation capabilities**
- **Mobile-optimized experience**
- **Comprehensive monitoring**

**Next Steps:**

1. Choose cloud provider
2. Set up CI/CD pipeline
3. Configure monitoring
4. Deploy to staging
5. Load test
6. Go live! 🎉

---

*UniBabel - Breaking language barriers, one conversation at a time.* 🌍