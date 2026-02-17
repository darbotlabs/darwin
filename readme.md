# Darwin

Darwin is an agentic fork of WinSCP, designed to provide intelligent file transfer capabilities through a powerful agent framework. It supports SFTP, FTP, FTPS, SCP, S3, WebDAV and local-to-local file transfers for Windows. Darwin enhances productivity with automation options including .NET assembly scripting, batch file operations, and planned FastAPI integration for modern tool calling and agent orchestration.

## Features

- **Multi-Protocol Support**: SFTP, FTP, FTPS, SCP, S3, WebDAV, and local file operations
- **.NET Assembly**: Comprehensive C# API for programmatic file operations
- **FastAPI REST Server**: Production-ready API with OpenAPI documentation
- **MCP Integration**: Model Context Protocol for seamless LLM tool calling
- **Agent Swarm Framework**: Coordinate multiple agents for parallel operations
- **Agentic Framework**: Designed for AI agent integration and automation
- **File Operations**: Upload, download, synchronization, and directory management
- **Interactive Examples**: Jupyter notebooks, Adaptive Cards, and agent scenarios

## Building Darwin

### Prerequisites

To build Darwin you need:
- [Embarcadero C++Builder 11 Professional](https://www.embarcadero.com/products/cbuilder) (for native components)
- [Build Tools for Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) (for C# 9.0 and MSBuild)
- [.NET SDK](https://dotnet.microsoft.com/download) (for building the .NET assembly)
- [nasm](https://www.nasm.us/) - store executable to `buildtools/tools/nasm.exe`
- [Object file converter](https://www.agner.org/optimize/#objconv) - store to `buildtools/tools/objconv.exe`

### Build Instructions

To build Darwin from source, use the provided build script:

```bash
build.bat
```

The build process:
1. Builds native libraries from `/libs` directory
2. Compiles C++ components using C++Builder
3. Builds the .NET assembly using MSBuild and dotnet CLI

**Note**: Building requires Windows with the above prerequisites installed. The build outputs are placed in the respective `bin` directories within each component folder.

## Directory Structure

```
/source             Project files for all native libraries and executables
  /components       Native Darwin visual components
  /console          Console interface application
  /core             Core (non-visual) Darwin functionality
                    Contains protocol implementations: SSH, SFTP, FTP, 
                    WebDAV, S3, SCP
  /dragext          Drag & drop shell extension
  /filezilla        FileZilla FTP client source code (3rd party)
  /forms            Visual components (dialogs and windows)
  /packages         General visual components (custom and 3rd party)
  /putty            PuTTY SSH client source code (3rd party)
  /resource         Resource strings for UI
  /windows          Additional Windows-specific sources

/dotnet             Darwin .NET assembly source code
                    Provides C# API for programmatic file operations
                    Key classes: Session, SessionOptions, TransferOptions

/api                FastAPI server (NEW!)
  /app              FastAPI application and routers
    /models         Pydantic data models
    /routers        API endpoint handlers (session, MCP, agents)
    /services       Business logic (Darwin, MCP, Agent services)
  /examples         Usage examples
    /notebooks      Jupyter notebooks
    /adaptive_cards Adaptive Card templates
    /agent_scenarios Agent coordination examples
  /tests            Test suite
  /dashboard        Monitoring dashboard UI
                    
/docs/wiki          Jekyll-based documentation wiki

/libs               Third-party libraries (OpenSSL, libssh, expat, neon)
/deployment         Inno Setup scripts for creating installer packages
/translations       UI translations for multiple languages
/buildtools         Build utilities (nasm, objconv - not in repo)
```

## Using the .NET Assembly

The Darwin .NET assembly provides a comprehensive API for file operations:

```csharp
using WinSCP;

// Setup session options
SessionOptions sessionOptions = new SessionOptions
{
    Protocol = Protocol.Sftp,
    HostName = "example.com",
    UserName = "user",
    Password = "password",
};

// Connect and perform operations
using (Session session = new Session())
{
    session.Open(sessionOptions);
    
    // Upload files
    TransferOptions transferOptions = new TransferOptions();
    transferOptions.TransferMode = TransferMode.Binary;
    
    TransferOperationResult transferResult;
    transferResult = session.PutFiles(@"C:\local\*", "/remote/path/", 
                                      false, transferOptions);
    
    transferResult.Check(); // Throws on error
}
```

## FastAPI Server (New!)

Darwin now includes a production-ready FastAPI server that exposes all file transfer operations as RESTful endpoints with AI agent capabilities:

### Features
- **RESTful API**: All file operations accessible via HTTP endpoints
- **MCP Support**: Model Context Protocol integration for LLM tool calling
- **Agent Swarms**: Coordinate multiple agents for parallel and distributed operations
- **OpenAPI Documentation**: Auto-generated interactive API docs at `/docs`
- **Session Management**: Secure session handling with configurable timeouts
- **Adaptive Cards**: Pre-built UI templates for Microsoft Teams and bot integration
- **Jupyter Integration**: Interactive notebooks with examples
- **Dashboard**: Real-time monitoring UI for sessions and agents

### Quick Start

```bash
# Install dependencies
cd api
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start the server
python -m uvicorn app.main:app --reload
```

Access the API at `http://localhost:8000` and documentation at `http://localhost:8000/docs`.

### Example Usage

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

# Create session
response = client.post("/api/v1/session/create", json={
    "options": {
        "protocol": "sftp",
        "hostname": "example.com",
        "username": "user",
        "password": "password"
    }
})
session_id = response.json()["session_id"]

# Upload file
client.post(f"/api/v1/session/{session_id}/upload", json={
    "local_path": "/path/to/file.txt",
    "remote_path": "/remote/destination/"
})
```

See the [API README](api/README.md) for detailed documentation.

## License

Darwin inherits the WinSCP license. See the file [`license.txt`](license.txt) for complete license conditions.

## Contributing

Darwin is focused on becoming a premier agentic file transfer framework. Contributions are welcome, particularly in:
- Agent swarm coordination improvements
- Additional MCP tool definitions
- Performance optimizations
- Protocol support enhancements
- Dashboard UI enhancements
- Example scenarios and use cases

## Links

- Original WinSCP Project: https://winscp.net/
- Darwin Repository: https://github.com/darbotlabs/darwin

[![NuGet](https://img.shields.io/nuget/v/WinSCP.svg)](https://www.nuget.org/packages/WinSCP/)
