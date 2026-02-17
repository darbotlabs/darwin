"""
MCP API Router - Model Context Protocol endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import MCPTool, MCPToolCallRequest, MCPToolCallResponse
from app.services.mcp_service import mcp_service

router = APIRouter()


@router.get("/tools", response_model=List[MCPTool])
async def list_mcp_tools():
    """
    List all available MCP tools for LLM integration
    
    Returns a list of tools that can be called by language models,
    following the Model Context Protocol specification.
    """
    try:
        tools = await mcp_service.list_tools()
        return [MCPTool(**tool) for tool in tools]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list MCP tools: {str(e)}"
        )


@router.get("/tools/{tool_name}", response_model=MCPTool)
async def get_mcp_tool(tool_name: str):
    """Get details about a specific MCP tool"""
    try:
        tool = mcp_service.get_tool_schema(tool_name)
        return MCPTool(**tool)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool: {str(e)}"
        )


@router.post("/tools/call", response_model=MCPToolCallResponse)
async def call_mcp_tool(request: MCPToolCallRequest):
    """
    Execute an MCP tool with provided arguments
    
    This endpoint allows LLMs to call Darwin file transfer operations
    using the Model Context Protocol.
    
    - **tool_name**: Name of the tool to execute
    - **arguments**: Tool-specific arguments matching the tool's input schema
    
    Example:
    ```json
    {
        "tool_name": "darwin_upload_file",
        "arguments": {
            "session_id": "uuid-here",
            "local_path": "/path/to/file",
            "remote_path": "/remote/destination"
        }
    }
    ```
    """
    try:
        result = await mcp_service.call_tool(
            tool_name=request.tool_name,
            arguments=request.arguments
        )
        
        return MCPToolCallResponse(
            result=result.get("result"),
            success=result.get("success", False),
            error=result.get("error")
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool call failed: {str(e)}"
        )
