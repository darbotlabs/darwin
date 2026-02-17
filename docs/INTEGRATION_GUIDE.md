# Darwin Integration Guide

This guide provides detailed instructions for integrating Darwin with various AI frameworks, tools, and platforms.

## Table of Contents

1. [OpenAI / ChatGPT](#openai--chatgpt)
2. [LangChain](#langchain)
3. [Microsoft Autogen](#microsoft-autogen)
4. [Semantic Kernel](#semantic-kernel)
5. [Microsoft Teams Bots](#microsoft-teams-bots)
6. [Slack Bots](#slack-bots)
7. [GitHub Actions](#github-actions)
8. [Azure Functions](#azure-functions)
9. [AWS Lambda](#aws-lambda)
10. [Docker Deployment](#docker-deployment)

---

## OpenAI / ChatGPT

### Setup

```python
import openai
import httpx
import json

# Initialize clients
openai_client = openai.OpenAI(api_key="your-key")
darwin_client = httpx.Client(base_url="http://localhost:8000")
```

### Get Darwin Tools

```python
# Fetch MCP tools from Darwin
mcp_tools = darwin_client.get("/mcp/tools").json()

# Convert to OpenAI function format
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
```

### Use with Chat Completions

```python
def chat_with_darwin(message: str):
    messages = [
        {"role": "system", "content": "You are a helpful file transfer assistant."},
        {"role": "user", "content": message}
    ]
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"
    )
    
    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            # Execute via Darwin MCP
            result = darwin_client.post("/mcp/tools/call", json={
                "tool_name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            })
            
            # Add result to messages
            messages.append({
                "role": "function",
                "name": tool_call.function.name,
                "content": json.dumps(result.json())
            })
        
        # Get final response
        final_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return final_response.choices[0].message.content
    
    return response.choices[0].message.content

# Example usage
result = chat_with_darwin("Upload myfile.txt to example.com via SFTP")
print(result)
```

---

## LangChain

### Setup

```bash
pip install langchain langchain-openai
```

### Create Darwin Tools

```python
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import httpx

darwin = httpx.Client(base_url="http://localhost:8000")

def darwin_upload(session_id: str, local_path: str, remote_path: str) -> dict:
    """Upload a file to remote server"""
    result = darwin.post("/mcp/tools/call", json={
        "tool_name": "darwin_upload_file",
        "arguments": {
            "session_id": session_id,
            "local_path": local_path,
            "remote_path": remote_path
        }
    })
    return result.json()

def darwin_list(session_id: str, remote_path: str = "/") -> dict:
    """List directory contents"""
    result = darwin.post("/mcp/tools/call", json={
        "tool_name": "darwin_list_directory",
        "arguments": {
            "session_id": session_id,
            "remote_path": remote_path
        }
    })
    return result.json()

# Create LangChain tools
upload_tool = StructuredTool.from_function(
    func=darwin_upload,
    name="upload_file",
    description="Upload a file to remote server via SFTP/FTP"
)

list_tool = StructuredTool.from_function(
    func=darwin_list,
    name="list_directory",
    description="List contents of a remote directory"
)

tools = [upload_tool, list_tool]
```

### Create Agent

```python
# Create LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a file transfer assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use agent
result = agent_executor.invoke({
    "input": "Upload report.pdf to production server"
})
print(result)
```

---

## Microsoft Autogen

### Setup

```bash
pip install pyautogen
```

### Configure Autogen with Darwin

```python
import autogen
import httpx

darwin = httpx.Client(base_url="http://localhost:8000")

# Get Darwin tools
mcp_tools = darwin.get("/mcp/tools").json()

# Convert to Autogen format
autogen_functions = []
for tool in mcp_tools:
    autogen_functions.append({
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["input_schema"]
    })

# Configure LLM
config_list = [{
    "model": "gpt-4",
    "api_key": "your-key"
}]

# Create assistant
assistant = autogen.AssistantAgent(
    name="file_transfer_assistant",
    llm_config={
        "config_list": config_list,
        "functions": autogen_functions
    }
)

# Create user proxy
def execute_darwin_function(name: str, arguments: dict) -> dict:
    """Execute Darwin MCP tool"""
    result = darwin.post("/mcp/tools/call", json={
        "tool_name": name,
        "arguments": arguments
    })
    return result.json()

# Map all Darwin tools
function_map = {
    tool["name"]: lambda **kwargs: execute_darwin_function(kwargs)
    for tool in mcp_tools
}

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    function_map=function_map
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Upload all log files from /var/logs to backup server"
)
```

---

## Semantic Kernel

### Setup

```bash
pip install semantic-kernel
```

### Create Plugins

```python
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
import httpx

kernel = Kernel()
darwin = httpx.Client(base_url="http://localhost:8000")

class DarwinPlugin:
    """Darwin file transfer plugin for Semantic Kernel"""
    
    @kernel_function(
        name="upload_file",
        description="Upload a file to remote server"
    )
    def upload_file(
        self,
        session_id: str,
        local_path: str,
        remote_path: str
    ) -> str:
        result = darwin.post("/mcp/tools/call", json={
            "tool_name": "darwin_upload_file",
            "arguments": {
                "session_id": session_id,
                "local_path": local_path,
                "remote_path": remote_path
            }
        })
        return str(result.json())
    
    @kernel_function(
        name="list_directory",
        description="List directory contents"
    )
    def list_directory(self, session_id: str, remote_path: str = "/") -> str:
        result = darwin.post("/mcp/tools/call", json={
            "tool_name": "darwin_list_directory",
            "arguments": {
                "session_id": session_id,
                "remote_path": remote_path
            }
        })
        return str(result.json())

# Add plugin to kernel
kernel.add_plugin(DarwinPlugin(), plugin_name="darwin")

# Use in chat
chat = kernel.create_chat()
response = await chat.send_message(
    "Upload myfile.txt to the production server"
)
```

---

## Microsoft Teams Bots

### Setup

```bash
pip install botbuilder-core botbuilder-schema
```

### Use Adaptive Cards

```python
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity, Attachment
import json
import httpx

darwin = httpx.Client(base_url="http://localhost:8000")

class DarwinBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower()
        
        if "upload" in text:
            # Load Adaptive Card template
            with open("adaptive_cards/file_upload_card.json") as f:
                card_template = json.load(f)
            
            # Create session
            session = darwin.post("/api/v1/session/create", json={
                "options": {
                    "protocol": "sftp",
                    "hostname": "example.com",
                    "username": "user",
                    "password": "pass"
                }
            }).json()
            
            # Populate card data
            card_data = {
                "session_id": session["session_id"],
                "protocol": "SFTP",
                "hostname": "example.com",
                "status": "connected",
                "api_url": "http://localhost:8000"
            }
            
            # Send card
            card_attachment = Attachment(
                content_type="application/vnd.microsoft.card.adaptive",
                content=card_template
            )
            
            await turn_context.send_activity(
                Activity(attachments=[card_attachment])
            )
```

---

## GitHub Actions

### Workflow Example

```yaml
name: Deploy with Darwin

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build project
        run: npm run build
      
      - name: Upload to server
        env:
          DARWIN_API: ${{ secrets.DARWIN_API_URL }}
          SERVER_PASSWORD: ${{ secrets.SERVER_PASSWORD }}
        run: |
          # Create session
          SESSION_ID=$(curl -X POST $DARWIN_API/api/v1/session/create \
            -H "Content-Type: application/json" \
            -d '{
              "options": {
                "protocol": "sftp",
                "hostname": "production.example.com",
                "username": "deploy",
                "password": "'$SERVER_PASSWORD'"
              }
            }' | jq -r .session_id)
          
          # Upload files
          curl -X POST $DARWIN_API/api/v1/session/$SESSION_ID/upload \
            -H "Content-Type: application/json" \
            -d '{
              "local_path": "./dist/*",
              "remote_path": "/var/www/html/"
            }'
          
          # Close session
          curl -X DELETE $DARWIN_API/api/v1/session/$SESSION_ID
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY api/ .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  darwin-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - ENABLE_MCP_SERVER=true
      - ENABLE_AGENT_SWARM=true
    volumes:
      - ./api:/app
    restart: unless-stopped
```

### Deploy

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Best Practices

1. **Error Handling**: Always wrap Darwin API calls in try-catch blocks
2. **Session Management**: Reuse sessions for multiple operations
3. **Security**: Store credentials in environment variables, not code
4. **Rate Limiting**: Implement rate limiting for production deployments
5. **Logging**: Enable detailed logging for troubleshooting
6. **Monitoring**: Use the dashboard to monitor active sessions and agents
7. **Testing**: Test integrations in staging before production

## Troubleshooting

### Connection Refused
- Check Darwin API is running: `curl http://localhost:8000/health`
- Verify firewall rules allow port 8000

### Authentication Errors
- Verify server credentials
- Check SSH key fingerprints for SFTP

### Tool Call Failures
- Validate input arguments match tool schema
- Check Darwin API logs for detailed errors

## Support

- GitHub Issues: https://github.com/darbotlabs/darwin/issues
- Documentation: http://localhost:8000/docs
- Wiki: https://github.com/darbotlabs/darwin/wiki
