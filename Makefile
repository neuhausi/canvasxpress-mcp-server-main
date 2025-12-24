.PHONY: help build run stop clean init shell logs test-db test-shell run-http run-httpi test-http venv venv-light venv-onnx init-local run-local run-locali clean-local generate-alt-wordings

# Docker image name
IMAGE_NAME = canvasxpress-mcp-server:latest

# Python virtual environment (requires Python 3.10+, FastMCP requirement)
# Auto-detect Python: try python3.12, python3.11, python3.10, python3 in order
# Override by setting PYTHON_BIN environment variable or editing this line
PYTHON_BIN ?= $(shell command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3.10 2>/dev/null || command -v python3 2>/dev/null || echo python3)
VENV = ./venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

help:
	@echo "CanvasXpress MCP Server - Makefile"
	@echo ""
	@echo "=== Docker Workflow ==="
	@echo "  build      - Build Docker image"
	@echo "  init       - Initialize vector database (Docker)"
	@echo "  run-http   - Run MCP server (HTTP mode, daemon)"
	@echo "  run-httpi  - Run MCP server (HTTP mode, interactive)"
	@echo "  run        - Run MCP server (STDIO mode)"
	@echo "  stop       - Stop running container"
	@echo "  logs       - Show container logs"
	@echo "  shell      - Open shell in running container"
	@echo "  clean      - Remove container and image"
	@echo ""
	@echo "=== Local Virtual Environment Workflow ==="
	@echo "  venv        - Create virtual environment & install ALL deps (~8GB)"
	@echo "  venv-onnx   - Create venv with ONNX embeddings (~500MB, no PyTorch) ⭐"
	@echo "  venv-light  - Create venv with cloud embeddings only (~500MB)"
	@echo "  init-local  - Initialize vector database (local)"
	@echo "  run-local   - Run MCP server locally (HTTP mode, foreground)"
	@echo "  run-locali  - Run MCP server locally (STDIO mode)"
	@echo "  clean-local - Remove venv and local vector_db"
	@echo ""
	@echo "=== Utilities ==="
	@echo "  generate-alt-wordings - Generate alternative wordings for few-shot examples"
	@echo ""
	@echo "=== Testing ==="
	@echo "  test-db    - Test vector database"
	@echo "  test-shell - Interactive shell with database"
	@echo "  test-http  - Test HTTP server (Docker)"
	@echo ""
	@echo "=== First Time Setup (Docker) ==="
	@echo "  1. cp .env.example .env && edit .env"
	@echo "  2. make build"
	@echo "  3. make init"
	@echo "  4. make run-http"
	@echo ""
	@echo "=== First Time Setup (Local) ==="
	@echo "  1. cp .env.example .env && edit .env"
	@echo "  2. make venv          (full, ~8GB for local BGE-M3 embeddings)"
	@echo "     OR make venv-onnx  (lightweight, ~500MB ONNX embeddings) ⭐"
	@echo "     OR make venv-light (lightweight, cloud embeddings)"
	@echo "  3. make init-local"
	@echo "  4. make run-local"

build:
	@echo "🔨 Building Docker image..."
	docker build -t canvasxpress-mcp-server:latest .
	@echo "✅ Build complete!"

init:
	@echo "🔧 Initializing vector database..."
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	docker run --rm \
		--env-file .env \
		-v $(PWD)/vector_db:/root/.cache \
		canvasxpress-mcp-server:latest \
		python -c "from src.canvasxpress_generator import CanvasXpressGenerator; CanvasXpressGenerator(); print('✅ Vector database initialized!')"
	@echo "✅ Initialization complete!"

run:
	@echo "🚀 Starting MCP server..."
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d vector_db ]; then \
		echo "❌ Error: vector_db directory not found. Run 'make init' first!"; \
		exit 1; \
	fi
	docker run -it --rm \
		-v $(PWD)/vector_db:/root/.cache \
		--env-file .env \
		$(IMAGE_NAME) \
		python -m src.mcp_server

run-http:
	@echo "🌐 Starting MCP Server (HTTP mode, daemon)..."
	@echo "📡 Accessible at: http://localhost:8000/mcp"
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d vector_db ]; then \
		echo "❌ Error: vector_db directory not found. Run 'make init' first!"; \
		exit 1; \
	fi
	docker run -d \
		--name canvasxpress-mcp-server \
		-p 8000:8000 \
		-v $(PWD)/vector_db:/root/.cache \
		--env-file .env \
		-e MCP_TRANSPORT=http \
		$(IMAGE_NAME) \
		python -m src.mcp_server --http
	@echo "✅ Server started in background!"
	@echo "   Use 'make logs' to view logs"
	@echo "   Use 'make stop' to stop the server"

run-httpi:
	@echo "🌐 Starting MCP Server (HTTP mode, interactive)..."
	@echo "📡 Accessible at: http://localhost:8000/mcp"
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d vector_db ]; then \
		echo "❌ Error: vector_db directory not found. Run 'make init' first!"; \
		exit 1; \
	fi
	docker run -it --rm \
		-p 8000:8000 \
		-v $(PWD)/vector_db:/root/.cache \
		--env-file .env \
		-e MCP_TRANSPORT=http \
		$(IMAGE_NAME) \
		python -m src.mcp_server --http

stop:
	@echo "🛑 Stopping MCP server..."
	docker stop canvasxpress-mcp-server || true
	docker rm canvasxpress-mcp-server || true
	@echo "✅ Server stopped!"

clean: stop
	@echo "🧹 Cleaning up..."
	docker rmi canvasxpress-mcp-server:latest || true
	@echo "✅ Cleanup complete!"

shell:
	@echo "🐚 Opening shell in container..."
	docker exec -it canvasxpress-mcp-server bash

logs:
	@echo "📋 Showing container logs (Ctrl+C to exit)..."
	docker logs -f canvasxpress-mcp-server

test-db:
	@echo "🧪 Testing vector database..."
	@if [ ! -d vector_db ]; then \
		echo "❌ Error: vector_db directory not found. Run 'make init' first!"; \
		exit 1; \
	fi
	docker run --rm \
		-v $(PWD)/vector_db:/root/.cache \
		canvasxpress-mcp-server:latest \
		python /app/test_vector_db.py

test-shell:
	@echo "🐚 Starting interactive test shell..."
	@echo "📁 Vector database mounted at: /root/.cache/"
	@echo "📝 Example scripts available: /app/examples_usage.py"
	@echo ""
	@if [ ! -d vector_db ]; then \
		echo "⚠️  Warning: vector_db directory not found."; \
		echo "   Run 'make init' first to create the database."; \
		echo ""; \
	fi
	@if [ ! -f .env ]; then \
		echo "⚠️  Warning: .env file not found."; \
		echo "   Environment variables not loaded."; \
		echo ""; \
	fi
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/vector_db:/root/.cache \
		canvasxpress-mcp-server:latest \
		/bin/bash

test-http:
	@echo "🧪 Testing HTTP MCP Server..."
	@echo "📡 Connecting to: http://localhost:8000/mcp"
	@echo ""
	@CONTAINER_ID=$$(docker ps -q --filter ancestor=canvasxpress-mcp-server:latest); \
	if [ -z "$$CONTAINER_ID" ]; then \
		echo "❌ Error: No running container found!"; \
		echo ""; \
		echo "Please start the HTTP server first:"; \
		echo "  make run-http"; \
		echo ""; \
		echo "Then in another terminal, run:"; \
		echo "  make test-http"; \
		exit 1; \
	fi; \
	echo "📦 Installing mcp package in container..."; \
	docker exec $$CONTAINER_ID pip install -q mcp; \
	echo "🚀 Running HTTP client test..."; \
	echo ""; \
	docker exec $$CONTAINER_ID python /app/mcp_http_client.py

# =============================================================================
# Local Virtual Environment Targets
# =============================================================================

venv:
	@echo "🐍 Creating virtual environment with $(PYTHON_BIN)..."
	@$(PYTHON_BIN) --version || (echo "❌ Error: $(PYTHON_BIN) not found. Install Python 3.10+ or set PYTHON_BIN=<path-to-python>"; exit 1)
	@$(PYTHON_BIN) -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || (echo "❌ Error: Python 3.10+ required. Found: $$($(PYTHON_BIN) --version)"; exit 1)
	$(PYTHON_BIN) -m venv $(VENV)
	@echo "📦 Installing ALL dependencies (includes PyTorch ~2GB for local embeddings)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "✅ Virtual environment created!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. make init-local  (initialize vector DB)"
	@echo "  2. make run-local   (start server)"

venv-light:
	@echo "🐍 Creating LIGHTWEIGHT virtual environment with $(PYTHON_BIN)..."
	@echo "   (No PyTorch - uses cloud embeddings via Gemini or OpenAI API)"
	@$(PYTHON_BIN) --version || (echo "❌ Error: $(PYTHON_BIN) not found. Install Python 3.10+ or set PYTHON_BIN=<path-to-python>"; exit 1)
	@$(PYTHON_BIN) -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || (echo "❌ Error: Python 3.10+ required. Found: $$($(PYTHON_BIN) --version)"; exit 1)
	$(PYTHON_BIN) -m venv $(VENV)
	@echo "📦 Installing lightweight dependencies (~500MB vs ~8GB)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-light.txt
	@echo ""
	@echo "✅ Lightweight virtual environment created!"
	@echo ""
	@echo "⚠️  IMPORTANT: You MUST configure cloud embeddings in .env:"
	@echo "     EMBEDDING_PROVIDER=gemini   (or openai)"
	@echo "     GOOGLE_API_KEY=your-key     (or AZURE_OPENAI_KEY)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env and set EMBEDDING_PROVIDER=gemini"
	@echo "  2. make init-local  (initialize vector DB)"
	@echo "  3. make run-local   (start server)"

venv-onnx:
	@echo "🐍 Creating ONNX virtual environment with $(PYTHON_BIN)..."
	@echo "   (Lightweight local embeddings - ~1GB RAM vs ~3-4GB for BGE-M3)"
	@$(PYTHON_BIN) --version || (echo "❌ Error: $(PYTHON_BIN) not found. Install Python 3.10+ or set PYTHON_BIN=<path-to-python>"; exit 1)
	@$(PYTHON_BIN) -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || (echo "❌ Error: Python 3.10+ required. Found: $$($(PYTHON_BIN) --version)"; exit 1)
	$(PYTHON_BIN) -m venv $(VENV)
	@echo "📦 Installing ONNX dependencies (~500MB vs ~8GB for full)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-light.txt
	$(PIP) install sentence-transformers onnxruntime
	@echo ""
	@echo "✅ ONNX virtual environment created!"
	@echo ""
	@echo "📋 Configure ONNX embeddings in .env:"
	@echo "     EMBEDDING_PROVIDER=onnx"
	@echo "     ONNX_EMBEDDING_MODEL=all-MiniLM-L6-v2  (default, fast)"
	@echo ""
	@echo "   Other model options:"
	@echo "     all-mpnet-base-v2              (768d, best quality)"
	@echo "     BAAI/bge-small-en-v1.5         (384d, BGE family)"
	@echo "     nomic-ai/nomic-embed-text-v1.5 (768d, long context)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env and set EMBEDDING_PROVIDER=onnx"
	@echo "  2. make init-local  (initialize vector DB)"
	@echo "  3. make run-local   (start server)"

init-local:
	@echo "🔧 Initializing vector database (local)..."
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d $(VENV) ]; then \
		echo "❌ Error: Virtual environment not found. Run 'make venv' first!"; \
		exit 1; \
	fi
	$(PYTHON) scripts/init_vector_db.py

run-local:
	@echo "🌐 Starting MCP Server locally (HTTP mode)..."
	@echo "📡 Accessible at: http://localhost:8000/mcp"
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d vector_db ]; then \
		echo "❌ Error: vector_db directory not found. Run 'make init-local' first!"; \
		exit 1; \
	fi
	@if [ ! -d $(VENV) ]; then \
		echo "❌ Error: Virtual environment not found. Run 'make venv' first!"; \
		exit 1; \
	fi
	$(PYTHON) -m src.mcp_server --http

run-locali:
	@echo "📋 Starting MCP Server locally (STDIO mode)..."
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d vector_db ]; then \
		echo "❌ Error: vector_db directory not found. Run 'make init-local' first!"; \
		exit 1; \
	fi
	@if [ ! -d $(VENV) ]; then \
		echo "❌ Error: Virtual environment not found. Run 'make venv' first!"; \
		exit 1; \
	fi
	$(PYTHON) -m src.mcp_server

clean-local:
	@echo "🧹 Cleaning local environment..."
	rm -rf $(VENV)
	rm -rf vector_db/canvasxpress_mcp.db
	@echo "✅ Local cleanup complete!"

generate-alt-wordings:
	@echo "🔧 Generating alternative wordings for few-shot examples..."
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Copy .env.example to .env first!"; \
		exit 1; \
	fi
	@if [ ! -d $(VENV) ]; then \
		echo "❌ Error: Virtual environment not found. Run 'make venv' or 'make venv-light' first!"; \
		exit 1; \
	fi
	$(PYTHON) scripts/generate_alt_wordings.py
	@echo ""
	@echo "⚠️  Remember to re-initialize the vector database after generating new wordings:"
	@echo "   rm -rf vector_db/"
	@echo "   make init-local"