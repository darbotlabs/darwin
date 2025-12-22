# Darwin Copilot Agent Onboarding Instructions

Welcome! This document will help you understand the Darwin codebase and work efficiently with it.

## Project Overview

Darwin is an agentic fork of WinSCP, a Windows file transfer application. The project consists of:
- **Native C++ core** - File transfer protocol implementations (SFTP, FTP, FTPS, SCP, S3, WebDAV)
- **.NET C# assembly** - Managed API wrapper exposing file operations to .NET applications
- **Future FastAPI layer** - Planned REST API for agent tool calling (not yet implemented)

### Architecture Philosophy

Darwin inherits WinSCP's architecture:
1. Native C++ core handles all protocol implementations and low-level operations
2. A console application (`winscp.com`) provides a command-line interface with XML output
3. The .NET assembly launches the console app as a child process and communicates via XML
4. Future: FastAPI will wrap the .NET assembly to provide RESTful endpoints

## Critical Build Information

### Prerequisites

**This is a Windows-only codebase.** Building requires:

1. **Embarcadero C++Builder 11 Professional** - Commercial IDE for C++ components
   - Used for: All native code in `/source`
   - Project files: `*.cbproj` (C++Builder project format)
   - Group file: `source/WinSCP.groupproj`

2. **Visual Studio 2022 Build Tools** - For MSBuild
   - Used for: Building C++Builder projects via MSBuild
   - Required component: C# 9.0 compiler

3. **.NET SDK** - For .NET assembly
   - Target frameworks: .NET Framework 4.0 and .NET Standard 2.0
   - Build tool: `dotnet` CLI

4. **Additional Tools** (place in `buildtools/tools/`):
   - `nasm.exe` - NASM assembler for cryptographic code
   - `objconv.exe` - Object file format converter

### Build Process

**Main build script**: `build.bat` in repository root

Build order:
1. Libraries (`libs/` directory) - OpenSSL, libssh, expat, neon
2. Native components (`source/` directory) - C++ core, GUI, console
3. .NET assembly (`dotnet/` directory) - C# wrapper

**To build everything:**
```batch
build.bat
```

**To skip .NET assembly:**
```batch
set WITH_DOTNET=0
build.bat
```

**Build outputs:**
- Native executables: `source/` directory (same location as source)
- .NET assembly: `dotnet/bin/Release/` or `dotnet/bin/Debug/`

### Common Build Issues and Workarounds

⚠️ **Issue**: C++Builder not found
- **Cause**: Build script expects C++Builder in `C:\Program Files (x86)\Embarcadero\Studio\22.0`
- **Workaround**: Edit `build.bat` line 15 to set correct path: `set BDS=<your_path>`

⚠️ **Issue**: MSBuild not found
- **Cause**: Visual Studio 2022 Build Tools not installed or in unexpected location
- **Workaround**: Edit `build.bat` lines 20-24 to set correct MSBuild path

⚠️ **Issue**: Missing nasm.exe or objconv.exe
- **Cause**: Tools must be manually downloaded and placed in `buildtools/tools/`
- **Workaround**: Download from official sites and place in correct directory

⚠️ **Issue**: Build fails with cryptic C++Builder errors
- **Cause**: C++Builder projects are sensitive to environment changes
- **Workaround**: 
  - Ensure all paths in `.cbproj` files are correct
  - Check that `INTERM_PATH` and `FINAL_PATH` environment variables are set correctly
  - Try building individual projects first to isolate issues

⚠️ **Note**: **Cannot build on Linux/Mac** - This is Windows-specific code using Windows APIs and Windows-only build tools. The code is NOT cross-platform.

## Directory Structure Deep Dive

### `/source` - Native C++ Code

**Core protocol implementations** (`/source/core/`):
- `SessionData.cpp` - Connection configuration and credentials
- `Terminal.cpp` - Main connection handling, session management
- `SftpFileSystem.cpp` - SFTP protocol implementation
- `FtpFileSystem.cpp` - FTP/FTPS protocol implementation  
- `WebDAVFileSystem.cpp` - WebDAV protocol
- `S3FileSystem.cpp` - Amazon S3 protocol
- `FileOperationProgress.cpp` - Progress tracking for operations
- `CopyParam.cpp` - File transfer parameters and options

**Console interface** (`/source/console/`):
- `Main.cpp` - Command-line interface entry point
- Implements script mode with XML output for .NET assembly communication

**GUI components** (`/source/forms/`):
- Windows forms for the desktop application
- NOT used by .NET assembly or future API

**Third-party code**:
- `/source/putty/` - PuTTY SSH implementation (DO NOT MODIFY without upstream coordination)
- `/source/filezilla/` - FileZilla FTP code (DO NOT MODIFY without upstream coordination)

### `/dotnet` - .NET Assembly API

**Key classes to understand**:

1. **`Session.cs`** - Main API entry point
   - Manages WinSCP console process lifecycle
   - Sends commands and parses XML responses
   - Public methods: `Open()`, `PutFiles()`, `GetFiles()`, `ListDirectory()`, `SynchronizeDirectories()`, etc.

2. **`SessionOptions.cs`** - Connection configuration
   - Properties: `Protocol`, `HostName`, `UserName`, `Password`, `SshHostKeyFingerprint`, etc.

3. **`TransferOptions.cs`** - File transfer settings
   - Transfer mode (binary/text), file permissions, resume support, etc.

4. **`RemoteFileInfo.cs`** - Remote file metadata
   - Name, size, timestamp, permissions, etc.

5. **Internal classes** (`/dotnet/internal/`):
   - `ExeSessionProcess.cs` - Manages WinSCP.com child process
   - `SessionElementLogReader.cs` - Parses XML output from console
   - `ProgressHandler.cs` - Handles progress events

**Important**: The .NET assembly does NOT implement protocols directly. It acts as a wrapper:
1. Launches `winscp.com` (console application) as child process
2. Sends text commands to stdin
3. Receives XML responses from stdout
4. Parses XML and converts to C# objects

### `/libs` - Third-Party Libraries

Pre-compiled libraries used by native code:
- OpenSSL - Cryptography for SSH, TLS
- libssh - SSH protocol support  
- expat - XML parsing
- neon - WebDAV support
- zlib, libbz2 - Compression

**Note**: These are built separately via `libs/buildlibs.bat`

### `/deployment` - Installer Packaging

- Inno Setup scripts (`.iss` files)
- NuGet package specification (`WinSCPnet.nuspec`)
- NOT relevant for development/API work

### `/translations` - UI Localization

- `.ini` files with translated strings
- Only relevant for GUI application, not API

## Working with the Codebase

### If You Need to Modify Protocol Logic

1. **Identify the protocol**: SFTP, FTP, WebDAV, S3, or SCP?
2. **Find the implementation**: `source/core/<Protocol>FileSystem.cpp/h`
3. **Understand the flow**:
   - `Terminal.cpp` manages the session
   - Protocol filesystem classes handle specific operations
   - Changes here require rebuilding native components
4. **Test changes**: Build native code, then test via .NET assembly or console app

### If You Need to Modify .NET API

1. **Locate functionality**: Check `Session.cs` for public methods
2. **Understand command flow**:
   - Method calls in `Session.cs` generate console commands
   - Commands sent to `winscp.com` child process
   - XML responses parsed back into C# objects
3. **Test changes**: Build .NET assembly only (`dotnet build dotnet/WinSCPnet.csproj`)

### If You Need to Add New API Endpoints (Future FastAPI Work)

**Current status**: FastAPI integration does NOT exist yet. Here's the planned approach:

1. **Design principle**: FastAPI should wrap the .NET assembly, NOT reimplement protocols
   - FastAPI Python → calls .NET assembly via pythonnet or subprocess
   - Expose Session methods as REST endpoints
   - Use OpenAPI schemas for LLM tool calling

2. **Example endpoint design**:
   ```python
   @app.post("/session/upload")
   async def upload_files(
       session_id: str,
       local_path: str,
       remote_path: str,
       options: TransferOptions
   ):
       # Call .NET assembly Session.PutFiles()
       # Return operation result as JSON
   ```

3. **Key considerations**:
   - Session management (keep Session objects alive across requests)
   - Authentication (API keys, OAuth, etc.)
   - Error handling (convert .NET exceptions to HTTP status codes)
   - Progress reporting (WebSockets or polling endpoints)
   - File streaming for large transfers

4. **Implementation location**: Create new `/api` or `/fastapi` directory
   - Keep separate from core C++/.NET code
   - Add Python dependencies (`requirements.txt`)
   - Add Docker support for deployment

### Testing Your Changes

**No automated test suite exists** for this codebase. Testing is manual:

1. **For native changes**:
   - Build full project
   - Run `source/WinSCP.exe` (GUI) or `source/WinSCP.com` (console)
   - Manually test affected operations

2. **For .NET changes**:
   - Build .NET assembly
   - Create a test C# console application
   - Reference `WinSCPnet.dll`
   - Write test code using Session API
   - Run and verify behavior

3. **For future API changes**:
   - Use tools like `curl`, Postman, or Python requests
   - Verify OpenAPI schema generation
   - Test error conditions explicitly

### Linting and Code Style

**No formal linters configured**. Follow existing patterns:

- **C++ code**: Follows traditional C++ style with PascalCase for types, camelCase for variables
- **C# code**: Follows .NET conventions (PascalCase for public members)
- **Comments**: Minimal in existing code; add when logic is complex

### Git Workflow

- **Main branch**: Contains stable code
- **Feature branches**: Use descriptive names like `feature/fastapi-upload-endpoint`
- **Commits**: Write clear commit messages explaining WHY, not just WHAT

## Common Pitfalls to Avoid

❌ **Don't** try to build on Linux/Mac - This is Windows-only code

❌ **Don't** modify PuTTY or FileZilla code without careful consideration - These are upstream dependencies

❌ **Don't** implement protocol logic in the .NET assembly - Protocols belong in C++ core

❌ **Don't** assume cross-platform compatibility - Windows APIs are used throughout

❌ **Don't** create breaking changes to Session.cs public API - This would break existing users

❌ **Don't** add heavy dependencies without discussion - Keep the .NET assembly lightweight

✅ **Do** test protocol changes against real servers (SFTP, FTP, S3, etc.)

✅ **Do** handle errors gracefully - File operations fail frequently

✅ **Do** document new API endpoints thoroughly

✅ **Do** preserve backward compatibility when possible

## Quick Reference: Key Files

| File | Purpose |
|------|---------|
| `build.bat` | Main build script |
| `source/WinSCP.groupproj` | C++Builder solution file |
| `source/console/Main.cpp` | Console application entry point |
| `source/core/Terminal.cpp` | Session management |
| `source/core/SftpFileSystem.cpp` | SFTP implementation |
| `dotnet/Session.cs` | .NET API main class |
| `dotnet/WinSCPnet.csproj` | .NET project file |
| `dotnet/internal/ExeSessionProcess.cs` | Process management |

## Getting Help

If you encounter issues:
1. Check build prerequisites are correctly installed
2. Review error messages carefully - C++Builder errors can be cryptic
3. Verify paths in `build.bat` match your system
4. Try building individual components to isolate problems
5. Check Darwin repository issues on GitHub

## Future Roadmap Context

Darwin aims to become an AI-native file transfer framework:
- **Phase 1** (Current): Stable C++/.NET core inherited from WinSCP
- **Phase 2** (Planned): FastAPI REST layer for tool calling
- **Phase 3** (Future): Agent orchestration, multi-session management, advanced automation

When working on the codebase, keep this progression in mind. The goal is to maintain the robust protocol implementations while adding modern API layers for agent integration.

## Summary

Darwin is a mature, complex codebase with:
- ✅ Solid protocol implementations
- ✅ Comprehensive .NET API
- ✅ Windows-only build system
- ⚠️ No automated tests
- ⚠️ Windows-specific tools required
- 🔮 FastAPI layer is planned but not implemented

Take your time to understand the architecture before making changes. The codebase is well-structured but tightly coupled to Windows and requires specific build tools.

Good luck! 🚀
