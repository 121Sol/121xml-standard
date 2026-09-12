# 121AI Deployment Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Git
- 8GB RAM minimum
- 50GB disk space

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/rashadkhan/121ai.git
cd 121ai
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install 121AI
```bash
pip install -e .
```

#### 4. Initialize Configuration
```bash
121ai-config
```

#### 5. Start Server
```bash
121ai serve --port 8000
```

Visit: `http://localhost:8000`

---

## Platform-Specific Deployment

### Web Deployment

#### Docker (Recommended)
```bash
docker run -d \
  -p 8000:8000 \
  -e 121AI_ENV=production \
  -v ./config:/app/config \
  121ai:latest
```

#### Kubernetes
```bash
kubectl apply -f deployment/kubernetes.yaml
kubectl port-forward svc/121ai 8000:8000
```

#### AWS (EC2 + RDS)
```bash
terraform init
terraform apply -var="environment=production"
```

#### Google Cloud (Cloud Run)
```bash
gcloud run deploy 121ai \
  --source . \
  --platform managed \
  --region us-central1
```

#### Azure (App Service)
```bash
az webapp create \
  --resource-group 121ai-rg \
  --plan 121ai-plan \
  --name 121ai-app \
  --runtime "PYTHON:3.11"
```

### Windows Deployment

#### Standalone Executable
1. Download `121AI-1.0.0.exe` from releases
2. Run installer
3. Configure in Settings → Admin Panel
4. Start service (automatic on boot)

#### Windows Service
```powershell
.\install.ps1
sc start 121ai-service
```

### macOS Deployment

#### DMG Installer
1. Download `121AI-1.0.0.dmg` from releases
2. Open DMG file
3. Drag 121AI to Applications
4. Run: `/Applications/121AI.app/Contents/MacOS/121ai`

### Linux Deployment

#### AppImage
```bash
chmod +x 121AI-1.0.0-x86_64.AppImage
./121AI-1.0.0-x86_64.AppImage
```

#### Systemd Service
```bash
sudo cp deployment/121ai.service /etc/systemd/system/
sudo systemctl enable 121ai
sudo systemctl start 121ai
```

### iOS Deployment

#### Testflight
1. Download `121AI-1.0.0.ipa` from releases
2. Use Apple Testflight app to install

### Android Deployment

#### Google Play Store
1. Upload APK to Google Play Console
2. Configure store listing
3. Submit for review

#### Direct APK Install
```bash
adb install 121AI-1.0.0-debug.apk
```

---

## Configuration

### Environment Variables
```bash
121AI_ENV=production              # production or development
121AI_PORT=8000                   # Server port
121AI_WORKERS=4                   # Worker processes
121AI_DATABASE_URL=postgresql://... # Database connection
121AI_LOG_LEVEL=INFO              # Log level
```

### Configuration File (config/121ai.yml)
```yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  ssl:
    enabled: true

database:
  engine: postgresql
  url: postgresql://user:pass@localhost/121ai
  pool_size: 20

auth:
  providers:
    - google
    - microsoft
    - github

logging:
  level: INFO
  format: json
```

---

## Production Checklist

- [ ] Enable TLS/SSL
- [ ] Configure authentication
- [ ] Set up automated backups
- [ ] Enable monitoring & alerting
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Test disaster recovery
- [ ] Set up firewall rules
- [ ] Document runbooks

---

## Support

- **Documentation**: https://121ai.readthedocs.io
- **Issues**: https://github.com/rashadkhan/121ai/issues
- **Email**: support@121ai.io

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*