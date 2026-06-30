# ResearchGPT Chatbot - Docker Deployment

Chat interface untuk Research Gatherer dengan database MongoDB untuk menyimpan history chat dan konfigurasi.

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Frontend   │   Backend    │   MongoDB    │   Mongo    │
│   (Nginx)    │   (FastAPI)  │  (Database)  │  Express   │
│   Port 3000  │   Port 8001  │  Port 27017  │ Port 8081  │
└──────────────┴──────────────┴──────────────┴────────────┘
```

### Komponen

1. **Frontend** (Nginx) - Chat UI dengan sidebar history
2. **Backend** (FastAPI) - REST API untuk mengelola sessions dan config
3. **MongoDB** - Database untuk menyimpan chat history dan konfigurasi
4. **Mongo Express** - Web UI untuk manage MongoDB (opsional)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Research Gatherer API running (atau update konfigurasi)

### 1. Clone & Setup

```bash
cd /home/mws/tfs/github/research-gatherer/apps/chatbot

# Copy environment variables
cp .env.example .env
```

### 2. Build & Deploy

```bash
# Build dan jalankan semua service
make build

# Atau manual:
docker-compose up -d --build
```

### 3. Akses Aplikasi

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8001/docs | - |
| **Mongo Express** | http://localhost:8081 | admin / admin123 |
| **MongoDB** | mongodb://localhost:27017 | - |

## 📁 Struktur Proyek

```
chatbot/
├── backend/
│   ├── main.py              # FastAPI backend
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── index.html           # Chat UI dengan history sidebar
│   └── Dockerfile
├── docker-compose.yml       # Orkestrasi semua service
├── .env                     # Environment variables
├── .env.example             # Template environment
├── Makefile                 # Helper commands
└── README.md
```

## 🔧 Makefile Commands

```bash
# Start services
make up

# Build dan start
make build

# Stop services
make down

# View logs
make logs

# Restart services
make restart

# Check status
make status

# Test backend health
make test

# Reset everything (WARNING: destroys data)
make clean

# Access MongoDB shell
make mongo

# Open Mongo Express
make mongo-ui
```

## 📊 Database Schema

### Collection: `sessions`

```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "title": "string",
  "messages": [
    {
      "role": "user|assistant|error",
      "content": "string",
      "timestamp": "ISODate"
    }
  ],
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

### Collection: `config`

```json
{
  "_id": "default",
  "api_base": "http://research-gatherer:8000",
  "api_key": "",
  "model_name": "research-assistant",
  "stream_enabled": true,
  "byok_enabled": false,
  "byok_url": "https://api.openai.com/v1",
  "byok_key": "",
  "byok_model": "gpt-4o",
  "updated_at": "ISODate"
}
```

## 🔌 Backend API Endpoints

### Sessions Management

```bash
# Get all sessions
GET /api/sessions

# Create new session
POST /api/sessions

# Get specific session
GET /api/sessions/{session_id}

# Update session
PUT /api/sessions/{session_id}

# Delete session
DELETE /api/sessions/{session_id}

# Add message to session
POST /api/sessions/{session_id}/messages
```

### Configuration

```bash
# Get config
GET /api/config

# Update config
PUT /api/config
```

### Utilities

```bash
# Health check
GET /health

# Statistics
GET /api/stats
```

## 🎨 Frontend Features

- ✅ **Chat History Sidebar** - List semua chat sessions
- ✅ **Auto-save Messages** - Otomatis menyimpan setiap pesan
- ✅ **Persistent Config** - Konfigurasi tersimpan di database
- ✅ **BYOK Support** - Bring Your Own Key (OpenAI/custom LLM)
- ✅ **Streaming Responses** - Real-time streaming dari LLM
- ✅ **Citation Support** - Markdown rendering dengan citation markers
- ✅ **Dark Theme** - Modern GitHub-inspired dark UI

## 🔐 Keamanan

1. **MongoDB** - Tidak ada authentication (internal network only)
2. **Mongo Express** - Protected dengan basic auth (admin/admin123)
3. **Backend API** - CORS enabled untuk development

> ⚠️ **Production**: Tambahkan MongoDB authentication dan ubah Mongo Express password!

## 🐛 Troubleshooting

### Backend tidak connect ke MongoDB

```bash
# Check MongoDB status
docker logs chatbot-mongodb

# Restart MongoDB
docker-compose restart mongodb

# Check network
docker network inspect chatbot-network
```

### Frontend tidak bisa connect ke backend

```bash
# Check backend logs
docker logs chatbot-backend

# Test backend health
curl http://localhost:8001/health

# Check CORS settings di backend/main.py
```

### MongoDB data loss after restart

```bash
# Check volumes
docker volume ls | grep chatbot

# Ensure volumes are defined in docker-compose.yml
```

## 📈 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f mongodb
```

### Database Statistics

```bash
# Via API
curl http://localhost:8001/api/stats

# Via Mongo Express
# Open http://localhost:8081
```

### Health Check

```bash
# Backend + MongoDB
curl http://localhost:8001/health | jq

# Expected output:
# {
#   "status": "healthy",
#   "mongodb": "connected",
#   "timestamp": "2026-06-30T09:00:00.000Z"
# }
```

## 🚀 Production Deployment

### 1. Tambahkan MongoDB Authentication

Edit `docker-compose.yml`:

```yaml
mongodb:
  environment:
    - MONGO_INITDB_ROOT_USERNAME=admin
    - MONGO_INITDB_ROOT_PASSWORD=<strong-password>
```

### 2. Update Connection String

Edit `backend/main.py`:

```python
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://admin:<password>@mongodb:27017/?authSource=admin"
)
```

### 3. Secure Mongo Express

Edit `docker-compose.yml`:

```yaml
mongo-express:
  environment:
    - ME_CONFIG_BASICAUTH_USERNAME=<new-username>
    - ME_CONFIG_BASICAUTH_PASSWORD=<strong-password>
```

### 4. Add HTTPS (Nginx Reverse Proxy)

```bash
# Install certbot
# Configure nginx upstream
# Generate SSL certificates
```

### 5. Backup Strategy

```bash
# Backup MongoDB
docker exec chatbot-mongodb mongodump --out /backup

# Restore MongoDB
docker exec chatbot-mongodb mongorestore /backup
```

## 🔄 Update & Migration

### Update Backend Code

```bash
# Edit backend/main.py
# Restart backend only
docker-compose restart backend
```

### Update Frontend

```bash
# Edit frontend/index.html
# Rebuild frontend
docker-compose up -d --build frontend
```

### Database Migration

```bash
# Connect to MongoDB
docker exec -it chatbot-mongodb mongosh

# Run migration commands
use chatbot_db
db.sessions.updateMany({}, {$set: {new_field: "value"}})
```

## 📝 Development

### Local Development (without Docker)

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set MongoDB URL
export MONGO_URL=mongodb://localhost:27017

# Run
uvicorn main:app --reload --port 8001
```

#### Frontend

```bash
cd frontend
python -m http.server 3000
```

### Hot Reload

Backend sudah dikonfigurasi dengan `--reload` flag untuk auto-reload saat file berubah.

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License

## 🆘 Support

- Issues: GitHub Issues
- Docs: `/docs` endpoint di backend
- MongoDB UI: Mongo Express di port 8081

---

**Made with ❤️ for Research Gatherer**