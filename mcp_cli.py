#!/usr/bin/env python3
"""
CanvasXpress MCP CLI Client

Command-line client for the CanvasXpress HTTP MCP Server.
Sends queries to the running MCP server and displays the results.

Usage:
    python3 mcp_cli.py -q "Generate a bar graph with title 'hello, world'"
    python3 mcp_cli.py --query "Create a scatter plot" --headers "Time,Expression"
    python3 mcp_cli.py -q "Heatmap with clustering" --temperature 0.5 --url http://localhost:8000

Output modes:
    (default)     Pretty formatted output with usage instructions
    --json        Full JSON response: {success, description, headers, config, error}
    --config-only Just the CanvasXpress config JSON (for piping to other tools)

Examples:
    # Basic bar chart (pretty output)
    python3 mcp_cli.py -q "Generate a bar graph with title 'hello, world'"
    
    # Scatter plot with headers
    python3 mcp_cli.py -q "Scatter plot of gene expression over time" --headers "Time,Expression,Gene"
    
    # Heatmap with temperature
    python3 mcp_cli.py -q "Create a clustered heatmap" --temperature 0.2
    
    # Get full JSON response (for programmatic use)
    python3 mcp_cli.py -q "Bar chart" --json
    
    # Get just the config (pipe to file or jq)
    python3 mcp_cli.py -q "Line chart" --config-only > config.json
    
    # Connect to custom server URL
    python3 mcp_cli.py -q "Bar chart" --url http://myserver:8000
"""

import argparse
import asyncio
import json
import sys
import uuid
import httpx


async def get_session_id(base_url: str) -> str:
    """Get session ID from MCP server."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/mcp", headers={"Accept": "application/json"})
        session_id = response.headers.get("mcp-session-id")
        if not session_id:
            raise ValueError("Failed to get session ID from server")
        return session_id


async def send_mcp_request(client: httpx.AsyncClient, url: str, session_id: str, method: str, params: dict = None):
    """Send MCP request and parse SSE response."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method
    }
    if params:
        payload["params"] = params
    
    headers = {
        "mcp-session-id": session_id,
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
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
    
    raise ValueError(f"Request failed with status {response.status_code}: {response.text}")


async def generate_config(base_url: str, query: str, headers: str = None, temperature: float = 0.0):
    """Generate CanvasXpress configuration via HTTP MCP server."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Get session ID
        session_id = await get_session_id(base_url)
        
        # 2. Initialize MCP session
        init_response = await send_mcp_request(
            client, f"{base_url}/mcp", session_id,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-cli", "version": "1.0.0"}
            }
        )
        
        # 3. Send initialized notification
        await send_mcp_request(
            client, f"{base_url}/mcp", session_id,
            "notifications/initialized"
        )
        
        # 4. Call the generate_canvasxpress_config tool
        params = {
            "name": "generate_canvasxpress_config",
            "arguments": {
                "description": query,
                "temperature": temperature
            }
        }
        
        if headers:
            params["arguments"]["headers"] = headers
        
        result = await send_mcp_request(
            client, f"{base_url}/mcp", session_id,
            "tools/call",
            params
        )
        
        return result


def main():
    parser = argparse.ArgumentParser(
        description="CLI client for CanvasXpress HTTP MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -q "Generate a bar graph with title 'hello, world'"
  %(prog)s -q "Scatter plot of expression over time" --headers "Time,Expression"
  %(prog)s -q "Clustered heatmap" --temperature 0.2
  %(prog)s -q "Bar chart" --json             # Full JSON response
  %(prog)s -q "Line chart" --config-only     # Just the config
  %(prog)s -q "Bar chart" --url http://myserver:8000
        """
    )
    
    parser.add_argument(
        "-q", "--query",
        required=True,
        help="Natural language description of the visualization"
    )
    
    parser.add_argument(
        "--headers",
        help="Optional comma-separated column headers (e.g., 'Time,Expression,Gene')"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM temperature (0.0-1.0, default: 0.0 for deterministic output)"
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="MCP server URL (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the full JSON response (success, config, error)"
    )
    
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Output only the CanvasXpress config JSON (no wrapper)"
    )
    
    args = parser.parse_args()
    
    # Validate temperature
    if not 0.0 <= args.temperature <= 1.0:
        print("❌ Error: temperature must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(1)
    
    # Display header unless json or config-only mode
    if not args.json and not args.config_only:
        print("🎨 CanvasXpress MCP CLI Client", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"🌐 Server: {args.url}", file=sys.stderr)
        print(f"📝 Query: {args.query}", file=sys.stderr)
        if args.headers:
            print(f"📊 Headers: {args.headers}", file=sys.stderr)
        print(f"🌡️  Temperature: {args.temperature}", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("⏳ Connecting to MCP server...", file=sys.stderr)
        print("", file=sys.stderr)
    
    try:
        # Generate configuration
        result = asyncio.run(generate_config(
            args.url,
            args.query,
            args.headers,
            args.temperature
        ))
        
        # Extract result
        if "result" in result:
            content = result["result"]["content"]
            
            # Get the JSON response from the tool
            tool_response = None
            for item in content:
                if item["type"] == "text":
                    tool_response = json.loads(item["text"])
                    break
            
            if tool_response is None:
                print("❌ No response content from tool", file=sys.stderr)
                sys.exit(1)
            
            if args.json:
                # Output full JSON response
                print(json.dumps(tool_response, indent=2))
            elif args.config_only:
                # Output only the config (or error if failed)
                if tool_response["success"]:
                    print(json.dumps(tool_response["config"], indent=2))
                else:
                    print(f"Error: {tool_response['error']}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Pretty formatted output
                if tool_response["success"]:
                    print("✅ Configuration generated successfully!", file=sys.stderr)
                    print("", file=sys.stderr)
                    print("=" * 60)
                    print(f"✅ **CanvasXpress Configuration Generated**\n")
                    print(f"**Description:** {tool_response['description']}")
                    if tool_response['headers']:
                        print(f"**Headers:** {tool_response['headers']}")
                    print(f"\n**Configuration:**")
                    print("```json")
                    print(json.dumps(tool_response['config'], indent=2))
                    print("```")
                    print("\n**Usage:**")
                    print("1. Copy the JSON configuration above")
                    print("2. Pass it to CanvasXpress constructor: `new CanvasXpress(data, config)`")
                    print("3. Or use with CanvasXpress libraries in R/Python")
                    print("\n**Documentation:** https://www.canvasxpress.org/")
                    print("**Examples:** https://www.canvasxpress.org/examples.html")
                    print("=" * 60)
                else:
                    print("❌ Generation failed!", file=sys.stderr)
                    print("", file=sys.stderr)
                    print("=" * 60)
                    print(f"❌ **Error**\n")
                    print(f"{tool_response['error']}")
                    print("\n**Troubleshooting:**")
                    print("- Check your API key environment variable")
                    print("- Ensure vector database is initialized")
                    print("- Check Docker logs for details")
                    print("=" * 60)
                    sys.exit(1)
        elif "error" in result:
            print(f"❌ MCP Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"❌ Unexpected response: {result}", file=sys.stderr)
            sys.exit(1)
    
    except httpx.ConnectError:
        print(f"❌ Connection Error: Could not connect to {args.url}", file=sys.stderr)
        print("\nMake sure the MCP server is running:", file=sys.stderr)
        print("  make run-http", file=sys.stderr)
        print("  or: docker run -p 8000:8000 canvasxpress-mcp-server:latest", file=sys.stderr)
        sys.exit(1)
    
    except KeyError as e:
        print(f"❌ Protocol Error: Missing expected field {e}", file=sys.stderr)
        print("\nThe server response was not in the expected format.", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
