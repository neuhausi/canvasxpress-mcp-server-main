#!/usr/bin/env python3
"""
MCP HTTP Client Example

This demonstrates calling a FastMCP server over HTTP (network).
Unlike examples_usage.py which directly imports the Python package,
this uses the MCP protocol over HTTP/SSE to call a remote server.

Requirements:
    pip install httpx

Usage:
    # 1. Start the MCP server in HTTP mode:
    make run-http
    
    # 2. Run this client:
    python mcp_http_client.py
"""

import asyncio
import httpx
import json
import uuid


async def send_mcp_request(client, url, session_id, method, params=None):
    """Send an MCP JSON-RPC request and parse SSE response"""
    
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
    
    if response.status_code == 200:
        # Parse SSE format response
        if 'text/event-stream' in response.headers.get('content-type', ''):
            # Extract JSON from SSE data field
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    json_str = line[6:]  # Remove "data: " prefix
                    return json.loads(json_str)
        else:
            return response.json()
    
    return None


async def call_mcp_http_server():
    """Connect to MCP server over HTTP and generate charts"""
    
    # MCP server URL (change if deployed remotely)
    server_url = "http://localhost:8000/mcp"
    
    print("=" * 60)
    print("MCP HTTP Client Example")
    print("=" * 60)
    print(f"📡 Connecting to: {server_url}\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Get session ID
            response = await client.get(server_url, headers={"Accept": "application/json"})
            session_id = response.headers.get("mcp-session-id")
            
            if not session_id:
                print("❌ Failed to get session ID")
                return
            
            # Step 2: Initialize MCP session
            init_result = await send_mcp_request(
                client, server_url, session_id,
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "canvasxpress-http-client",
                        "version": "1.0.0"
                    }
                }
            )
            
            if not init_result:
                print("❌ Failed to initialize MCP session")
                return
            
            print("✅ Connected to MCP server\n")
            
            # Step 3: Send initialized notification
            notification_payload = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            headers = {
                "Content-Type": "application/json",
                "mcp-session-id": session_id,
            }
            await client.post(server_url, json=notification_payload, headers=headers)
            
            # Step 4: List available tools
            tools_result = await send_mcp_request(
                client, server_url, session_id,
                method="tools/list"
            )
            
            if tools_result and "result" in tools_result:
                tools = tools_result["result"].get("tools", [])
                print(f"🔧 Available tools: {len(tools)}")
                for tool in tools:
                    print(f"   - {tool['name']}")
                print()
            
            # Example 1: Bar chart
            print("🎨 Example 1: Generating bar chart...")
            print("-" * 60)
            
            result = await send_mcp_request(
                client, server_url, session_id,
                method="tools/call",
                params={
                    "name": "generate_canvasxpress_config",
                    "arguments": {
                        "description": "Create a bar chart with blue bars and legend on the right",
                        "headers": "Region, Sales, Profit",
                        "temperature": 0.0
                    }
                }
            )
            
            if result and "result" in result:
                print("\n📊 Result:")
                print("=" * 60)
                for content in result["result"]["content"]:
                    if "text" in content:
                        print(content["text"])
                print("=" * 60)
            
            # Example 2: Scatter plot
            print("\n\n🎨 Example 2: Generating scatter plot...")
            print("-" * 60)
            
            result2 = await send_mcp_request(
                client, server_url, session_id,
                method="tools/call",
                params={
                    "name": "generate_canvasxpress_config",
                    "arguments": {
                        "description": "Scatter plot with red points, x-axis is time, y-axis is expression",
                        "headers": "Time, Expression, Gene"
                    }
                }
            )
            
            if result2 and "result" in result2:
                print("\n📊 Result:")
                print("=" * 60)
                for content in result2["result"]["content"]:
                    if "text" in content:
                        print(content["text"])
                print("=" * 60)
            
            # Example 3: Heatmap
            print("\n\n🎨 Example 3: Generating heatmap...")
            print("-" * 60)
            
            result3 = await send_mcp_request(
                client, server_url, session_id,
                method="tools/call",
                params={
                    "name": "generate_canvasxpress_config",
                    "arguments": {
                        "description": "Heatmap with clustering and dendrograms on both axes",
                        "headers": "Gene1, Gene2, Gene3, Sample"
                    }
                }
            )
            
            if result3 and "result" in result3:
                print("\n📊 Result:")
                print("=" * 60)
                for content in result3["result"]["content"]:
                    if "text" in content:
                        print(content["text"])
                print("=" * 60)
                
    except ConnectionRefusedError:
        print(f"❌ Error: Cannot connect to {server_url}")
        print("\n💡 Make sure the MCP server is running:")
        print("   make run-http")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run examples"""
    
    print("🚀 FastMCP HTTP Client Examples")
    print("=" * 60)
    print()
    print("This demonstrates calling an MCP server over HTTP/network,")
    print("unlike examples_usage.py which directly imports the Python library.")
    print()
    
    # Run local HTTP example
    asyncio.run(call_mcp_http_server())
    
    print("\n" + "=" * 60)
    print("✅ HTTP client examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
