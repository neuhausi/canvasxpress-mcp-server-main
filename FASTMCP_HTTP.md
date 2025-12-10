# FastMCP HTTP Deployment Guide

## Overview

**I was wrong earlier!** FastMCP 2.0+ **DOES support HTTP deployment** for network access. Your MCP server can be accessed remotely over the internet.

Source: https://gofastmcp.com/deployment/http

---

## Two Transport Modes

FastMCP supports both local and network access:

### 1. STDIO Transport (Local Only)
- For Claude Desktop integration
- Same-machine access only
- Communication via stdin/stdout

### 2. HTTP Transport (Network Access) ⭐
- **Accessible over the internet**
- Multiple simultaneous clients
- RESTful MCP protocol via HTTP
- Perfect for remote/cloud deployments

---

## HTTP Deployment Options

### Option 1: Direct HTTP Server (Simplest)

Your MCP server with built-in HTTP support:

```python
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool
def process_data(input: str) -> str:
    return f"Processed: {input}"

if __name__ == "__main__":
    # Start HTTP server on 0.0.0.0:8000
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Access at:** `http://your-server:8000/mcp`

### Option 2: ASGI Application (Production)

For use with Uvicorn/Gunicorn with multiple workers:

```python
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool
def process_data(input: str) -> str:
    return f"Processed: {input}"

# Create ASGI app
app = mcp.http_app()
```

Run with:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Updated CanvasXpress MCP Server

Our server now supports **both modes**:

### STDIO Mode (Default) - For Claude Desktop

```bash
# Start in STDIO mode
python -m src.mcp_server

# Or via Docker
make run
```

### HTTP Mode - For Network Access

```bash
# Start in HTTP mode
python -m src.mcp_server --http

# Or via Docker with HTTP
docker run -p 8000:8000 \
  -v $(pwd)/vector_db:/root/.cache \
  --env-file .env \
  -e MCP_TRANSPORT=http \
  canvasxpress-mcp-server \
  python -m src.mcp_server --http
```

**Access at:** `http://localhost:8000/mcp`

---

## Network Deployment

### Docker Compose (HTTP Mode)

```yaml
version: '3.8'

services:
  mcp-http:
    build: .
    command: python -m src.mcp_server --http
    ports:
      - "8000:8000"
    volumes:
      - ./vector_db:/root/.cache
    environment:
      # LLM Provider: 'openai' (Azure BMS) or 'gemini'
      - LLM_PROVIDER=openai
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - LLM_MODEL=gpt-4o-global
      - LLM_ENVIRONMENT=nonprod
      # Embedding Provider: 'local' (BGE-M3), 'openai', or 'gemini'
      - EMBEDDING_PROVIDER=local
      # MCP Transport
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
    restart: unless-stopped
```

For cloud embeddings (smaller deployment):
```yaml
    environment:
      # Use cloud providers - no PyTorch required
      - LLM_PROVIDER=gemini
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - EMBEDDING_PROVIDER=gemini
      # MCP Transport
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
```

### Deploy to Cloud

#### AWS ECS/Fargate
```bash
# Build and push to ECR
docker build -t canvasxpress-mcp .
docker tag canvasxpress-mcp:latest <account>.dkr.ecr.us-east-1.amazonaws.com/canvasxpress-mcp:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/canvasxpress-mcp:latest

# Create ECS task with port 8000 exposed
# Add environment: MCP_TRANSPORT=http
```

#### Google Cloud Run
```bash
# With Azure OpenAI:
gcloud run deploy canvasxpress-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=openai,AZURE_OPENAI_KEY=xxx,EMBEDDING_PROVIDER=openai,MCP_TRANSPORT=http,MCP_PORT=8080

# With Gemini (recommended for GCP):
gcloud run deploy canvasxpress-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_PROVIDER=gemini,GEMINI_API_KEY=xxx,EMBEDDING_PROVIDER=gemini,MCP_TRANSPORT=http,MCP_PORT=8080
```

#### Railway / Render
```bash
# Install CLI
curl -fsSL https://railway.app/install.sh | sh

# Deploy (automatically uses Dockerfile)
railway up

# Set environment variables (Azure OpenAI)
railway variables set \
  LLM_PROVIDER=openai \
  AZURE_OPENAI_KEY=xxx \
  EMBEDDING_PROVIDER=openai \
  MCP_TRANSPORT=http \
  MCP_PORT=8000

# Or for Gemini
railway variables set \
  LLM_PROVIDER=gemini \
  GEMINI_API_KEY=xxx \
  EMBEDDING_PROVIDER=gemini \
  MCP_TRANSPORT=http \
  MCP_PORT=8000
```

---

## Authentication (Recommended for Production)

FastMCP supports multiple auth methods:

### Bearer Token Authentication

```python
from fastmcp import FastMCP
from fastmcp.server.auth import BearerTokenAuth

auth = BearerTokenAuth(token=os.environ["MCP_AUTH_TOKEN"])
mcp = FastMCP("Secure Server", auth=auth)

app = mcp.http_app()
```

Clients must include:
```
Authorization: Bearer your-token-here
```

### OAuth (GitHub, Google, etc.)

```python
from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
    base_url="https://your-server.com"
)

mcp = FastMCP("OAuth Server", auth=auth)
app = mcp.http_app()
```

---

## Client Usage

### MCP Client (Python)

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def call_remote_mcp():
    """Connect to remote MCP server over HTTP"""
    
    async with sse_client("http://your-server:8000/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call the tool
            result = await session.call_tool(
                "generate_canvasxpress_config",
                arguments={
                    "description": "bar chart with blue bars",
                    "headers": "Region, Sales"
                }
            )
            
            print(result.content[0].text)

asyncio.run(call_remote_mcp())
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "canvasxpress-remote": {
      "url": "http://your-server.com:8000/mcp",
      "transport": "http"
    }
  }
}
```

### ChatGPT / Web-based AI Assistants

Configure MCP connection:
- Protocol: HTTP
- URL: `http://your-server.com:8000/mcp`
- Authentication: Bearer token (if configured)

---

## Health Checks & Monitoring

### Add Health Endpoint

```python
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "service": "canvasxpress-mcp",
        "examples": 132
    })
```

Access at: `http://your-server:8000/health`

### Production Monitoring

```python
from prometheus_client import Counter, Histogram, make_asgi_app

request_count = Counter('mcp_requests_total', 'Total MCP requests')
request_duration = Histogram('mcp_request_duration_seconds', 'Request duration')

@mcp.tool()
def generate_canvasxpress_config(...):
    request_count.inc()
    with request_duration.time():
        # ... tool logic
        pass

# Expose metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## Load Balancing & Scaling

### nginx Configuration

```nginx
upstream mcp_backend {
    least_conn;
    server mcp1:8000 max_fails=3 fail_timeout=30s;
    server mcp2:8000 max_fails=3 fail_timeout=30s;
    server mcp3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name mcp.yourcompany.com;
    
    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # MCP-specific headers
        proxy_set_header mcp-protocol-version $http_mcp_protocol_version;
        proxy_set_header mcp-session-id $http_mcp_session_id;
    }
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: canvasxpress-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: canvasxpress-mcp
  template:
    metadata:
      labels:
        app: canvasxpress-mcp
    spec:
      containers:
      - name: mcp
        image: your-registry/canvasxpress-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: MCP_TRANSPORT
          value: "http"
        - name: MCP_PORT
          value: "8000"
        - name: AZURE_OPENAI_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: azure-openai-key
---
apiVersion: v1
kind: Service
metadata:
  name: canvasxpress-mcp
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: canvasxpress-mcp
```

---

## Comparison: HTTP vs REST API

| Feature | FastMCP HTTP | Custom REST API |
|---------|-------------|-----------------|
| **MCP Protocol** | ✅ Yes | ❌ No |
| **Claude Desktop** | ✅ Yes | ❌ No |
| **Network Access** | ✅ Yes | ✅ Yes |
| **Tool Discovery** | ✅ Auto | ❌ Manual |
| **Streaming** | ✅ Yes | Manual |
| **Setup Complexity** | Low | Medium |
| **Standard Protocol** | ✅ MCP | Custom |

**Use FastMCP HTTP when:**
- ✅ You want MCP protocol compliance
- ✅ AI assistants need to discover tools automatically
- ✅ You want Claude Desktop / ChatGPT integration
- ✅ You need standardized tool interfaces

**Use Custom REST API when:**
- ✅ You need complete API control
- ✅ Non-AI clients (web/mobile apps)
- ✅ Custom authentication flows
- ✅ Legacy system integration

---

## Summary

### I was wrong! FastMCP HTTP deployment provides:

1. ✅ **Network Access** - Deploy to cloud, accessible over internet
2. ✅ **Multiple Clients** - Concurrent connections from anywhere
3. ✅ **MCP Protocol** - Standard tool discovery and invocation
4. ✅ **AI Assistant Integration** - Works with Claude, ChatGPT, etc.
5. ✅ **Production Ready** - Auth, monitoring, load balancing

### Transport Comparison

| Use Case | STDIO | HTTP |
|----------|-------|------|
| Claude Desktop (local) | ✅ | ❌ |
| Claude Desktop (remote) | ❌ | ✅ |
| Web-based AI (ChatGPT) | ❌ | ✅ |
| Multiple users | ❌ | ✅ |
| Cloud deployment | ❌ | ✅ |
| Local development | ✅ | ✅ |

**Bottom Line**: FastMCP HTTP transport solves the network distribution problem while maintaining MCP protocol compliance. You CAN make your MCP server widely available over the internet!
