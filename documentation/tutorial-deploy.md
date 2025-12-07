# 🚀 Deployment Tutorial

Panduan lengkap untuk deploy Customer Service Agent ke VPS atau hosting.

## 📋 Requirements

### Minimal Server Specs
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU      | 2 cores | 4+ cores    |
| RAM      | 4 GB    | 8+ GB       |
| Storage | 20 GB SSD | 50+ GB SSD |
| OS | Ubuntu 22.04+ | Ubuntu 24.04 LTS |

> ⚠️ **Note**: Ollama membutuhkan RAM yang cukup besar. Jika RAM terbatas, gunakan external LLM API (OpenAI/Groq).

## 🛠️ Step 1: Prepare VPS

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, then verify
docker --version
```

### 1.3 Install Docker Compose
```bash
# Docker Compose sudah termasuk di Docker Engine terbaru
docker compose version
```

### 1.4 Install Git
```bash
sudo apt install git -y
```

## 📦 Step 2: Clone & Configure

### 2.1 Clone Repository
```bash
cd /opt
sudo git clone <your-repo-url> cs-ai-agent
sudo chown -R $USER:$USER cs-ai-agent
cd cs-ai-agent
```

### 2.2 Configure Environment
```bash
cp config/.env.example .env
nano .env
```

**Edit `.env` untuk production:**
```bash
# ... (same as before)
```

## 🔧 Step 3: Production Configuration

File `docker-compose.prod.yml` sudah tersedia di folder `infra/`.

### 3.2 Jalankan dengan Production Config
Masuk ke folder `infra` dan jalankan:

```bash
cd infra
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 🌐 Step 4: Setup Reverse Proxy (Nginx)

### 4.1 Install Nginx
```bash
sudo apt install nginx -y
```

### 4.2 Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/cs-agent
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Streamlit UI
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # FastAPI Backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # LightRAG API (optional, for direct access)
    location /lightrag/ {
        proxy_pass http://localhost:9621/;
        proxy_set_header Host $host;
        proxy_read_timeout 300;
    }
}
```

### 4.3 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/cs-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Step 5: Setup SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL Certificate
sudo certbot --nginx -d your-domain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

## 🚀 Step 6: Start Services

### 6.1 Build & Start
```bash
cd /opt/cs-ai-agent
docker compose up -d --build
```

### 6.2 Pull Ollama Models
```bash
docker exec ollama ollama pull llama3.2
docker exec ollama ollama pull mxbai-embed-large
```

### 6.3 Verify Services
```bash
docker compose ps
```

Semua services harus `Up`:
```
NAME           STATUS
app            Up
streamlit      Up
qdrant         Up
neo4j          Up (healthy)
lightrag       Up
postgres       Up
ollama         Up
```

## 📊 Step 7: Monitoring

### 7.1 View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f lightrag
```

### 7.2 Check Resource Usage
```bash
docker stats
```

### 7.3 Create Monitoring Script
```bash
nano /opt/cs-ai-agent/health-check.sh
```

```bash
#!/bin/bash
# Health check script

echo "=== Service Status ==="
docker compose ps

echo -e "\n=== API Health ==="
curl -s http://localhost:8000/health | jq .

echo -e "\n=== LightRAG Health ==="
curl -s http://localhost:9621/health | jq .

echo -e "\n=== Memory Usage ==="
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"
```

```bash
chmod +x /opt/cs-ai-agent/health-check.sh
```

## 🔄 Step 8: Auto-Restart & Updates

### 8.1 Create Systemd Service (Optional)
```bash
sudo nano /etc/systemd/system/cs-agent.service
```

```ini
[Unit]
Description=Customer Service Agent
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/cs-ai-agent
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=root

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cs-agent
sudo systemctl start cs-agent
```

### 8.2 Update Script
```bash
nano /opt/cs-ai-agent/update.sh
```

```bash
#!/bin/bash
cd /opt/cs-ai-agent
git pull origin main
docker compose down
docker compose up -d --build
docker compose logs -f --tail=50
```

```bash
chmod +x /opt/cs-ai-agent/update.sh
```

## 🔥 Firewall Configuration

```bash
# Allow necessary ports
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH

# Enable firewall
sudo ufw enable
```

## ⚡ Performance Tips

### Low RAM Mode (< 8GB)

Jika RAM terbatas, disable Ollama dan gunakan external API:

1. Comment out ollama service di `docker-compose.yml`
2. Update `.env`:
```bash
# Use Groq instead of Ollama
GROQ_API_KEY=gsk_xxx
```
3. Update LightRAG untuk pakai OpenAI-compatible API

### Optimize Qdrant
```yaml
# di docker-compose.yml
qdrant:
  environment:
    - QDRANT__STORAGE__PERFORMANCE__MAX_OPTIMIZATION_THREADS=2
```

## 🛡️ Security Checklist

- [ ] Ganti semua default passwords
- [ ] Setup SSL/HTTPS
- [ ] Configure firewall
- [ ] Enable fail2ban untuk SSH
- [ ] Regular backups
- [ ] Keep Docker & system updated

## 📞 Troubleshooting

### Container keeps restarting
```bash
docker compose logs <service-name>
```

### Out of memory
```bash
# Check memory
free -h

# Reduce memory limits in docker-compose.prod.yml
# Or add swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Port already in use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

---

## 🎉 Done!

Setelah semua langkah selesai, akses:
- **Main UI**: https://your-domain.com
- **API Docs**: https://your-domain.com/api/docs
- **LightRAG**: https://your-domain.com/lightrag/docs
