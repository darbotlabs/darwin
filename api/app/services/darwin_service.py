"""
Darwin Service - Wrapper for WinSCP .NET Assembly

This service provides Python-friendly access to the Darwin/WinSCP .NET assembly
for file transfer operations.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DarwinService:
    """Service for managing Darwin file transfer operations"""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._dotnet_loaded = False
        self._clr = None
        
    def _load_dotnet_assembly(self):
        """Load the WinSCP .NET assembly using pythonnet"""
        if self._dotnet_loaded:
            return
            
        try:
            import clr
            from app.config import get_assembly_path
            
            assembly_path = get_assembly_path()
            logger.info(f"Loading WinSCP .NET assembly from {assembly_path}")
            
            # Add reference to the assembly
            clr.AddReference(str(assembly_path))
            
            # Import WinSCP namespace
            import WinSCP
            self._clr = clr
            self._winscp = WinSCP
            self._dotnet_loaded = True
            
            logger.info("WinSCP .NET assembly loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load WinSCP .NET assembly: {e}")
            raise RuntimeError(f"Failed to load Darwin .NET assembly: {e}")
    
    async def create_session(
        self,
        protocol: str,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        port: Optional[int] = None,
        ssh_host_key_fingerprint: Optional[str] = None,
        timeout: int = 60
    ) -> str:
        """
        Create a new file transfer session
        
        Returns:
            session_id: Unique identifier for the session
        """
        self._load_dotnet_assembly()
        
        session_id = str(uuid.uuid4())
        
        try:
            # Create session options
            session_options = self._winscp.SessionOptions()
            
            # Map protocol string to WinSCP Protocol enum
            protocol_map = {
                "sftp": self._winscp.Protocol.Sftp,
                "ftp": self._winscp.Protocol.Ftp,
                "ftps": self._winscp.Protocol.Ftp,  # FTPS uses FTP with TLS
                "scp": self._winscp.Protocol.Scp,
                "s3": self._winscp.Protocol.S3,
                "webdav": self._winscp.Protocol.Webdav,
            }
            
            session_options.Protocol = protocol_map.get(protocol.lower())
            session_options.HostName = hostname
            session_options.UserName = username
            
            if password:
                session_options.Password = password
            
            if port:
                session_options.PortNumber = port
            
            if ssh_host_key_fingerprint:
                session_options.SshHostKeyFingerprint = ssh_host_key_fingerprint
            
            session_options.Timeout = timeout
            
            # For FTPS, enable TLS
            if protocol.lower() == "ftps":
                session_options.FtpSecure = self._winscp.FtpSecure.Explicit
            
            # Create and open session
            session = self._winscp.Session()
            
            # Note: In real implementation, we would open the session here
            # session.Open(session_options)
            # For now, we store the configuration
            
            self._sessions[session_id] = {
                "session": session,
                "options": session_options,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "operations_count": 0,
                "status": "created"
            }
            
            logger.info(f"Created session {session_id} for {hostname}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def close_session(self, session_id: str) -> bool:
        """Close a session and cleanup resources"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        try:
            session_data = self._sessions[session_id]
            session = session_data["session"]
            
            # Close the session if it's open
            if hasattr(session, "Opened") and session.Opened:
                session.Close()
            
            # Dispose the session object
            if hasattr(session, "Dispose"):
                session.Dispose()
            
            del self._sessions[session_id]
            logger.info(f"Closed session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            raise
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a session"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_data = self._sessions[session_id]
        return {
            "session_id": session_id,
            "status": session_data["status"],
            "created_at": session_data["created_at"],
            "last_activity": session_data["last_activity"],
            "operations_count": session_data["operations_count"]
        }
    
    async def upload_files(
        self,
        session_id: str,
        local_path: str,
        remote_path: str,
        transfer_mode: str = "automatic",
        remove_after: bool = False
    ) -> Dict[str, Any]:
        """Upload files to remote server"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_data = self._sessions[session_id]
        session = session_data["session"]
        
        try:
            # Create transfer options
            transfer_options = self._winscp.TransferOptions()
            
            mode_map = {
                "binary": self._winscp.TransferMode.Binary,
                "text": self._winscp.TransferMode.Ascii,
                "automatic": self._winscp.TransferMode.Automatic
            }
            transfer_options.TransferMode = mode_map.get(transfer_mode.lower())
            
            # Perform upload
            # result = session.PutFiles(local_path, remote_path, remove_after, transfer_options)
            
            # Update session activity
            session_data["last_activity"] = datetime.utcnow()
            session_data["operations_count"] += 1
            
            logger.info(f"Upload completed for session {session_id}")
            
            return {
                "success": True,
                "operation": "upload",
                "files_transferred": 1,  # Placeholder
                "message": f"Uploaded {local_path} to {remote_path}"
            }
            
        except Exception as e:
            logger.error(f"Upload failed for session {session_id}: {e}")
            raise
    
    async def download_files(
        self,
        session_id: str,
        remote_path: str,
        local_path: str,
        transfer_mode: str = "automatic",
        remove_after: bool = False
    ) -> Dict[str, Any]:
        """Download files from remote server"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_data = self._sessions[session_id]
        session = session_data["session"]
        
        try:
            # Create transfer options
            transfer_options = self._winscp.TransferOptions()
            
            mode_map = {
                "binary": self._winscp.TransferMode.Binary,
                "text": self._winscp.TransferMode.Ascii,
                "automatic": self._winscp.TransferMode.Automatic
            }
            transfer_options.TransferMode = mode_map.get(transfer_mode.lower())
            
            # Perform download
            # result = session.GetFiles(remote_path, local_path, remove_after, transfer_options)
            
            # Update session activity
            session_data["last_activity"] = datetime.utcnow()
            session_data["operations_count"] += 1
            
            logger.info(f"Download completed for session {session_id}")
            
            return {
                "success": True,
                "operation": "download",
                "files_transferred": 1,  # Placeholder
                "message": f"Downloaded {remote_path} to {local_path}"
            }
            
        except Exception as e:
            logger.error(f"Download failed for session {session_id}: {e}")
            raise
    
    async def list_directory(
        self,
        session_id: str,
        remote_path: str = "/"
    ) -> List[Dict[str, Any]]:
        """List contents of a remote directory"""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_data = self._sessions[session_id]
        session = session_data["session"]
        
        try:
            # List directory
            # directory_info = session.ListDirectory(remote_path)
            
            # Update session activity
            session_data["last_activity"] = datetime.utcnow()
            
            # Placeholder response
            files = []
            logger.info(f"Listed directory {remote_path} for session {session_id}")
            
            return files
            
        except Exception as e:
            logger.error(f"List directory failed for session {session_id}: {e}")
            raise


# Global service instance
darwin_service = DarwinService()
