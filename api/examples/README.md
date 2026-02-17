# Darwin API Examples

This directory contains examples for using the Darwin API.

## Contents

### Jupyter Notebooks (`notebooks/`)

Interactive examples demonstrating API usage:

- **`getting_started.ipynb`** - Complete walkthrough of Darwin API features
  - Creating sessions
  - File upload/download
  - MCP tool calling
  - Agent swarm coordination

To use:
```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
cd api/examples/notebooks
jupyter notebook getting_started.ipynb
```

### Adaptive Cards (`adaptive_cards/`)

Microsoft Adaptive Cards templates for rich UI integration:

- **`file_upload_card.json`** - File upload form with session context
- **`agent_swarm_status_card.json`** - Real-time agent swarm monitoring

Use these with:
- Microsoft Teams bots
- Azure Bot Service
- Outlook Actionable Messages
- Windows Timeline

Example integration:
```python
import json
from adaptivecards.card import AdaptiveCard

# Load template
with open('file_upload_card.json') as f:
    template = json.load(f)

# Populate with data
card_data = {
    "session_id": "abc-123",
    "protocol": "SFTP",
    "hostname": "example.com",
    "status": "connected",
    "api_url": "http://localhost:8000"
}

# Render card (in bot framework)
card = AdaptiveCard.from_dict(template)
# Send to user...
```

### Agent Scenarios (`agent_scenarios/`)

Example agent coordination scenarios:

1. **Parallel Uploads** - Multiple agents uploading different files simultaneously
2. **Data Pipeline** - Sequential processing with multiple agent types
3. **Monitoring & Alerting** - Continuous monitoring with alert agents
4. **Batch Processing** - Large-scale file operations

## Running Examples

### Basic API Usage (Python)

```python
import httpx

# Connect to Darwin API
client = httpx.Client(base_url="http://localhost:8000")

# Create session
response = client.post("/api/v1/session/create", json={
    "options": {
        "protocol": "sftp",
        "hostname": "example.com",
        "username": "user",
        "password": "pass"
    }
})
session_id = response.json()["session_id"]

# Upload file
response = client.post(
    f"/api/v1/session/{session_id}/upload",
    json={
        "local_path": "/local/file.txt",
        "remote_path": "/remote/"
    }
)
print(response.json())
```

### MCP Tool Calling (LangChain)

```python
from langchain.tools import StructuredTool
import httpx

client = httpx.Client(base_url="http://localhost:8000")

def darwin_upload_tool(session_id: str, local_path: str, remote_path: str):
    """Upload a file using Darwin"""
    response = client.post(f"/api/v1/session/{session_id}/upload", json={
        "local_path": local_path,
        "remote_path": remote_path
    })
    return response.json()

# Create LangChain tool
upload_tool = StructuredTool.from_function(
    func=darwin_upload_tool,
    name="darwin_upload",
    description="Upload files to remote server via SFTP/FTP"
)

# Use with LLM...
```

### Agent Swarm (AutoGen)

```python
import autogen
import httpx

# Darwin API client
darwin_client = httpx.Client(base_url="http://localhost:8000")

# Create agents in Darwin
agent_ids = []
for i in range(3):
    response = darwin_client.post("/api/v1/agents", json={
        "name": f"FileAgent-{i}",
        "agent_type": "file_transfer",
        "capabilities": ["upload", "download"]
    })
    agent_ids.append(response.json()["agent_id"])

# Coordinate swarm
response = darwin_client.post("/api/v1/agents/swarm/coordinate", json={
    "task_description": "Upload logs from all servers",
    "agents": agent_ids
})

coordination_id = response.json()["coordination_id"]
print(f"Swarm coordination started: {coordination_id}")
```

## Integration Patterns

### 1. LLM Tool Calling

Use MCP endpoints for seamless LLM integration:

```python
# Get tool schemas
tools = client.get("/mcp/tools").json()

# Pass to LLM (OpenAI format)
llm_tools = [{
    "type": "function",
    "function": {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["input_schema"]
    }
} for tool in tools]

# LLM calls tool -> execute via Darwin MCP endpoint
```

### 2. CI/CD Integration

```yaml
# GitHub Actions example
- name: Deploy with Darwin
  run: |
    SESSION_ID=$(curl -X POST http://darwin-api/api/v1/session/create \
      -H "Content-Type: application/json" \
      -d '{"options": {...}}' | jq -r .session_id)
    
    curl -X POST http://darwin-api/api/v1/session/$SESSION_ID/upload \
      -H "Content-Type: application/json" \
      -d '{"local_path": "./dist/*", "remote_path": "/var/www/"}'
```

### 3. Monitoring Dashboard

Use WebSocket endpoints for real-time updates:

```javascript
// React/Vue dashboard
const ws = new WebSocket('ws://localhost:8000/ws/sessions');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
};
```

## Need Help?

- API Documentation: http://localhost:8000/docs
- GitHub Issues: https://github.com/darbotlabs/darwin/issues
- MCP Specification: https://modelcontextprotocol.io
