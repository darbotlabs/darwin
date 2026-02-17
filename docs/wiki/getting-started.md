---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started with Darwin

This guide will help you set up and start using Darwin for file transfer operations with AI agent integration.

## Prerequisites

- Python 3.8 or higher
- .NET Framework 4.8 or .NET Core 3.1+ (for Windows)
- Basic understanding of REST APIs

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/darbotlabs/darwin.git
cd darwin
```

### 2. Install Python Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here

# Enable features
ENABLE_MCP_SERVER=true
ENABLE_AGENT_SWARM=true
```

### 4. Build .NET Assembly (Optional)

If you want to use the full file transfer capabilities:

```bash
cd ../dotnet
dotnet build
```

## Starting the Server

Start the FastAPI server:

```bash
cd api
python -m uvicorn app.main:app --reload
```

The server will start on http://localhost:8000

## Verify Installation

### Check API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Open API Documentation

Navigate to http://localhost:8000/docs in your browser to see the interactive API documentation.

## Your First Request

### 1. Create a Session

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

response = client.post("/api/v1/session/create", json={
    "options": {
        "protocol": "sftp",
        "hostname": "example.com",
        "username": "user",
        "password": "password"
    }
})

session_id = response.json()["session_id"]
print(f"Session created: {session_id}")
```

### 2. Upload a File

```python
response = client.post(
    f"/api/v1/session/{session_id}/upload",
    json={
        "local_path": "/path/to/file.txt",
        "remote_path": "/remote/destination/"
    }
)

print(response.json())
```

### 3. List Directory

```python
response = client.post(
    f"/api/v1/session/{session_id}/list",
    json={"remote_path": "/"}
)

files = response.json()
print(f"Found {files['count']} files")
```

### 4. Close Session

```python
client.delete(f"/api/v1/session/{session_id}")
print("Session closed")
```

## Using MCP (Model Context Protocol)

List available tools for LLM integration:

```python
response = client.get("/mcp/tools")
tools = response.json()

for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

Call an MCP tool:

```python
response = client.post("/mcp/tools/call", json={
    "tool_name": "darwin_list_directory",
    "arguments": {
        "session_id": session_id,
        "remote_path": "/"
    }
})

result = response.json()
print(result)
```

## Creating Agents

Create a file transfer agent:

```python
response = client.post("/api/v1/agents", json={
    "name": "MyFileAgent",
    "agent_type": "file_transfer",
    "capabilities": ["upload", "download", "sync"]
})

agent_id = response.json()["agent_id"]
print(f"Agent created: {agent_id}")
```

## Coordinate Agent Swarm

```python
# Create multiple agents
agent_ids = []
for i in range(3):
    response = client.post("/api/v1/agents", json={
        "name": f"Agent-{i}",
        "agent_type": "file_transfer",
        "capabilities": ["upload"]
    })
    agent_ids.append(response.json()["agent_id"])

# Coordinate them
response = client.post("/api/v1/agents/swarm/coordinate", json={
    "task_description": "Upload files in parallel",
    "agents": agent_ids
})

print(response.json())
```

## Next Steps

- Explore [API Reference](api-reference.md) for detailed endpoint documentation
- Learn about [MCP Integration](mcp-integration.md) for LLM tool calling
- Read [Agent Swarms](agent-swarms.md) for advanced coordination
- Try the [Jupyter Notebooks](../api/examples/notebooks/) for interactive examples

## Troubleshooting

### Server won't start

Check that port 8000 is not in use:
```bash
lsof -i :8000  # On Linux/Mac
netstat -ano | findstr :8000  # On Windows
```

### .NET assembly not found

Make sure you've built the .NET project:
```bash
cd dotnet
dotnet build
```

Or set the assembly path in `.env`:
```env
WINSCP_NET_ASSEMBLY_PATH=/path/to/WinSCPnet.dll
```

### Connection errors

Verify your server credentials and network connectivity. Use a tool like `ssh` or `ftp` to test the connection manually first.

## Support

- Report issues: https://github.com/darbotlabs/darwin/issues
- Ask questions: https://github.com/darbotlabs/darwin/discussions
- Read more: https://github.com/darbotlabs/darwin/wiki
