# Darwin API - MCP Integration Guide

This guide explains how to integrate Darwin with LLMs using the Model Context Protocol (MCP).

## What is MCP?

Model Context Protocol (MCP) is a standard for exposing tools to Large Language Models. It provides a consistent way to define tool schemas, handle tool calls, and return results.

## Available Tools

Darwin exposes the following MCP tools:

### 1. darwin_create_session

Create a new file transfer session.

**Input Schema:**
```json
{
  "protocol": "sftp",           // sftp, ftp, ftps, scp, s3, webdav
  "hostname": "example.com",    // Server address
  "username": "user",           // Authentication username
  "password": "password",       // Authentication password
  "port": 22,                   // Optional: custom port
  "ssh_host_key_fingerprint": "..." // Optional: for SFTP/SCP
}
```

**Returns:** `{ "session_id": "uuid" }`

### 2. darwin_upload_file

Upload files to remote server.

**Input Schema:**
```json
{
  "session_id": "uuid",
  "local_path": "/path/to/file.txt",
  "remote_path": "/remote/destination/",
  "transfer_mode": "automatic"  // binary, text, or automatic
}
```

### 3. darwin_download_file

Download files from remote server.

**Input Schema:**
```json
{
  "session_id": "uuid",
  "remote_path": "/remote/file.txt",
  "local_path": "/path/to/local/",
  "transfer_mode": "automatic"
}
```

### 4. darwin_list_directory

List contents of a remote directory.

**Input Schema:**
```json
{
  "session_id": "uuid",
  "remote_path": "/"
}
```

### 5. darwin_synchronize_directories

Synchronize local and remote directories.

**Input Schema:**
```json
{
  "session_id": "uuid",
  "local_path": "/local/dir",
  "remote_path": "/remote/dir",
  "mode": "local",              // local, remote, or both
  "remove_files": false,        // Delete files not in source
  "mirror": false               // Exact replica mode
}
```

## Integration Examples

### OpenAI Function Calling

```python
import openai
import httpx

# Get MCP tools from Darwin
darwin_client = httpx.Client(base_url="http://localhost:8000")
tools_response = darwin_client.get("/mcp/tools")
mcp_tools = tools_response.json()

# Convert to OpenAI format
openai_tools = []
for tool in mcp_tools:
    openai_tools.append({
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"]
        }
    })

# Use with OpenAI
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Upload myfile.txt to example.com via SFTP"}
    ],
    tools=openai_tools,
    tool_choice="auto"
)

# Execute tool calls via Darwin MCP endpoint
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = darwin_client.post("/mcp/tools/call", json={
            "tool_name": tool_call.function.name,
            "arguments": json.loads(tool_call.function.arguments)
        })
        print(result.json())
```

### LangChain Integration

```python
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
import httpx

darwin_client = httpx.Client(base_url="http://localhost:8000")

# Create LangChain tool
def darwin_upload(session_id: str, local_path: str, remote_path: str):
    """Upload a file to remote server using Darwin"""
    result = darwin_client.post("/mcp/tools/call", json={
        "tool_name": "darwin_upload_file",
        "arguments": {
            "session_id": session_id,
            "local_path": local_path,
            "remote_path": remote_path
        }
    })
    return result.json()

upload_tool = StructuredTool.from_function(
    func=darwin_upload,
    name="darwin_upload",
    description="Upload files to remote server via SFTP/FTP"
)

# Create agent
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_functions_agent(llm, [upload_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[upload_tool])

# Use agent
result = agent_executor.invoke({
    "input": "Upload report.pdf to the production server"
})
```

### Autogen Integration

```python
import autogen
import httpx

config_list = [{"model": "gpt-4", "api_key": "..."}]

# Create Darwin MCP function definitions
darwin_client = httpx.Client(base_url="http://localhost:8000")
tools = darwin_client.get("/mcp/tools").json()

# Convert to Autogen function format
functions = []
for tool in tools:
    functions.append({
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["input_schema"]
    })

# Create assistant with Darwin tools
assistant = autogen.AssistantAgent(
    name="file_transfer_assistant",
    llm_config={
        "config_list": config_list,
        "functions": functions
    }
)

# Create user proxy that executes Darwin calls
def execute_darwin_tool(name, arguments):
    result = darwin_client.post("/mcp/tools/call", json={
        "tool_name": name,
        "arguments": arguments
    })
    return result.json()

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    function_map={tool["name"]: execute_darwin_tool for tool in tools}
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Upload all log files to the backup server"
)
```

### Semantic Kernel Integration

```python
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
import httpx

kernel = Kernel()
darwin_client = httpx.Client(base_url="http://localhost:8000")

@kernel_function(
    name="upload_file",
    description="Upload a file to remote server"
)
def upload_file(session_id: str, local_path: str, remote_path: str) -> str:
    result = darwin_client.post("/mcp/tools/call", json={
        "tool_name": "darwin_upload_file",
        "arguments": {
            "session_id": session_id,
            "local_path": local_path,
            "remote_path": remote_path
        }
    })
    return str(result.json())

# Add to kernel
kernel.add_function(plugin_name="darwin", function=upload_file)

# Use in chat
chat = kernel.create_chat()
response = await chat.send_message("Upload myfile.txt to the server")
```

## Direct MCP Server Usage

Darwin also exposes a direct MCP server endpoint:

```python
# List tools
GET /mcp/tools

# Get tool schema
GET /mcp/tools/{tool_name}

# Call tool
POST /mcp/tools/call
{
  "tool_name": "darwin_upload_file",
  "arguments": {
    "session_id": "...",
    "local_path": "...",
    "remote_path": "..."
  }
}
```

## Best Practices

1. **Session Management**: Create a session once and reuse for multiple operations
2. **Error Handling**: Always check the `success` field in tool responses
3. **Security**: Never expose credentials in prompts; use environment variables
4. **Timeouts**: Set appropriate timeouts for large file transfers
5. **Validation**: Validate file paths before passing to tools

## Example Workflow

```python
# 1. Create session
session_response = call_mcp_tool("darwin_create_session", {
    "protocol": "sftp",
    "hostname": "example.com",
    "username": "user",
    "password": "pass"
})
session_id = session_response["result"]["session_id"]

# 2. List remote files
files_response = call_mcp_tool("darwin_list_directory", {
    "session_id": session_id,
    "remote_path": "/"
})

# 3. Upload file
upload_response = call_mcp_tool("darwin_upload_file", {
    "session_id": session_id,
    "local_path": "/data/report.pdf",
    "remote_path": "/uploads/"
})

# 4. Synchronize directories
sync_response = call_mcp_tool("darwin_synchronize_directories", {
    "session_id": session_id,
    "local_path": "/local/data",
    "remote_path": "/remote/backup",
    "mode": "local",
    "mirror": True
})
```

## Troubleshooting

### Tool Not Found

Ensure the Darwin API server is running:
```bash
curl http://localhost:8000/mcp/tools
```

### Authentication Errors

Check session credentials and SSH key fingerprints for SFTP.

### Permission Errors

Verify the user has appropriate permissions on the remote server.

### Network Errors

Check firewall rules and network connectivity to the remote server.

## Next Steps

- Try the [Jupyter notebook examples](../examples/notebooks/)
- Explore [agent swarm coordination](agent-swarms.md)
- Read the [API reference](api-reference.md)
