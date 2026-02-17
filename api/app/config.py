"""
Darwin API Configuration Management
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    api_title: str = "Darwin File Transfer API"
    api_version: str = "1.0.0"
    api_description: str = "AI-native file transfer API with agent swarm support"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-this-secret-key-in-production"
    
    # .NET Assembly Configuration
    winscp_net_assembly_path: Optional[str] = None
    winscp_executable_path: Optional[str] = None
    
    # Agent Configuration
    enable_agent_swarm: bool = True
    max_concurrent_agents: int = 10
    agent_timeout_seconds: int = 300
    
    # MCP Configuration
    enable_mcp_server: bool = True
    mcp_server_port: int = 8001
    
    # Session Management
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 100
    
    # Security
    enable_authentication: bool = False
    cors_origins: list[str] = ["*"]
    
    # Monitoring
    enable_prometheus: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_assembly_path() -> Path:
    """Get the path to the WinSCP .NET assembly"""
    if settings.winscp_net_assembly_path:
        return Path(settings.winscp_net_assembly_path)
    
    # Default paths to check
    base_dir = Path(__file__).parent.parent.parent
    possible_paths = [
        base_dir / "dotnet" / "bin" / "Release" / "net48" / "WinSCPnet.dll",
        base_dir / "dotnet" / "bin" / "Debug" / "net48" / "WinSCPnet.dll",
        base_dir / "dotnet" / "bin" / "Release" / "netstandard2.0" / "WinSCPnet.dll",
        base_dir / "dotnet" / "bin" / "Debug" / "netstandard2.0" / "WinSCPnet.dll",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(
        "WinSCP .NET assembly not found. Please build the .NET project first or "
        "set WINSCP_NET_ASSEMBLY_PATH environment variable."
    )
