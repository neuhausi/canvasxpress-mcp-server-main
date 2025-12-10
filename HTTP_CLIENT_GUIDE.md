# HTTP MCP Client Guide

Complete guide for connecting to the CanvasXpress MCP server over HTTP/network.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Protocol Details](#protocol-details)
4. [Client Implementation](#client-implementation)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The CanvasXpress MCP server exposes a **Model Context Protocol (MCP)** interface over HTTP using Server-Sent Events (SSE). This allows remote clients to generate CanvasXpress chart configurations from natural language descriptions.

**Key Features:**
- 🌐 **Network Accessible**: Connect from any machine on the network
- 🔐 **Session-based**: Each client gets a unique session ID
- 📡 **SSE Transport**: Server-Sent Events for real-time responses
- 🎨 **132 Examples**: RAG system with 66 chart types (132 total examples)
- 🤖 **AI-Powered**: BMS Azure OpenAI (gpt-4o-global) with 93% accuracy

---

## Quick Start

### 1. Start the HTTP Server

```bash
# From the project directory
make run-http

# Or manually:
docker run -it --rm \
  -p 8000:8000 \
  -v $(PWD)/vector_db:/root/.cache \
  --env-file .env \
  -e MCP_TRANSPORT=http \
  canvasxpress-mcp-server:latest \
  python -m src.mcp_server --http
```

Server will be accessible at: **http://localhost:8000/mcp**

### 2. Run the Example Client

```bash
# Inside the Docker container:
python3 mcp_http_client.py

# Or from host (if Python 3.10+ and httpx installed):
python3 mcp_http_client.py
```

### 3. Expected Output

```
🚀 FastMCP HTTP Client Examples
============================================================

📡 Connecting to: http://localhost:8000/mcp

✅ Connected to MCP server

🔧 Available tools: 1
   - generate_canvasxpress_config

🎨 Example 1: Generating bar chart...
------------------------------------------------------------

📊 Result:
============================================================
✅ **CanvasXpress Configuration Generated**

**Description:** Create a bar chart with blue bars and legend on the right

**Configuration:**
```json
{
  "graphType": "Bar",
  "colors": ["blue"],
  "legendPosition": "right"
}
```
...
```

---

## Protocol Details

### MCP over HTTP/SSE

The CanvasXpress MCP server uses the **MCP (Model Context Protocol)** specification with HTTP and Server-Sent Events (SSE) as the transport layer.

#### 1. Session Management

**Get Session ID:**
```http
GET /mcp HTTP/1.1
Accept: application/json
```

**Response Headers:**
```
mcp-session-id: <uuid>
```

The server returns a unique session ID in the response headers. This ID must be included in all subsequent requests.

#### 2. Request Format

**Send MCP Request:**
```http
POST /mcp HTTP/1.1
Content-Type: application/json
mcp-session-id: <session-id>
Accept: application/json, text/event-stream

{
  "jsonrpc": "2.0",
  "id": "<request-id>",
  "method": "<method-name>",
  "params": { ... }
}
```

#### 3. Response Format (SSE)

Responses are sent as Server-Sent Events:

```
event: message
data: {"jsonrpc":"2.0","id":"<request-id>","result":{...}}
```

The JSON-RPC response is embedded in the SSE `data:` field.

### MCP Methods

#### `initialize`

Initialize the MCP session. **Must be called first.**

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {"listChanged": true},
      "sampling": {}
    },
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "experimental": {},
      "prompts": {"listChanged": true},
      "resources": {"subscribe": true, "listChanged": true},
      "tools": {"listChanged": true}
    },
    "serverInfo": {
      "name": "CanvasXpress Chart Generator 🎨",
      "version": "2.13.0.2"
    }
  }
}
```

#### `notifications/initialized`

Notify server that client is ready. **Must be called after initialize.**

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

No response expected (notification).

#### `tools/list`

List available tools.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "result": {
    "tools": [
      {
        "name": "generate_canvasxpress_config",
        "description": "Generate CanvasXpress visualization configuration...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "description": {"type": "string"},
            "headers": {"type": "string"},
            "temperature": {"type": "number"}
          },
          "required": ["description"]
        }
      }
    ]
  }
}
```

#### `tools/call`

Call a tool to generate a CanvasXpress configuration.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "generate_canvasxpress_config",
    "arguments": {
      "description": "Create a bar chart with blue bars",
      "headers": "Region, Sales, Profit",
      "temperature": 0.0
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ **CanvasXpress Configuration Generated**\n\n**Description:** Create a bar chart with blue bars\n\n**Configuration:**\n```json\n{\n  \"graphType\": \"Bar\",\n  \"colors\": [\"blue\"]\n}\n```\n..."
      }
    ]
  }
}
```

---

## Client Implementation

### Python Example

See `mcp_http_client.py` for a complete working example.

**Key Functions:**

```python
import httpx
import json
import uuid

async def send_mcp_request(client, url, session_id, method, params=None):
    """Send MCP request and parse SSE response"""
    
    request_id = str(uuid.uuid4())
    
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params:
        payload["params"] = params
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-session-id": session_id,
    }
    
    response = await client.post(url, json=payload, headers=headers)
    
    # Parse SSE response
    if 'text/event-stream' in response.headers.get('content-type', ''):
        for line in response.text.split('\n'):
            if line.startswith('data: '):
                return json.loads(line[6:])  # Remove "data: " prefix
    
    return response.json()
```

**Full Workflow:**

```python
async with httpx.AsyncClient(timeout=60.0) as client:
    # 1. Get session ID
    response = await client.get(url, headers={"Accept": "application/json"})
    session_id = response.headers.get("mcp-session-id")
    
    # 2. Initialize
    await send_mcp_request(
        client, url, session_id,
        method="initialize",
        params={
            "protocolVersion": "2024-11-05",
            "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
            "clientInfo": {"name": "my-client", "version": "1.0.0"}
        }
    )
    
    # 3. Send initialized notification
    await client.post(url, 
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers={"Content-Type": "application/json", "mcp-session-id": session_id}
    )
    
    # 4. Call tool
    result = await send_mcp_request(
        client, url, session_id,
        method="tools/call",
        params={
            "name": "generate_canvasxpress_config",
            "arguments": {
                "description": "Create a bar chart with blue bars",
                "temperature": 0.0
            }
        }
    )
    
    # 5. Extract result
    config_text = result["result"]["content"][0]["text"]
    print(config_text)
```

### JavaScript/TypeScript Example

```typescript
import fetch from 'node-fetch';

async function callMCPServer() {
  const url = 'http://localhost:8000/mcp';
  
  // 1. Get session ID
  const initResp = await fetch(url, {
    headers: { 'Accept': 'application/json' }
  });
  const sessionId = initResp.headers.get('mcp-session-id');
  
  // 2. Initialize session
  const initializeResp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'mcp-session-id': sessionId,
      'Accept': 'application/json, text/event-stream'
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: crypto.randomUUID(),
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: { roots: { listChanged: true }, sampling: {} },
        clientInfo: { name: 'js-client', version: '1.0.0' }
      }
    })
  });
  
  // Parse SSE response
  const text = await initializeResp.text();
  const data = text.split('\n').find(l => l.startsWith('data: '));
  const result = JSON.parse(data.substring(6));
  
  // 3. Send initialized notification
  await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'mcp-session-id': sessionId
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'notifications/initialized'
    })
  });
  
  // 4. Call tool
  const callResp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'mcp-session-id': sessionId,
      'Accept': 'application/json, text/event-stream'
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: crypto.randomUUID(),
      method: 'tools/call',
      params: {
        name: 'generate_canvasxpress_config',
        arguments: {
          description: 'Create a bar chart with blue bars',
          temperature: 0.0
        }
      }
    })
  });
  
  const callText = await callResp.text();
  const callData = callText.split('\n').find(l => l.startsWith('data: '));
  const callResult = JSON.parse(callData.substring(6));
  
  console.log(callResult.result.content[0].text);
}
```

### cURL Examples

```bash
# 1. Get session ID
SESSION_ID=$(curl -s -i http://localhost:8000/mcp \
  -H "Accept: application/json" \
  | grep -i "mcp-session-id:" \
  | cut -d: -f2 \
  | tr -d ' \r')

echo "Session ID: $SESSION_ID"

# 2. Initialize
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {"roots": {"listChanged": true}, "sampling": {}},
      "clientInfo": {"name": "curl-client", "version": "1.0.0"}
    }
  }'

# 3. Send initialized notification
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'

# 4. Call tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: $SESSION_ID" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "generate_canvasxpress_config",
      "arguments": {
        "description": "Create a bar chart with blue bars",
        "temperature": 0.0
      }
    }
  }'
```

---

## Examples

### Example 1: Simple Bar Chart

**Request:**
```json
{
  "description": "Create a bar chart with blue bars"
}
```

**Response:**
```json
{
  "graphType": "Bar",
  "colors": ["blue"]
}
```

### Example 2: Scatter Plot with Customization

**Request:**
```json
{
  "description": "Scatter plot with red points, x-axis is time, y-axis is expression, add regression line",
  "headers": "Time, Expression, Gene"
}
```

**Response:**
```json
{
  "graphType": "Scatter2D",
  "colors": ["red"],
  "xAxis": ["Time"],
  "yAxis": ["Expression"],
  "decorations": {
    "line": [{"type": "regression"}]
  }
}
```

### Example 3: Heatmap with Clustering

**Request:**
```json
{
  "description": "Heatmap with clustering and dendrograms on both axes, use blue-red color scheme",
  "headers": "Gene1, Gene2, Gene3, Sample"
}
```

**Response:**
```json
{
  "graphType": "Heatmap",
  "colorScheme": "BlueRed",
  "smpDendrogramPosition": "top",
  "varDendrogramPosition": "left",
  "smpClustering": true,
  "varClustering": true
}
```

### Example 4: Box Plot with Groups

**Request:**
```json
{
  "description": "Box plot grouped by treatment, show outliers, use pastel colors",
  "headers": "Treatment, Value, Patient"
}
```

**Response:**
```json
{
  "graphType": "Boxplot",
  "groupingFactors": ["Treatment"],
  "showOutliers": true,
  "colorScheme": "Pastel"
}
```

---

## Troubleshooting

### Connection Refused

**Error:**
```
ConnectionRefusedError: Cannot connect to http://localhost:8000/mcp
```

**Solution:**
- Ensure the HTTP MCP server is running: `make run-http`
- Check that port 8000 is exposed: `docker ps` should show `0.0.0.0:8000->8000/tcp`
- Verify firewall settings if connecting from remote machine

### Missing Session ID

**Error:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Bad Request: Missing session ID"
  }
}
```

**Solution:**
- Always get the session ID first with a GET request
- Include `mcp-session-id` header in all subsequent POST requests

### Invalid JSON in Response

**Error:**
```
json.decoder.JSONDecodeError: Expecting value
```

**Solution:**
- The response is in SSE format, not plain JSON
- Parse the `data:` field from SSE events
- See client implementation examples above

### Tool Call Failed

**Error:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error"
  }
}
```

**Solution:**
- Check server logs: `docker logs <container-id>`
- Verify BMS Azure OpenAI credentials in `.env`
- Ensure vector database is initialized: `make init`
- Check description is clear and specific

### Timeout

**Error:**
```
asyncio.exceptions.TimeoutError
```

**Solution:**
- LLM generation can take 5-30 seconds
- Increase client timeout to 60+ seconds
- Check server is responding: `curl http://localhost:8000/mcp`

---

## Advanced Usage

### Remote Deployment

To connect to a remotely deployed MCP server:

```python
# Change server URL
server_url = "https://your-domain.com/mcp"

# Add authentication if required
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json",
    "mcp-session-id": session_id
}
```

### Batch Processing

Generate multiple charts in one session:

```python
async with httpx.AsyncClient(timeout=60.0) as client:
    # Initialize once
    session_id = await get_session_id(client, url)
    await initialize_session(client, url, session_id)
    
    # Generate multiple charts
    descriptions = [
        "bar chart with sales data",
        "line chart showing trends over time",
        "heatmap with gene expression"
    ]
    
    for desc in descriptions:
        result = await send_mcp_request(
            client, url, session_id,
            method="tools/call",
            params={
                "name": "generate_canvasxpress_config",
                "arguments": {"description": desc}
            }
        )
        # Process result...
```

### Error Handling

```python
try:
    result = await send_mcp_request(...)
    
    if "error" in result:
        error = result["error"]
        print(f"MCP Error {error['code']}: {error['message']}")
    elif "result" in result:
        # Success
        config = result["result"]["content"][0]["text"]
        
except httpx.TimeoutException:
    print("Request timed out")
except httpx.ConnectError:
    print("Cannot connect to server")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Resources

- **MCP Specification**: https://modelcontextprotocol.io/
- **FastMCP Documentation**: https://gofastmcp.com/
- **CanvasXpress Docs**: https://www.canvasxpress.org/
- **Server Code**: `src/mcp_server.py`
- **Example Client**: `mcp_http_client.py`
- **Test Client**: `test_mcp_protocol.py`
