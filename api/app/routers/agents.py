"""
Agent API Router - Agent swarm management and coordination
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import (
    AgentCreateRequest,
    AgentStatus,
    SwarmCoordinationRequest,
    SwarmCoordinationResponse
)
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("/agents", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_agent(request: AgentCreateRequest):
    """
    Create a new agent
    
    - **name**: Human-readable agent name
    - **agent_type**: Type of agent (file_transfer, orchestrator, monitor, custom)
    - **capabilities**: List of capabilities this agent possesses
    - **config**: Optional configuration parameters
    """
    try:
        agent_id = await agent_service.create_agent(
            name=request.name,
            agent_type=request.agent_type.value,
            capabilities=request.capabilities,
            config=request.config
        )
        
        return {
            "agent_id": agent_id,
            "name": request.name,
            "status": "created",
            "message": f"Agent {request.name} created successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/agents", response_model=List[AgentStatus])
async def list_agents():
    """List all active agents in the system"""
    try:
        agents = await agent_service.list_agents()
        return [AgentStatus(**agent) for agent in agents]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/agents/{agent_id}", response_model=AgentStatus)
async def get_agent_status(agent_id: str):
    """Get status and details of a specific agent"""
    try:
        agent = await agent_service.get_agent_status(agent_id)
        return AgentStatus(**agent)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_agent(agent_id: str):
    """Terminate an agent and cleanup resources"""
    try:
        await agent_service.terminate_agent(agent_id)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate agent: {str(e)}"
        )


@router.post("/agents/swarm/coordinate", response_model=SwarmCoordinationResponse)
async def coordinate_agent_swarm(request: SwarmCoordinationRequest):
    """
    Coordinate a swarm of agents to work on a task
    
    This endpoint enables multi-agent coordination where multiple agents
    can work together on complex file transfer and orchestration tasks.
    
    - **task_description**: Description of the task to accomplish
    - **agents**: List of agent IDs to coordinate
    - **config**: Optional swarm configuration (parallelism, timeout, etc.)
    
    Example use cases:
    - Parallel file uploads/downloads across multiple servers
    - Distributed data synchronization
    - Multi-stage file processing pipelines
    """
    try:
        result = await agent_service.coordinate_swarm(
            task_description=request.task_description,
            agent_ids=request.agents,
            config=request.config
        )
        
        return SwarmCoordinationResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Swarm coordination failed: {str(e)}"
        )
