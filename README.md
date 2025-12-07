# 🤖 Customer Service Agent

A modular, production-ready Customer Service Agent built with LangChain, FastAPI, LightRAG, and Neo4j.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Knowledge Base Management](#-knowledge-base-management)
- [Database Management](#-database-management)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

| Feature | Description |
|---------|-------------|
| **RAG Knowledge Base** | LightRAG with Qdrant (vectors) + Neo4j (knowledge graph) |
| **Long-term Memory** | User context persistence with Mem0 + PostgreSQL |
| **Multi-channel** | Web, WhatsApp, Telegram with unified message format |
| **LLM Fallback** | Prioritized fallback: OpenAI → Groq → Ollama |
| **Streamlit UI** | Admin dashboard for testing and management |

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│   FastAPI App   │────▶│  LangGraph Agent│
│   (Port 8501)   │     │   (Port 8000)   │     │                 │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                       │
                    ┌────────────┴────────────┐          │
                    ▼                         ▼          ▼
            ┌───────────────┐         ┌───────────────┐  │
            │   PostgreSQL  │         │     Mem0      │  │
            │  (Checkpoints)│         │   (Memory)    │◀─┘
            └───────────────┘         └───────────────┘
                                             │
                                             ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    LightRAG     │────▶│     Qdrant      │     │     Neo4j       │
│   (Port 9621)   │     │   (Port 6333)   │     │   (Port 7474)   │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│     Ollama      │
│  (Port 11434)   │
└─────────────────┘
```

## 📁 Project Structure

```
cs-ai-BluePrint/
├── app/               # Application code
├── infra/             # Docker & Deployment files
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── documentation/     # Guides & Manuals
├── config/            # Configuration files
├── .env               # Environment variables (Keep at root)
└── README.md
```

## 🚀 Quick Start

### 1. Configure Environment
Copy `.env.example` from `config/` to root `.env`:
```bash
cp config/.env.example .env
# Edit .env with your keys
```

### 2. Run with Docker
You need to point to the `.env` file when running from `infra/`:
```bash
cd infra
docker compose --env-file ../.env up -d --build
```
*Note: We use `--env-file ../.env` because the compose file is in `infra/` but `.env` is at root.*

### 3. Access UIs
(Same as before: http://localhost:8501, etc.)

## 🔧 Production Deployment

To run in production mode (using `infra/docker-compose.prod.yml`):

```bash
cd infra
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 📝 License

MIT License
