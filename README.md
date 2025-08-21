# Browser History Summarizer

A scalable distributed system that automatically processes browser history using AI-powered content analysis and semantic search capabilities.

## Overview

This project transforms your browsing history into intelligent, searchable summaries using a distributed architecture built with Docker, RabbitMQ, and local LLM integration. The system processes any number of URLs in parallel, generating concise AI summaries that enable semantic search through your browsing patterns. Currently supporting Safari browsing history, with other browser support (Chrome, Firefox) planned.

## Key Features

- **Distributed Processing**: Horizontally scalable worker architecture using RabbitMQ message queuing
- **AI-Powered Summarization**: Local LLM integration (Ollama/Granite3.2) for privacy-focused content analysis  
- **Semantic Search**: CLI interface for intelligent querying of processed browser history
- **Fault Tolerance**: Automatic message requeuing and error handling for reliable processing
- **Containerized**: Full Docker Compose orchestration with health checks and service discovery
- **High Performance**: Parallel web scraping and batch database operations

## Architecture

```
Safari History → Ingester → RabbitMQ → Workers → SQLite → Search CLI
                    ↓         ↓         ↓        ↓        ↓
                Publisher   Queue    Scrapers  Database  Results
```

### Core Components

- **RabbitMQ**: Message broker for distributed URL processing
- **Ingester**: Reads Safari history and publishes URLs to message queue
- **Workers**: Scalable containers that scrape, summarize, and store content
- **Search CLI**: Interactive interface for semantic search of processed summaries

## Technology Stack

- **Backend**: Python 3.12, SQLite, RabbitMQ
- **AI/ML**: Ollama, Granite3.2 LLM
- **Infrastructure**: Docker, Docker Compose
- **Web Scraping**: Requests, BeautifulSoup4
- **Data Processing**: Pandas, JSON

## Prerequisites

- Docker and Docker Compose
- Ollama installed and running locally
- Safari browser (for history ingestion)
- Python 3.12+ (for local development)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/cxcollins/browser_history_summarizer.git
cd browser_history_summarizer
```

### 2. Prepare Browser History

```bash
# Copy Safari history to data directory
mkdir -p data
cp ~/Library/Safari/History.db data/
```

### 3. Start Ollama

```bash
# Install and start Ollama with Granite model
ollama serve
ollama pull granite3.2:2b
```

### 4. Launch Distributed System

```bash
# Start message broker
docker-compose up rabbitmq

# Populate URL queue (in new terminal)
docker-compose up ingester

# Start processing with 3 workers (in new terminal)
docker-compose up --scale worker=3
```

### 5. Search Your History

```bash
# Search processed summaries
python frontend/search_cli.py "machine learning tutorials"
python frontend/search_cli.py "React documentation" -n 5
```

## Monitoring

Access RabbitMQ management interface at http://localhost:15672 (guest/guest) to monitor:
- Queue depth and message processing rates
- Worker connections and performance
- System health and throughput metrics

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RABBITMQ_HOST` | RabbitMQ hostname | `rabbitmq` |
| `DAYS_BACK` | History processing window | `14` |
| `HISTORY_PATH` | Safari history database path | `/app/data/History.db` |
| `OLLAMA_URL` | Local LLM API endpoint | `http://host.docker.internal:11434/api/generate` |

### Scaling Workers

```bash
# Scale to N workers for increased throughput
docker-compose up --scale worker=5

# Monitor processing with logs
docker-compose logs -f worker
```

## Usage Examples

### Basic Search
```bash
python frontend/search_cli.py "Python tutorials"
```

### Advanced Search
```bash
# Limit results
python frontend/search_cli.py "Docker containers" -n 3

# Custom database path
python frontend/search_cli.py "AI research" --db-path custom/summaries.db
```

## Project Structure

```
├── backend/
│   ├── ingester.py          # Safari history reader
│   ├── publisher.py         # RabbitMQ message publisher
│   ├── worker.py           # Distributed processing worker
│   ├── scraper.py          # Web content extraction
│   ├── summarizer.py       # LLM integration
│   └── setup_db.py         # Database initialization
├── frontend/
│   └── search_cli.py       # Interactive search interface
├── data/                   # Shared data volume
├── docker-compose.yml      # Service orchestration
├── Dockerfile             # Container definition
└── requirements.txt       # Python dependencies
```

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run components individually
python backend/ingester.py
python backend/worker.py
```

### Adding New Features

1. **Custom Scrapers**: Extend `scraper.py` for specialized content extraction
2. **Alternative LLMs**: Modify `summarizer.py` for different AI models  
3. **Web Interface**: Add Flask/FastAPI frontend in `frontend/` directory
4. **Database Backends**: Replace SQLite with PostgreSQL for production scale

## Troubleshooting

### Common Issues

**Workers not processing messages:**
```bash
# Check RabbitMQ health
docker-compose logs rabbitmq

# Verify queue status
curl -u guest:guest http://localhost:15672/api/queues
```

**Ollama connection errors:**
```bash
# Ensure Ollama is running
ollama list
curl http://localhost:11434/api/generate
```

**Timestamp display issues:**
- Ensure WebKit timestamp conversion is applied in worker.py
- Existing data may need reprocessing for correct dates

## Performance

- **Throughput**: ~50-100 URLs/minute per worker (depends on content complexity)
- **Scalability**: Tested with up to 10 concurrent workers
- **Memory**: ~200MB per worker container
- **Storage**: ~1KB per processed URL summary

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
