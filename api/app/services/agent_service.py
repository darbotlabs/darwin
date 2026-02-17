"""
Agent Service - Multi-agent orchestration and coordination

Implements agent swarm capabilities for distributed file operations.
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    CREATED = "created"
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class Agent:
    """Individual agent in the swarm"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.config = config or {}
        self.status = AgentStatus.CREATED
        self.created_at = datetime.utcnow()
        self.last_activity = None
        self.operations_completed = 0
        self.current_task = None
    
    def assign_task(self, task: Dict[str, Any]):
        """Assign a task to this agent"""
        self.current_task = task
        self.status = AgentStatus.WORKING
        self.last_activity = datetime.utcnow()
        logger.info(f"Agent {self.name} assigned task: {task.get('description', 'N/A')}")
    
    def complete_task(self, result: Dict[str, Any]):
        """Mark current task as completed"""
        self.operations_completed += 1
        self.status = AgentStatus.IDLE
        self.last_activity = datetime.utcnow()
        self.current_task = None
        logger.info(f"Agent {self.name} completed task")
    
    def fail_task(self, error: str):
        """Mark current task as failed"""
        self.status = AgentStatus.FAILED
        self.last_activity = datetime.utcnow()
        logger.error(f"Agent {self.name} task failed: {error}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "operations_completed": self.operations_completed,
            "current_task": self.current_task
        }


class AgentSwarm:
    """Manages a swarm of coordinated agents"""
    
    def __init__(self, swarm_id: str, config: Optional[Dict[str, Any]] = None):
        self.swarm_id = swarm_id
        self.config = config or {}
        self.agents: Dict[str, Agent] = {}
        self.created_at = datetime.utcnow()
        self.task_queue: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: Agent):
        """Add an agent to the swarm"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Added agent {agent.name} to swarm {self.swarm_id}")
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the swarm"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_id} from swarm {self.swarm_id}")
    
    def get_idle_agents(self) -> List[Agent]:
        """Get list of idle agents"""
        return [a for a in self.agents.values() if a.status == AgentStatus.IDLE]
    
    def coordinate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate a task across the swarm
        
        Args:
            task: Task description and requirements
            
        Returns:
            Coordination result
        """
        # Find suitable agents for this task
        idle_agents = self.get_idle_agents()
        
        if not idle_agents:
            # Queue the task
            self.task_queue.append(task)
            logger.info(f"No idle agents, queued task: {task.get('description', 'N/A')}")
            return {
                "status": "queued",
                "message": "Task queued, no idle agents available"
            }
        
        # Assign task to first available agent
        agent = idle_agents[0]
        agent.assign_task(task)
        
        return {
            "status": "assigned",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "message": f"Task assigned to agent {agent.name}"
        }


class AgentService:
    """Service for managing agents and swarms"""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._swarms: Dict[str, AgentSwarm] = {}
    
    async def create_agent(
        self,
        name: str,
        agent_type: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new agent
        
        Returns:
            agent_id: Unique identifier for the agent
        """
        agent_id = str(uuid.uuid4())
        
        agent = Agent(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            capabilities=capabilities,
            config=config
        )
        
        self._agents[agent_id] = agent
        agent.status = AgentStatus.IDLE
        
        logger.info(f"Created agent {name} ({agent_id}) of type {agent_type}")
        return agent_id
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of an agent"""
        if agent_id not in self._agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        return self._agents[agent_id].to_dict()
    
    async def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent"""
        if agent_id not in self._agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self._agents[agent_id]
        agent.status = AgentStatus.TERMINATED
        del self._agents[agent_id]
        
        logger.info(f"Terminated agent {agent_id}")
        return True
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return [agent.to_dict() for agent in self._agents.values()]
    
    async def create_swarm(
        self,
        agent_ids: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create an agent swarm
        
        Args:
            agent_ids: List of agent IDs to include in swarm
            config: Swarm configuration
            
        Returns:
            swarm_id: Unique identifier for the swarm
        """
        swarm_id = str(uuid.uuid4())
        swarm = AgentSwarm(swarm_id=swarm_id, config=config)
        
        # Add agents to swarm
        for agent_id in agent_ids:
            if agent_id not in self._agents:
                raise ValueError(f"Agent {agent_id} not found")
            swarm.add_agent(self._agents[agent_id])
        
        self._swarms[swarm_id] = swarm
        logger.info(f"Created swarm {swarm_id} with {len(agent_ids)} agents")
        
        return swarm_id
    
    async def coordinate_swarm(
        self,
        task_description: str,
        agent_ids: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate a swarm of agents for a task
        
        Args:
            task_description: Description of the task
            agent_ids: List of agent IDs to coordinate
            config: Coordination configuration
            
        Returns:
            Coordination result
        """
        # Create or get swarm
        swarm_id = await self.create_swarm(agent_ids, config)
        swarm = self._swarms[swarm_id]
        
        # Create task
        task = {
            "description": task_description,
            "config": config or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Coordinate task across swarm
        result = swarm.coordinate_task(task)
        
        return {
            "coordination_id": swarm_id,
            "status": result["status"],
            "agents_assigned": 1 if result["status"] == "assigned" else 0,
            "estimated_completion": None,
            "details": result
        }


# Global agent service instance
agent_service = AgentService()
