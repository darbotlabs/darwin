"""
Agent Swarm Scenario: Data Processing Pipeline

This example shows a multi-stage pipeline with different agent types
working sequentially to process and transfer data.

Pipeline stages:
1. Monitor agents watch for new files
2. Processor agents validate and transform files
3. Transfer agents upload to remote server
4. Cleanup agents remove processed files
"""
import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime

DARWIN_API_URL = "http://localhost:8000"


class PipelineOrchestrator:
    """Orchestrates a multi-stage data pipeline"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.session_id = None
        self.agents = {}
    
    async def initialize(self):
        """Initialize the pipeline"""
        print("🔧 Initializing data pipeline...\n")
        
        # Create session
        async with httpx.AsyncClient(base_url=self.api_url) as client:
            response = await client.post(
                "/api/v1/session/create",
                json={
                    "options": {
                        "protocol": "sftp",
                        "hostname": "data-server.example.com",
                        "username": "pipeline-bot",
                        "password": "secure-password"
                    }
                }
            )
            self.session_id = response.json()["session_id"]
            print(f"✅ Session created: {self.session_id}")
        
        # Create specialized agents
        await self._create_pipeline_agents()
    
    async def _create_pipeline_agents(self):
        """Create agents for each pipeline stage"""
        agent_configs = [
            {
                "name": "FileMonitor",
                "type": "monitor",
                "capabilities": ["watch_directory", "detect_changes"],
                "stage": "monitoring"
            },
            {
                "name": "DataValidator",
                "type": "custom",
                "capabilities": ["validate_format", "check_integrity"],
                "stage": "validation"
            },
            {
                "name": "DataTransformer",
                "type": "custom",
                "capabilities": ["convert_format", "compress", "encrypt"],
                "stage": "transformation"
            },
            {
                "name": "FileTransfer",
                "type": "file_transfer",
                "capabilities": ["upload", "resume", "verify"],
                "stage": "transfer"
            },
            {
                "name": "Cleanup",
                "type": "custom",
                "capabilities": ["delete_files", "archive"],
                "stage": "cleanup"
            }
        ]
        
        async with httpx.AsyncClient(base_url=self.api_url) as client:
            for config in agent_configs:
                response = await client.post(
                    "/api/v1/agents",
                    json={
                        "name": config["name"],
                        "agent_type": config["type"],
                        "capabilities": config["capabilities"]
                    }
                )
                agent_data = response.json()
                self.agents[config["stage"]] = agent_data["agent_id"]
                print(f"✅ Created {config['name']} agent for {config['stage']} stage")
    
    async def execute_pipeline(self, input_files: List[str]):
        """Execute the pipeline for given files"""
        print(f"\n🚀 Starting pipeline for {len(input_files)} files\n")
        
        stages = [
            ("monitoring", "Detecting new files"),
            ("validation", "Validating file formats"),
            ("transformation", "Transforming and compressing"),
            ("transfer", "Uploading to remote server"),
            ("cleanup", "Cleaning up local files")
        ]
        
        for stage, description in stages:
            print(f"📍 Stage: {stage.upper()}")
            print(f"   {description}...")
            
            # Coordinate agent for this stage
            async with httpx.AsyncClient(base_url=self.api_url) as client:
                response = await client.post(
                    "/api/v1/agents/swarm/coordinate",
                    json={
                        "task_description": f"{description} for {len(input_files)} files",
                        "agents": [self.agents[stage]],
                        "config": {
                            "stage": stage,
                            "files": input_files,
                            "session_id": self.session_id
                        }
                    }
                )
                
                result = response.json()
                print(f"   ✅ {result['status']}")
                
                # Simulate processing time
                await asyncio.sleep(1)
        
        print("\n🎉 Pipeline execution complete!")
    
    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics"""
        metrics = {
            "total_stages": len(self.agents),
            "active_agents": len(self.agents),
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In real implementation, query agent statuses
        async with httpx.AsyncClient(base_url=self.api_url) as client:
            for stage, agent_id in self.agents.items():
                try:
                    response = await client.get(f"/api/v1/agents/{agent_id}")
                    agent_status = response.json()
                    metrics[f"{stage}_operations"] = agent_status.get("operations_completed", 0)
                except:
                    pass
        
        return metrics


async def main():
    """Main execution"""
    print("=" * 60)
    print("Darwin Agent Swarm - Data Processing Pipeline")
    print("=" * 60 + "\n")
    
    # Initialize pipeline
    orchestrator = PipelineOrchestrator(DARWIN_API_URL)
    await orchestrator.initialize()
    
    # Example files to process
    input_files = [
        "/data/input/dataset_001.csv",
        "/data/input/dataset_002.csv",
        "/data/input/dataset_003.csv",
        "/data/input/logs_2024.txt"
    ]
    
    # Execute pipeline
    await orchestrator.execute_pipeline(input_files)
    
    # Get metrics
    print("\n📊 Pipeline Metrics:")
    metrics = await orchestrator.get_pipeline_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
