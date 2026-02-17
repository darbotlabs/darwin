# Darwin FastAPI Server

This directory contains the FastAPI-based REST API server for Darwin, providing AI agent-friendly endpoints for file transfer operations.

## Features

- **RESTful API**: Complete file transfer operations exposed as HTTP endpoints
- **MCP Support**: Model Context Protocol integration for LLM tool calling
- **Agent Swarm**: Multi-agent orchestration and coordination
- **OpenAPI Documentation**: Auto-generated Swagger UI
- **WebSocket Support**: Real-time operation progress
- **Session Management**: Secure token-based authentication
- **Adaptive Cards**: Rich UI templates for operations

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Note: Requires .NET assembly to be built first
cd ../dotnet
dotnet build
```

## Quick Start

```bash
# Start the API server
python -m uvicorn app.main:app --reload --port 8000

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

## Configuration

Create a `.env` file in the `api/` directory:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here

# .NET Assembly Path
WINSCP_NET_ASSEMBLY_PATH=../dotnet/bin/Release/net48/WinSCPnet.dll

# Agent Configuration
ENABLE_AGENT_SWARM=true
MAX_CONCURRENT_AGENTS=10

# MCP Configuration
ENABLE_MCP_SERVER=true
MCP_SERVER_PORT=8001
```

## API Endpoints

### File Operations
- `POST /api/v1/session/create` - Create a new session
- `POST /api/v1/session/{session_id}/upload` - Upload files
- `POST /api/v1/session/{session_id}/download` - Download files
- `GET /api/v1/session/{session_id}/list` - List directory contents
- `POST /api/v1/session/{session_id}/sync` - Synchronize directories
- `DELETE /api/v1/session/{session_id}` - Close session

### MCP Integration
- `POST /mcp/tools/list` - List available MCP tools
- `POST /mcp/tools/call` - Execute MCP tool

### Agent Swarm
- `POST /api/v1/agents/create` - Create agent
- `GET /api/v1/agents/{agent_id}/status` - Get agent status
- `POST /api/v1/agents/swarm/coordinate` - Coordinate agent swarm

## Architecture

```
api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic data models
│   ├── routers/             # API route handlers
│   │   ├── session.py       # Session management endpoints
│   │   ├── mcp.py           # MCP protocol endpoints
│   │   └── agents.py        # Agent swarm endpoints
│   ├── services/            # Business logic
│   │   ├── darwin_service.py   # .NET assembly wrapper
│   │   ├── mcp_service.py      # MCP implementation
│   │   └── agent_service.py    # Agent orchestration
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── examples/                # Usage examples
│   ├── notebooks/           # Jupyter notebooks
│   ├── adaptive_cards/      # Adaptive Card templates
│   └── agent_scenarios/     # Agent swarm examples
└── config/                  # Configuration files
```

## Development

```bash
# Run tests
pytest tests/

# Run with auto-reload
uvicorn app.main:app --reload

# Generate OpenAPI schema
python -m app.main --generate-schema > openapi.json
```

## Examples

See the `examples/` directory for:
- Jupyter notebooks demonstrating API usage
- Agent swarm coordination scenarios
- MCP tool calling examples
- Adaptive Card templates
