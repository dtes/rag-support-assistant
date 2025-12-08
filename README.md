# RAG-based AI Support Assistant

## Project Description

### Core Idea
AI assistant for website user support, using RAG (Retrieval-Augmented Generation) to provide accurate answers based on site documentation.

### Concept
The system automatically indexes website documentation in a vector database and provides users with an intelligent chat interface for information retrieval. When receiving a question, the system finds relevant documentation fragments and generates an accurate answer using an LLM.

### Technical Details

#### System Architecture
- **Frontend**: Simple web interface with chat (HTML/CSS/JavaScript)
- **Backend**: FastAPI server (Python)
- **Vector Database**: Weaviate
- **LLM Provider**: Anthropic Claude API
- **Embeddings**: Local sentence-transformers (all-MiniLM-L6-v2)

#### Components
1. **Weaviate** - vector database for storing documentation chunks
2. **Backend API** - request processing, embedding creation, RAG pipeline
3. **Auto-loader** - automatic documentation loading and indexing on startup
4. **Web UI** - chat interface for users

### Dataset Concept
- **Data Type**: Markdown files with site documentation
- **Volume**: 20 documentation articles
- **Storage Format**: Documents are split into chunks (~500 tokens), each chunk is vectorized
- **Metadata**: filename, title, chunk position

### System Requirements
- Docker and Docker Compose
- 8GB RAM (minimum), 16GB RAM (recommended)
- API key: Anthropic Claude only (embeddings are generated locally)

### Limitations
- Works only with text documentation in Markdown format
- Requires internet connection for API access
- Limited multilingual support (optimized for Russian/English)

## Quick Start

### Prerequisites
1. Install Docker and Docker Compose
2. Obtain API key:
   - Anthropic Claude API: https://console.anthropic.com/

### Installation and Launch

1. **Clone/unzip the project**
```bash
cd rag-support-assistant
```

2. **Add documentation**
Place your .md files in the `data/` folder:
```bash
cp your_docs/*.md data/
```

3. **Configure environment variables**
Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

4. **Launch the system**
```bash
docker-compose up --build
```

On first launch:
- Weaviate will start and create the schema
- Local embedding model (all-MiniLM-L6-v2) will be downloaded automatically
- Backend will automatically load all .md files from the `data/` folder
- Documentation will be split into chunks and indexed using local embeddings

5. **Open UI**
Open browser: http://localhost:8000

### Stopping the system
```bash
docker-compose down
```

### Data cleanup
For complete cleanup (including vector DB):
```bash
docker-compose down -v
```

## Usage

1. Open the web interface in your browser
2. Enter a question about site documentation
3. The system will find relevant fragments and generate an answer
4. The answer will be based on actual documentation with source attribution

## Example Questions
- "How to register on the site?"
- "What payment methods are supported?"
- "How to reset password?"
- "What to do if an error occurs during checkout?"

## Project Structure
```
rag-support-assistant/
├── docker-compose.yml          # Container orchestration
├── .env                        # API keys (create manually)
├── README.md                   # Documentation
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI application
│   ├── rag_service.py          # RAG logic
│   └── loader.py               # Documentation loader
├── frontend/
│   └── index.html              # Web chat interface
└── data/                       # Folder for .md files (add yourself)
```

## Technical Implementation

### RAG Pipeline
1. **Indexing** (on startup):
   - Reading .md files from `data/`
   - Splitting into chunks (RecursiveCharacterTextSplitter)
   - Creating embeddings using local sentence-transformers model
   - Saving to Weaviate

2. **Query Processing**:
   - Receiving user question
   - Creating embedding for the question using local model
   - Searching for top-3 relevant chunks in Weaviate
   - Forming context
   - Generating response via Claude API
   - Returning response with sources

### API Endpoints
- `GET /` - Web interface
- `POST /chat` - Main endpoint for questions
- `GET /health` - System health check
- `GET /stats` - Database statistics

## Troubleshooting

### Issue: Containers not starting
**Solution**: Ensure Docker is running and ports 8000, 8080 are free

### Issue: API key error
**Solution**: Check `.env` file and key validity

### Issue: Documentation not loading
**Solution**:
- Ensure .md files are in the `data/` folder
- Check logs: `docker-compose logs backend`

### Issue: Slow responses
**Solution**: First request may be slow (cold start). Subsequent ones are faster.

## Video Demonstration
[Video link to be added after recording]
