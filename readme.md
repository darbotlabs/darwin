# Darwin

Darwin is an agentic fork of WinSCP, designed to provide intelligent file transfer capabilities through a powerful agent framework. It supports SFTP, FTP, FTPS, SCP, S3, WebDAV and local-to-local file transfers for Windows. Darwin enhances productivity with automation options including .NET assembly scripting, batch file operations, and planned FastAPI integration for modern tool calling and agent orchestration.

## Features

- **Multi-Protocol Support**: SFTP, FTP, FTPS, SCP, S3, WebDAV, and local file operations
- **.NET Assembly**: Comprehensive C# API for programmatic file operations
- **Agentic Framework**: Designed for AI agent integration and automation
- **File Operations**: Upload, download, synchronization, and directory management
- **Future FastAPI Integration**: Planned REST API layer for tool calling and agent orchestration

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

## Future Development: FastAPI Integration

Darwin is planned to include a FastAPI-based REST API layer that will expose all file transfer operations as tool-callable endpoints for AI agent integration. This will enable:

- RESTful endpoints for all file operations (upload, download, list, delete, sync)
- OpenAPI/Swagger documentation for easy agent integration
- Authentication and session management via API tokens
- Streaming support for large file transfers
- WebSocket support for real-time operation status
- Tool calling schemas for LLM integration

**Current Status**: The core file transfer functionality exists in the .NET assembly. FastAPI wrapper development is planned for future releases.

## License

Darwin inherits the WinSCP license. See the file [`license.txt`](license.txt) for complete license conditions.

## Contributing

Darwin is focused on becoming a premier agentic file transfer framework. Contributions are welcome, particularly in:
- FastAPI integration layer development
- Agent orchestration capabilities
- API endpoint design for tool calling
- Performance optimizations
- Protocol support enhancements

## Links

- Original WinSCP Project: https://winscp.net/
- Darwin Repository: https://github.com/darbotlabs/darwin

[![NuGet](https://img.shields.io/nuget/v/WinSCP.svg)](https://www.nuget.org/packages/WinSCP/)
