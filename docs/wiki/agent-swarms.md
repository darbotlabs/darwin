---
layout: default
title: Agent Swarms
nav_order: 4
---

# Agent Swarms

Agent swarms in Darwin enable coordinated multi-agent operations for complex file transfer and processing workflows.

## Overview

An agent swarm is a collection of coordinated agents working together on a shared task. Darwin's swarm architecture supports:

- **Parallel Execution**: Multiple agents running simultaneously
- **Task Distribution**: Automatic workload balancing
- **Failure Handling**: Automatic retry and failover
- **Progress Tracking**: Real-time monitoring of swarm status

## Agent Types

### File Transfer Agent

Specialized for file operations:
- Upload/download files
- Directory synchronization
- Batch operations
- Resume support

```python
client.post("/api/v1/agents", json={
    "name": "FileAgent-1",
    "agent_type": "file_transfer",
    "capabilities": ["upload", "download", "sync"]
})
```

### Monitor Agent

Watches for file system changes:
- Directory monitoring
- Change detection
- Event triggers
- Alert generation

```python
client.post("/api/v1/agents", json={
    "name": "MonitorAgent",
    "agent_type": "monitor",
    "capabilities": ["watch_directory", "detect_changes"]
})
```

### Orchestrator Agent

Coordinates other agents:
- Task distribution
- Workflow management
- Resource allocation
- Status aggregation

```python
client.post("/api/v1/agents", json={
    "name": "Orchestrator",
    "agent_type": "orchestrator",
    "capabilities": ["coordinate", "distribute_tasks"]
})
```

### Custom Agent

User-defined agents:
- Custom logic
- Specialized processing
- Integration with external systems

```python
client.post("/api/v1/agents", json={
    "name": "CustomProcessor",
    "agent_type": "custom",
    "capabilities": ["validate", "transform", "encrypt"]
})
```

## Creating a Swarm

### Basic Swarm

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

# Create agents
agent_ids = []
for i in range(3):
    response = client.post("/api/v1/agents", json={
        "name": f"Agent-{i}",
        "agent_type": "file_transfer",
        "capabilities": ["upload", "download"]
    })
    agent_ids.append(response.json()["agent_id"])

# Coordinate swarm
response = client.post("/api/v1/agents/swarm/coordinate", json={
    "task_description": "Upload files in parallel",
    "agents": agent_ids,
    "config": {
        "parallel_execution": True,
        "max_retries": 3
    }
})

coordination_id = response.json()["coordination_id"]
```

## Use Cases

### Parallel File Uploads

Upload multiple large files simultaneously:

```python
tasks = [
    {"local": "/data/file1.zip", "remote": "/backup/"},
    {"local": "/data/file2.zip", "remote": "/backup/"},
    {"local": "/data/file3.zip", "remote": "/backup/"},
]

# Create one agent per file
agents = [create_agent(f"Uploader-{i}") for i in range(len(tasks))]

# Coordinate upload
coordinate_swarm(
    agents=agents,
    task_description="Parallel upload of 3 files",
    config={"tasks": tasks}
)
```

### Multi-Stage Pipeline

Process files through multiple stages:

```python
# Stage 1: Monitor for new files
monitor = create_agent("Monitor", "monitor")

# Stage 2: Validate files
validator = create_agent("Validator", "custom")

# Stage 3: Transform files
transformer = create_agent("Transformer", "custom")

# Stage 4: Upload to remote
uploader = create_agent("Uploader", "file_transfer")

# Coordinate pipeline
pipeline = [monitor, validator, transformer, uploader]
coordinate_swarm(
    agents=pipeline,
    task_description="Multi-stage data pipeline",
    config={"sequential": True}
)
```

### Distributed Backup

Backup files to multiple locations:

```python
# Create agents for each backup location
backup_agents = [
    create_agent("AWS-S3", "file_transfer"),
    create_agent("Azure-Blob", "file_transfer"),
    create_agent("Local-NAS", "file_transfer"),
]

# Coordinate backup to all locations
coordinate_swarm(
    agents=backup_agents,
    task_description="Replicate backups to 3 locations",
    config={
        "parallel_execution": True,
        "source": "/data/backups",
        "verify_checksums": True
    }
)
```

## Monitoring Swarms

### Get Swarm Status

```python
response = client.get(f"/api/v1/agents/swarm/{coordination_id}/status")
status = response.json()

print(f"Status: {status['status']}")
print(f"Active agents: {status['active_agents']}")
print(f"Completed tasks: {status['completed_tasks']}")
```

### Monitor Individual Agents

```python
for agent_id in agent_ids:
    response = client.get(f"/api/v1/agents/{agent_id}")
    agent = response.json()
    
    print(f"{agent['name']}: {agent['status']}")
    print(f"  Operations: {agent['operations_completed']}")
    print(f"  Last activity: {agent['last_activity']}")
```

### Real-Time Updates (WebSocket)

```javascript
// JavaScript client
const ws = new WebSocket('ws://localhost:8000/ws/swarms/coordination_id');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log(`Swarm update: ${update.status}`);
    console.log(`Progress: ${update.progress}%`);
};
```

## Advanced Patterns

### Retry Logic

```python
config = {
    "max_retries": 3,
    "retry_delay_seconds": 5,
    "exponential_backoff": True,
    "retry_on_errors": ["ConnectionError", "TimeoutError"]
}
```

### Load Balancing

```python
config = {
    "load_balancing": "round_robin",  # or "least_loaded"
    "max_concurrent_per_agent": 5,
    "queue_overflow_strategy": "create_new_agent"
}
```

### Failure Handling

```python
config = {
    "on_agent_failure": "reassign",  # or "skip", "abort"
    "failure_threshold": 0.3,  # Abort if >30% fail
    "notify_on_failure": True
}
```

### Resource Limits

```python
config = {
    "max_memory_mb": 1024,
    "max_cpu_percent": 80,
    "max_network_mbps": 100,
    "timeout_seconds": 3600
}
```

## Best Practices

1. **Start Small**: Begin with 2-3 agents, scale up as needed
2. **Monitor Resources**: Watch CPU, memory, and network usage
3. **Handle Failures**: Always configure retry and failover logic
4. **Log Everything**: Enable detailed logging for troubleshooting
5. **Test Thoroughly**: Test swarm behavior under various conditions
6. **Optimize Tasks**: Ensure tasks are suitable for parallel execution
7. **Clean Up**: Terminate agents after tasks complete

## Example Scenarios

See the [example scenarios](../api/examples/agent_scenarios/) directory:
- `parallel_uploads.py` - Upload multiple files simultaneously
- `data_pipeline.py` - Multi-stage processing pipeline

## API Reference

### Create Agent
```
POST /api/v1/agents
```

### List Agents
```
GET /api/v1/agents
```

### Get Agent Status
```
GET /api/v1/agents/{agent_id}
```

### Coordinate Swarm
```
POST /api/v1/agents/swarm/coordinate
```

### Terminate Agent
```
DELETE /api/v1/agents/{agent_id}
```

## Next Steps

- Try the [parallel upload example](../api/examples/agent_scenarios/parallel_uploads.py)
- Build your own [custom agent](custom-agents.md)
- Integrate with [MCP for LLM control](mcp-integration.md)
