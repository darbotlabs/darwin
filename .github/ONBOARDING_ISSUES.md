# Darwin Onboarding Issues and Findings

This document tracks issues encountered during the onboarding process and provides context for future developers.

## Date: 2025-12-22

### Environment Information
- **Platform**: Linux (Ubuntu on Azure runner)
- **Available Tools**: .NET SDK 10.0.101, git, standard Unix tools
- **Missing Tools**: All Windows-specific build tools (C++Builder, MSBuild for Windows, nasm, objconv)

## Key Findings

### 1. Build System is Windows-Only

**Issue**: The Darwin codebase cannot be built on Linux or macOS.

**Details**:
- Native code requires **Embarcadero C++Builder 11 Professional** (Windows commercial IDE)
- Build script (`build.bat`) is a Windows batch file
- Project files are `.cbproj` format (C++Builder specific)
- MSBuild configuration targets Windows Visual Studio 2022
- Dependencies on Windows-specific APIs throughout the codebase

**Impact**: 
- Development must be done on Windows machines
- CI/CD pipelines require Windows runners
- Cross-platform development is not feasible without major refactoring

**Workaround**: 
- For documentation-only changes: Can be done on any platform
- For code changes: Requires Windows development environment
- For .NET assembly testing: Might work with .NET on Linux if pre-built native executables are available (untested)

### 2. Missing Build Tools Directory

**Issue**: `buildtools/` directory does not exist in the repository.

**Details**:
- Build script expects `buildtools/tools/nasm.exe` and `buildtools/tools/objconv.exe`
- These tools must be manually downloaded and placed in the correct location
- No documentation on exact versions required

**Recommended Action**:
- Document exact versions of nasm and objconv to use
- Consider adding checksums for verification
- Create `.gitignore` entry for buildtools/ or add download script

### 3. Third-Party Code Integration

**Finding**: Repository includes full source of PuTTY and FileZilla.

**Details**:
- `/source/putty/` - Complete PuTTY SSH client source
- `/source/filezilla/` - FileZilla FTP implementation
- These are upstream dependencies that should be coordinated with their respective projects

**Recommendation**: 
- Document the versions of PuTTY and FileZilla included
- Establish process for updating these dependencies
- Tag any Darwin-specific modifications clearly

### 4. FastAPI Integration - Not Implemented

**Issue**: README and issue description mention FastAPI integration, but no FastAPI code exists.

**Current State**:
- No Python code in the repository (except in third-party libs)
- No `requirements.txt`, `setup.py`, or `pyproject.toml`
- No API endpoint implementations
- No FastAPI dependencies

**Clarification**: FastAPI integration is a **planned feature**, not current functionality.

**Recommendations for Future Implementation**:

1. **Project Structure**:
   ```
   /api
     /darwin_api
       __init__.py
       main.py          # FastAPI application
       routers/
         sessions.py    # Session management endpoints
         transfers.py   # File transfer endpoints
       models/
         schemas.py     # Pydantic models
       services/
         dotnet_bridge.py  # Interface to .NET assembly
     requirements.txt
     Dockerfile
     README.md
   ```

2. **Technology Choices**:
   - **FastAPI**: For REST API framework
   - **pythonnet** or **subprocess**: To call .NET assembly
   - **pydantic**: For request/response schemas
   - **uvicorn**: For ASGI server
   - **pytest**: For API testing

3. **Architecture**:
   ```
   Client Request (HTTP/JSON)
         ↓
   FastAPI Endpoint
         ↓
   .NET Bridge (pythonnet or subprocess)
         ↓
   WinSCP .NET Assembly
         ↓
   winscp.com (native executable)
         ↓
   Protocol Implementation (C++)
   ```

4. **Deployment Considerations**:
   - FastAPI must run on Windows (or have access to Windows VM/container)
   - Native executables must be bundled with API deployment
   - Consider containerization with Windows containers

### 5. No Automated Testing

**Issue**: No test suite exists in the repository.

**Details**:
- No test directories or test files
- No testing framework configuration
- No CI/CD test jobs
- All testing is currently manual

**Impact**: 
- Risk of regressions when making changes
- Difficult to verify functionality without manual testing
- No safety net for refactoring

**Recommendations**:
1. For .NET assembly: Add xUnit or NUnit tests
2. For future FastAPI: Add pytest with test fixtures
3. For integration: Add end-to-end tests with real protocol servers (or mocks)
4. Set up GitHub Actions for automated testing

### 6. .NET Assembly Namespace Inconsistency

**Finding**: The .NET assembly still uses `WinSCP` namespace.

**Details**:
- All C# classes are in `namespace WinSCP`
- Assembly is named `WinSCPnet.dll`
- NuGet package references WinSCP

**Consideration**: 
- Changing namespace would be a **breaking change** for existing users
- Need to decide: Keep WinSCP namespace for compatibility, or rebrand to Darwin?
- If rebranding, consider versioning strategy (Darwin v2.0?)

**Recommendation**: Document this decision explicitly in project documentation

### 7. Documentation Gaps

**Missing Documentation**:
- Protocol-specific configuration examples (FTPS certificates, S3 credentials, etc.)
- Error handling best practices
- Performance tuning guidelines
- Security considerations (credential storage, etc.)
- Migration guide from original WinSCP

**Recommendation**: Create additional documentation files:
- `docs/PROTOCOLS.md` - Protocol-specific guides
- `docs/SECURITY.md` - Security best practices
- `docs/API_REFERENCE.md` - Complete API documentation
- `docs/MIGRATION.md` - For users migrating from WinSCP

### 8. License Considerations

**Finding**: Project uses WinSCP license.

**Details**:
- License file is present (`license.txt`)
- Darwin is a fork, so license inheritance is appropriate
- Need to clarify contribution terms for Darwin-specific additions

**Recommendation**: 
- Review license compatibility for future dependencies (especially Python packages)
- Add `CONTRIBUTING.md` with clear licensing terms
- Ensure compliance with upstream WinSCP license terms

## Validation Checklist

Due to environment limitations (Linux instead of Windows), the following could not be validated:

- [ ] Full build process execution
- [ ] C++Builder project compilation
- [ ] Native executable functionality
- [ ] .NET assembly build on Windows
- [ ] .NET assembly runtime testing
- [ ] Build script error handling
- [ ] Actual build times and resource requirements

## Recommended Next Steps

1. **Immediate** (Documentation):
   - ✅ Create comprehensive copilot-instructions.md
   - ✅ Update README with Darwin branding and future plans
   - ✅ Document build process and requirements
   - ✅ List known issues and workarounds

2. **Short-term** (Infrastructure):
   - Add Windows-based CI/CD pipeline for builds
   - Create automated test framework
   - Document exact tool versions required
   - Add .gitignore for build artifacts

3. **Medium-term** (Feature Development):
   - Design FastAPI integration architecture
   - Create Python wrapper for .NET assembly
   - Implement core API endpoints
   - Add authentication and authorization

4. **Long-term** (Enhancement):
   - Consider namespace migration to Darwin
   - Evaluate cross-platform possibilities (probably not feasible)
   - Add comprehensive monitoring and logging
   - Build agent orchestration capabilities

## Conclusions

Darwin is a well-structured codebase with:
- ✅ Solid foundation from mature WinSCP project
- ✅ Comprehensive protocol support
- ✅ Well-designed .NET API
- ⚠️ Windows-only build system (significant limitation)
- ⚠️ No automated testing
- ⚠️ FastAPI integration is aspirational, not actual
- 🔮 Significant potential for AI agent integration

The onboarding documentation provided in `copilot-instructions.md` should enable future developers to understand and work with the codebase effectively, especially once they have access to a proper Windows development environment.

---

**Document Author**: GitHub Copilot Agent  
**Date**: December 22, 2025  
**Status**: Initial onboarding complete, awaiting Windows environment for build validation
