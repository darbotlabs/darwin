"""
Tests for Darwin API

Run with: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "Darwin File Transfer API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_mcp_list_tools():
    """Test listing MCP tools"""
    response = client.get("/mcp/tools")
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # Check tool structure
    tool = tools[0]
    assert "name" in tool
    assert "description" in tool
    assert "input_schema" in tool


def test_create_agent():
    """Test creating an agent"""
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "TestAgent",
            "agent_type": "file_transfer",
            "capabilities": ["upload", "download"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "agent_id" in data
    assert data["name"] == "TestAgent"
    assert data["status"] == "created"


def test_list_agents():
    """Test listing agents"""
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)


def test_openapi_schema():
    """Test that OpenAPI schema is generated"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema


# Integration tests (require .NET assembly)
@pytest.mark.skipif(
    True,  # Skip by default - requires .NET assembly
    reason="Requires .NET assembly and proper configuration"
)
class TestSessionOperations:
    """Tests for session operations - requires .NET assembly"""
    
    def test_create_session(self):
        """Test creating a file transfer session"""
        response = client.post(
            "/api/v1/session/create",
            json={
                "options": {
                    "protocol": "sftp",
                    "hostname": "test.example.com",
                    "username": "testuser",
                    "password": "testpass"
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
    
    def test_list_directory(self):
        """Test listing directory (requires active session)"""
        # This would require a real session
        pass
