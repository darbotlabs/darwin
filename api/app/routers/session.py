"""
Session API Router - File transfer session management
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionStatus,
    FileUploadRequest,
    FileDownloadRequest,
    FileListRequest,
    FileListResponse,
    OperationResult,
    RemoteFileInfo
)
from app.services.darwin_service import darwin_service
from datetime import datetime

router = APIRouter()


@router.post("/session/create", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SessionCreateRequest):
    """
    Create a new file transfer session
    
    - **protocol**: File transfer protocol (sftp, ftp, ftps, scp, s3, webdav)
    - **hostname**: Server hostname or IP address
    - **username**: Authentication username
    - **password**: Authentication password (optional for key-based auth)
    - **ssh_host_key_fingerprint**: SSH host key fingerprint (required for SFTP/SCP)
    """
    try:
        session_id = await darwin_service.create_session(
            protocol=request.options.protocol.value,
            hostname=request.options.hostname,
            username=request.options.username,
            password=request.options.password,
            port=request.options.port,
            ssh_host_key_fingerprint=request.options.ssh_host_key_fingerprint,
            timeout=request.options.timeout
        )
        
        return SessionCreateResponse(
            session_id=session_id,
            status="created",
            created_at=datetime.utcnow(),
            message=f"Session created successfully for {request.options.hostname}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/session/{session_id}/status", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """Get the status of an active session"""
    try:
        session_status = await darwin_service.get_session_status(session_id)
        return SessionStatus(**session_status)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_session(session_id: str):
    """Close an active session and cleanup resources"""
    try:
        await darwin_service.close_session(session_id)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close session: {str(e)}"
        )


@router.post("/session/{session_id}/upload", response_model=OperationResult)
async def upload_files(session_id: str, request: FileUploadRequest):
    """
    Upload files to remote server
    
    - **local_path**: Local file or directory path (wildcards supported)
    - **remote_path**: Remote destination directory
    - **transfer_mode**: Transfer mode (binary, text, automatic)
    - **remove_after_upload**: Delete local files after successful upload
    """
    try:
        result = await darwin_service.upload_files(
            session_id=session_id,
            local_path=request.local_path,
            remote_path=request.remote_path,
            transfer_mode=request.options.transfer_mode.value if request.options else "automatic",
            remove_after=request.remove_after_upload
        )
        
        return OperationResult(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/session/{session_id}/download", response_model=OperationResult)
async def download_files(session_id: str, request: FileDownloadRequest):
    """
    Download files from remote server
    
    - **remote_path**: Remote file or directory path (wildcards supported)
    - **local_path**: Local destination directory
    - **transfer_mode**: Transfer mode (binary, text, automatic)
    - **remove_after_download**: Delete remote files after successful download
    """
    try:
        result = await darwin_service.download_files(
            session_id=session_id,
            remote_path=request.remote_path,
            local_path=request.local_path,
            transfer_mode=request.options.transfer_mode.value if request.options else "automatic",
            remove_after=request.remove_after_download
        )
        
        return OperationResult(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


@router.post("/session/{session_id}/list", response_model=FileListResponse)
async def list_directory(session_id: str, request: FileListRequest):
    """
    List contents of a remote directory
    
    - **remote_path**: Remote directory path (default: /)
    """
    try:
        files = await darwin_service.list_directory(
            session_id=session_id,
            remote_path=request.remote_path
        )
        
        return FileListResponse(
            path=request.remote_path,
            files=[RemoteFileInfo(**f) for f in files],
            count=len(files)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List directory failed: {str(e)}"
        )
