"""
Darwin API Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class Protocol(str, Enum):
    """File transfer protocols"""
    SFTP = "sftp"
    FTP = "ftp"
    FTPS = "ftps"
    SCP = "scp"
    S3 = "s3"
    WEBDAV = "webdav"


class TransferMode(str, Enum):
    """File transfer modes"""
    BINARY = "binary"
    TEXT = "text"
    AUTOMATIC = "automatic"


class SessionOptionsModel(BaseModel):
    """Session connection options"""
    protocol: Protocol
    hostname: str = Field(..., description="Server hostname or IP address")
    port: Optional[int] = Field(None, description="Server port (default: protocol-specific)")
    username: str = Field(..., description="Authentication username")
    password: Optional[str] = Field(None, description="Authentication password")
    ssh_host_key_fingerprint: Optional[str] = Field(None, description="SSH host key fingerprint")
    timeout: int = Field(default=60, description="Connection timeout in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "protocol": "sftp",
                "hostname": "example.com",
                "username": "user",
                "password": "pass123",
                "ssh_host_key_fingerprint": "ssh-rsa 2048 xx:xx:xx:xx...",
                "timeout": 60
            }
        }


class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    options: SessionOptionsModel
    session_name: Optional[str] = Field(None, description="Optional session name")


class SessionCreateResponse(BaseModel):
    """Response after creating a session"""
    session_id: str
    status: str
    created_at: datetime
    message: str


class TransferOptionsModel(BaseModel):
    """File transfer options"""
    transfer_mode: TransferMode = TransferMode.AUTOMATIC
    preserve_timestamp: bool = True
    resume_support: bool = True
    overwrite_mode: str = "overwrite"


class FileUploadRequest(BaseModel):
    """Request to upload files"""
    local_path: str = Field(..., description="Local file or directory path")
    remote_path: str = Field(..., description="Remote destination path")
    options: Optional[TransferOptionsModel] = None
    remove_after_upload: bool = False


class FileDownloadRequest(BaseModel):
    """Request to download files"""
    remote_path: str = Field(..., description="Remote file or directory path")
    local_path: str = Field(..., description="Local destination path")
    options: Optional[TransferOptionsModel] = None
    remove_after_download: bool = False


class FileListRequest(BaseModel):
    """Request to list directory contents"""
    remote_path: str = Field(default="/", description="Remote directory path")


class RemoteFileInfo(BaseModel):
    """Information about a remote file"""
    name: str
    full_name: str
    is_directory: bool
    length: int
    last_write_time: Optional[datetime] = None
    permissions: Optional[str] = None


class FileListResponse(BaseModel):
    """Response with directory listing"""
    path: str
    files: List[RemoteFileInfo]
    count: int


class OperationResult(BaseModel):
    """Result of a file operation"""
    success: bool
    operation: str
    files_transferred: int = 0
    bytes_transferred: int = 0
    duration_seconds: float = 0.0
    errors: List[str] = []
    message: str


class SessionStatus(BaseModel):
    """Status of a session"""
    session_id: str
    status: str
    created_at: datetime
    last_activity: datetime
    operations_count: int


# MCP Models

class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPToolCallRequest(BaseModel):
    """Request to call an MCP tool"""
    tool_name: str
    arguments: Dict[str, Any]


class MCPToolCallResponse(BaseModel):
    """Response from MCP tool call"""
    result: Any
    success: bool
    error: Optional[str] = None


# Agent Models

class AgentType(str, Enum):
    """Types of agents"""
    FILE_TRANSFER = "file_transfer"
    ORCHESTRATOR = "orchestrator"
    MONITOR = "monitor"
    CUSTOM = "custom"


class AgentCreateRequest(BaseModel):
    """Request to create an agent"""
    name: str
    agent_type: AgentType
    capabilities: List[str]
    config: Optional[Dict[str, Any]] = None


class AgentStatus(BaseModel):
    """Agent status"""
    agent_id: str
    name: str
    agent_type: AgentType
    status: str
    created_at: datetime
    last_activity: Optional[datetime] = None
    operations_completed: int = 0


class SwarmCoordinationRequest(BaseModel):
    """Request to coordinate agent swarm"""
    task_description: str
    agents: List[str] = Field(description="List of agent IDs to coordinate")
    config: Optional[Dict[str, Any]] = None


class SwarmCoordinationResponse(BaseModel):
    """Response from swarm coordination"""
    coordination_id: str
    status: str
    agents_assigned: int
    estimated_completion: Optional[datetime] = None
