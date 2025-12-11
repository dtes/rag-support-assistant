# Quick Start Guide

## Minimal Steps to Launch

### 1. Prerequisites
- Docker and Docker Compose installed
- No API keys needed - fully local!

### 2. Installation (Optional)

```bash
# Optional: Create .env file to use different model
cat > .env << EOF
OLLAMA_MODEL=llama3.2:3b
EOF
```

### 3. Add Documentation

```bash
# Copy your .md files to the data/ folder
cp /path/to/documentation/*.md data/
```

### 4. Launch

```bash
# Start all services
docker-compose up --build
```

Wait 30-60 seconds for document indexing.

### 5. Usage

Open browser: **http://localhost:8000**

### 6. Component Health Checks

**Check 1: Weaviate (Vector DB)**
```bash
curl http://localhost:8080/v1/.well-known/ready
```
Response: `{"status":"ok"}`

**Check 2: Backend API**
```bash
curl http://localhost:8000/health
```
Response: `{"status":"ok","service":"RAG Support Assistant","weaviate":"connected"}`

**Check 3: Database Statistics**
```bash
curl http://localhost:8000/stats
```
Response will show the number of indexed chunks

**Check 4: RAG System**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"How to register?"}'
```

### 7. Shutdown

```bash
# Stop the system
docker-compose down

# Complete cleanup (including DB data)
docker-compose down -v
```

## Troubleshooting

**Issue**: Ports are busy
**Solution**: Change ports in `docker-compose.yml` or stop other services

**Issue**: Ollama model downloading
**Solution**: First launch downloads ~2GB model. Wait patiently - this is one-time only.

**Issue**: Documentation not loading
**Solution**:
1. Check for .md files in `data/`
2. View logs: `docker-compose logs backend`
3. Restart with cleanup: `docker-compose down -v && docker-compose up --build`

## System Operation Demonstration

### Step 1: Data Loading
Logs will show:
```
backend_1    | ==========================================
backend_1    | Loading documentation into vector database
backend_1    | ==========================================
backend_1    | Found 20 .md files for indexing
backend_1    | Processing: registration.md
backend_1    |   → Created 5 chunks
backend_1    |   ✓ File registration.md indexed
backend_1    | ...
backend_1    | ✓ Indexing completed: 142 chunks from 20 files
backend_1    | ✓ System ready
```

### Step 2: Embedding Search
On user query:
```
backend_1    | Query: How to register?
backend_1    | Documents found: 3
```

### Step 3: Response Generation
Local Ollama LLM generates response based on found documents

### Step 4: Result
User receives response with source attribution

## RAG Execution Architecture

```
User Query → Embedding (Local sentence-transformers) → Vector Search (Weaviate) → Context + Query → LLM (Local Ollama) → Response
```

All components are now fully local:
1. ✓ Idea and description in README.md
2. ✓ Data: .md files in data/ folder
3. ✓ Database: Weaviate in Docker
4. ✓ Embeddings: Local sentence-transformers (all-MiniLM-L6-v2)
5. ✓ Auto-loading: loader.py on startup
6. ✓ LLM client: Local Ollama (Llama 3.2 3B)
7. ✓ UI: Web chat interface
8. ✓ RAG system: complete pipeline in rag_service.py
9. ✓ Video: [link to be added]
