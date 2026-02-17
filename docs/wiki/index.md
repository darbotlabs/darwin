---
layout: default
title: Home
nav_order: 1
---

# Darwin Wiki

Welcome to the Darwin documentation wiki. Darwin is an AI-native file transfer framework with advanced agent orchestration capabilities.

## Quick Links

- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [MCP Integration](mcp-integration.md)
- [Agent Swarms](agent-swarms.md)
- [Examples](examples.md)

## What is Darwin?

Darwin is an agentic fork of WinSCP, enhanced with modern AI capabilities:

- **Multi-Protocol Support**: SFTP, FTP, FTPS, SCP, S3, WebDAV
- **FastAPI REST Server**: RESTful API for all file operations
- **MCP Integration**: Model Context Protocol for LLM tool calling
- **Agent Swarms**: Coordinate multiple agents for parallel operations
- **Adaptive Cards**: Rich UI templates for bot integration
- **Jupyter Support**: Interactive notebooks for exploration

## Architecture

```
┌─────────────────────────────────────────┐
│          Client Applications            │
│   (LLMs, Bots, Scripts, Notebooks)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         FastAPI REST Server             │
│  ┌──────────┬──────────┬──────────┐    │
│  │ Session  │   MCP    │  Agent   │    │
│  │ Router   │  Router  │  Router  │    │
│  └──────────┴──────────┴──────────┘    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        .NET Assembly Wrapper            │
│     (WinSCP .NET API Integration)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Native C++ File Transfer Core      │
│   (SFTP, FTP, S3, WebDAV protocols)     │
└─────────────────────────────────────────┘
```

## Key Features

### RESTful API

All file transfer operations exposed as HTTP endpoints with OpenAPI documentation.

```python
# Create session
POST /api/v1/session/create

# Upload files
POST /api/v1/session/{session_id}/upload

# Download files
POST /api/v1/session/{session_id}/download
```

### Model Context Protocol (MCP)

LLM-friendly tool definitions for seamless AI integration.

```json
{
  "name": "darwin_upload_file",
  "description": "Upload file to remote server",
  "input_schema": { ... }
}
```

### Agent Swarms

Coordinate multiple agents for complex workflows:

- Parallel file operations
- Multi-stage pipelines
- Distributed processing
- Automatic failover

### Developer Experience

- **Interactive Notebooks**: Jupyter notebooks with examples
- **Adaptive Cards**: Pre-built UI templates
- **Comprehensive Docs**: API reference with examples
- **Testing Tools**: pytest suite included

## Getting Started

1. **Install Dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the Server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Open Documentation**
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8000/dashboard

## Use Cases

### CI/CD Integration

Automate deployments with file transfer operations in your build pipeline.

### Data Pipelines

Build multi-stage data processing workflows with agent coordination.

### LLM Tool Calling

Enable LLMs to perform file operations through MCP integration.

### Monitoring & Automation

Create monitoring agents that watch for file changes and trigger actions.

## Community

- **GitHub**: https://github.com/darbotlabs/darwin
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas

## License

Darwin inherits the WinSCP license. See [license.txt](../license.txt) for details.
