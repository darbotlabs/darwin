"""
Agent Swarm Scenario: Parallel File Uploads

This example demonstrates coordinating multiple agents to upload
files from different sources to a remote server in parallel.
"""
import httpx
import asyncio
from typing import List, Dict, Any

# Configuration
DARWIN_API_URL = "http://localhost:8000"
SFTP_CONFIG = {
    "protocol": "sftp",
    "hostname": "example.com",
    "username": "user",
    "password": "password"
}

# Files to upload (from different sources)
UPLOAD_TASKS = [
    {"local_path": "/data/logs/*.log", "remote_path": "/archive/logs/"},
    {"local_path": "/data/backups/*.zip", "remote_path": "/archive/backups/"},
    {"local_path": "/data/reports/*.pdf", "remote_path": "/archive/reports/"},
    {"local_path": "/data/images/*.jpg", "remote_path": "/archive/images/"},
]


async def create_session() -> str:
    """Create a Darwin session"""
    async with httpx.AsyncClient(base_url=DARWIN_API_URL) as client:
        response = await client.post(
            "/api/v1/session/create",
            json={"options": SFTP_CONFIG}
        )
        return response.json()["session_id"]


async def create_agents(count: int) -> List[str]:
    """Create multiple file transfer agents"""
    agent_ids = []
    async with httpx.AsyncClient(base_url=DARWIN_API_URL) as client:
        for i in range(count):
            response = await client.post(
                "/api/v1/agents",
                json={
                    "name": f"UploadAgent-{i}",
                    "agent_type": "file_transfer",
                    "capabilities": ["upload", "parallel_processing"],
                    "config": {"max_concurrent_transfers": 5}
                }
            )
            agent_data = response.json()
            agent_ids.append(agent_data["agent_id"])
            print(f"✅ Created agent: {agent_data['name']} ({agent_data['agent_id']})")
    
    return agent_ids


async def coordinate_parallel_uploads(
    session_id: str,
    agent_ids: List[str],
    tasks: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Coordinate agents to handle upload tasks in parallel"""
    async with httpx.AsyncClient(base_url=DARWIN_API_URL) as client:
        # Build task description
        task_description = f"Upload {len(tasks)} file sets in parallel: " + \
                          ", ".join([t["local_path"] for t in tasks])
        
        # Coordinate swarm
        response = await client.post(
            "/api/v1/agents/swarm/coordinate",
            json={
                "task_description": task_description,
                "agents": agent_ids,
                "config": {
                    "parallel_execution": True,
                    "tasks": tasks,
                    "session_id": session_id
                }
            }
        )
        
        return response.json()


async def monitor_progress(coordination_id: str):
    """Monitor swarm progress"""
    async with httpx.AsyncClient(base_url=DARWIN_API_URL) as client:
        while True:
            # In real implementation, this would query swarm status
            # For now, just demonstrate the pattern
            await asyncio.sleep(5)
            print(f"📊 Monitoring coordination {coordination_id}...")
            
            # Check if complete
            # break when done
            break


async def main():
    """Main execution"""
    print("🚀 Darwin Agent Swarm - Parallel Upload Scenario\n")
    
    # Step 1: Create session
    print("📡 Creating Darwin session...")
    session_id = await create_session()
    print(f"✅ Session created: {session_id}\n")
    
    # Step 2: Create agents
    print(f"🤖 Creating {len(UPLOAD_TASKS)} agents...")
    agent_ids = await create_agents(len(UPLOAD_TASKS))
    print(f"✅ Created {len(agent_ids)} agents\n")
    
    # Step 3: Coordinate uploads
    print("🎯 Coordinating parallel uploads...")
    coordination = await coordinate_parallel_uploads(
        session_id=session_id,
        agent_ids=agent_ids,
        tasks=UPLOAD_TASKS
    )
    print(f"✅ Coordination started: {coordination['coordination_id']}")
    print(f"   Status: {coordination['status']}")
    print(f"   Agents assigned: {coordination['agents_assigned']}\n")
    
    # Step 4: Monitor progress
    print("📊 Monitoring progress...")
    await monitor_progress(coordination['coordination_id'])
    
    print("\n🎉 Parallel upload complete!")
    print(f"\nSummary:")
    print(f"  - Files uploaded: {len(UPLOAD_TASKS)} sets")
    print(f"  - Agents used: {len(agent_ids)}")
    print(f"  - Execution: Parallel")


if __name__ == "__main__":
    asyncio.run(main())
