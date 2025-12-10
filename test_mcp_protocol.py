#!/usr/bin/env python3
"""
Complete FastMCP HTTP Client with proper MCP protocol flow
"""

import httpx
import asyncio
import json
import uuid


async def send_mcp_request(client, url, session_id, method, params=None):
    """Send an MCP JSON-RPC request via POST"""
    
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
    
    print(f"   📤 Sending: {method}")
    print(f"      Payload: {json.dumps(payload, indent=6)}")
    
    response = await client.post(url, json=payload, headers=headers)
    
    print(f"   📥 Response Status: {response.status_code}")
    print(f"      Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        # Check if response has content
        if len(response.content) == 0:
            print(f"      ⚠️  Empty response body")
            return {"empty": True}
        
        # Check if it's SSE format
        if 'text/event-stream' in response.headers.get('content-type', ''):
            # Parse SSE format: "data: {...}"
            text = response.text
            # Extract JSON from SSE data field
            for line in text.split('\n'):
                if line.startswith('data: '):
                    json_str = line[6:]  # Remove "data: " prefix
                    try:
                        result = json.loads(json_str)
                        print(f"      ✅ Parsed SSE data")
                        return result
                    except json.JSONDecodeError:
                        pass
            print(f"      ⚠️  Could not parse SSE data")
            return {"error": "sse_parse_failed", "content": text}
        
        # Try to parse as regular JSON
        try:
            result = response.json()
            print(f"      ✅ Parsed JSON")
            return result
        except json.JSONDecodeError:
            print(f"      ⚠️  Not JSON. Raw content:")
            print(f"      {response.text[:200]}")
            return {"error": "not_json", "content": response.text}
    else:
        print(f"      Error: {response.text}")
        return None


async def test_mcp_protocol():
    """Test complete MCP protocol flow"""
    
    print("=" * 60)
    print("🎨 Complete MCP Protocol Test")
    print("=" * 60)
    
    url = "http://localhost:8000/mcp"
    
    # Step 1: Get session ID
    print("\n1️⃣ Getting session ID...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, headers={"Accept": "application/json"})
        session_id = response.headers.get("mcp-session-id")
        print(f"   ✅ Session ID: {session_id}\n")
        
        # Step 2: Initialize MCP session
        print("2️⃣ Initializing MCP session...")
        init_result = await send_mcp_request(
            client, url, session_id,
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        )
        
        if not init_result:
            print("   ❌ Initialization failed!")
            return
        
        print()
        
        # Step 3: Send initialized notification
        print("3️⃣ Sending initialized notification...")
        notification_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        headers = {
            "Content-Type": "application/json",
            "mcp-session-id": session_id,
        }
        await client.post(url, json=notification_payload, headers=headers)
        print("   ✅ Sent\n")
        
        # Step 4: List tools
        print("4️⃣ Listing available tools...")
        tools_result = await send_mcp_request(
            client, url, session_id,
            method="tools/list"
        )
        
        if tools_result and "result" in tools_result:
            tools = tools_result["result"].get("tools", [])
            print(f"\n   ✅ Found {len(tools)} tool(s):")
            for tool in tools:
                print(f"      - {tool['name']}: {tool.get('description', '')[:60]}...")
        
        print()
        
        # Step 5: Call the tool
        print("5️⃣ Calling generate_canvasxpress_config tool...")
        call_result = await send_mcp_request(
            client, url, session_id,
            method="tools/call",
            params={
                "name": "generate_canvasxpress_config",
                "arguments": {
                    "description": "Create a simple bar chart with blue bars",
                    "temperature": 0.0
                }
            }
        )
        
        if call_result and "result" in call_result:
            print("\n   ✅ Tool call successful!")
            print("\n   📊 Response:")
            print("   " + "=" * 56)
            
            result = call_result["result"]
            if "content" in result:
                for content in result["content"]:
                    if "text" in content:
                        # Print first 500 chars
                        text = content["text"]
                        print(text[:500])
                        if len(text) > 500:
                            print("\n   ... (truncated)")
            
            print("   " + "=" * 56)
        
        print("\n" + "=" * 60)
        print("✅ MCP Protocol Test Complete!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())
