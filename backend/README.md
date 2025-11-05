# SSC RAG Backend

FastAPI backend for SSC Question RAG system with ChromaDB vector storage.

## Quick Start

### Using Docker Compose (Recommended)

1. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your configuration

Step-2:
docker-compose -f docker-compose.backend.yml up -d

Step-3:
docker-compose -f docker-compose.backend.yml ps


Using Python Directly
Install dependencies:

bash
pip install -r requirements.txt
Set environment variables (copy from .env.example)

Run the server:

bash
python run.py



Services
Backend API: http://localhost:8000

ChromaDB: http://localhost:8001

API Docs: http://localhost:8000/docs

Health Check: http://localhost:8000/health

API Endpoints
POST /query - Search similar questions

POST /process-file - Upload and process question papers

GET /subjects - List available subjects

GET /health - Health check

GET /stats - System statistics

Development

Running with hot reload:
]
docker-compose -f docker-compose.backend.yml up backend

View logs:

docker-compose -f docker-compose.backend.yml logs -f backend

Stop services:

docker-compose -f docker-compose.backend.yml down

Production Deployment
Set ENVIRONMENT=production in .env

Set RELOAD=false

Use proper AWS credentials with limited permissions

Consider using RDS instead of PostgreSQL container

Use ElastiCache instead of Redis container

text

## Usage Commands

### Start Backend Services:
```bash
cd backend
docker-compose -f docker-compose.backend.yml up -d
Stop Services:
bash
cd backend
docker-compose -f docker-compose.backend.yml down

View Logs:

cd backend
docker-compose -f docker-compose.backend.yml logs -f backend
Scale Services (if needed):

cd backend
docker-compose -f docker-compose.backend.yml up -d --scale backend=2
