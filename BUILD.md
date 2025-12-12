# Build Guide - Creating Standalone Executable

This guide explains how to build a standalone executable for the Customs Barcode Automation system using PyInstaller.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Building the Executable](#building-the-executable)
4. [Testing the Executable](#testing-the-executable)
5. [Distribution](#distribution)
6. [Troubleshooting](#troubleshooting)

## Overview

PyInstaller packages the Python application and all its dependencies into a single directory containing an executable file. This allows users to run the application without installing Python or any dependencies.

### What Gets Packaged

- Python interpreter
- All Python dependencies (pyodbc, selenium, requests, etc.)
- Application code (all modules)
- Configuration sample file
- Documentation files

### What's NOT Included

- WebDriver (chromedriver.exe or msedgedriver.exe) - must be provided separately
- User configuration (config.ini) - created by user
- Database (ECUS5) - accessed remotely
- PDF files - created at runtime

## Prerequisites

### Development Environment

- Python 3.8 or higher
- All application dependencies installed
- PyInstaller (will be installed automatically by build script)
- Windows 10 or later

### Install PyInstaller

If not already installed:

```cmd
python -m pip install pyinstaller
```

### Verify Installation

```cmd
python -m PyInstaller --version
```

Expected output: `5.x.x` or higher

## Building the Executable

### Method 1: Using Build Script (Recommended)

#### Batch Script

```cmd
build_exe.bat
```

#### PowerShell Script

```powershell
.\build_exe.ps1
```

The script will:
1. Install PyInstaller if needed
2. Clean previous build directories
3. Build the executable using the spec file
4. Copy documentation files
5. Create a distribution ZIP file

### Method 2: Manual Build

#### Step 1: Clean Previous Builds

```cmd
rmdir /s /q build
rmdir /s /q dist
```

#### Step 2: Run PyInstaller

```cmd
python -m PyInstaller customs_automation.spec --clean
```

#### Step 3: Copy Additional Files

```cmd
copy config.ini.sample dist\CustomsAutomation\
copy README.md dist\CustomsAutomation\
copy USER_GUIDE.md dist\CustomsAutomation\
copy DEPLOYMENT.md dist\CustomsAutomation\
mkdir dist\CustomsAutomation\logs
```

#### Step 4: Create Distribution Package

```cmd
cd dist
powershell Compress-Archive -Path CustomsAutomation -DestinationPath CustomsAutomation.zip
cd ..
```

## Build Output

After a successful build, you'll have:

```
dist/
└── CustomsAutomation/
    ├── CustomsAutomation.exe       # Main executable
    ├── config.ini.sample           # Configuration template
    ├── README.md                   # User documentation
    ├── USER_GUIDE.md              # Detailed user guide
    ├── DEPLOYMENT.md              # Deployment instructions
    ├── logs/                      # Log directory (empty)
    ├── _internal/                 # PyInstaller internals
    │   ├── python3x.dll
    │   ├── *.pyd files
    │   └── ... (many dependency files)
    └── ... (other PyInstaller files)

dist/CustomsAutomation.zip         # Distribution package
```

## Testing the Executable

### Basic Test

1. Navigate to the dist directory:
   ```cmd
   cd dist\CustomsAutomation
   ```

2. Create configuration:
   ```cmd
   copy config.ini.sample config.ini
   ```

3. Edit `config.ini` with test database credentials

4. Run the executable:
   ```cmd
   CustomsAutomation.exe
   ```

5. Verify:
   - GUI window opens
   - No error messages in log panel
   - Configuration loads successfully

### Full Test

1. Place WebDriver in the same directory:
   ```cmd
   copy C:\path\to\chromedriver.exe .
   ```

2. Run the executable

3. Test database connection:
   - Select Manual mode
   - Click "Run Once"
   - Check log panel for connection success

4. Test barcode retrieval:
   - Ensure database has eligible declarations
   - Click "Run Once"
   - Verify PDFs are created in output directory

### Test on Clean Machine

For thorough testing, test on a machine without Python installed:

1. Copy the entire `CustomsAutomation` directory to the test machine
2. Add WebDriver (chromedriver.exe or msedgedriver.exe)
3. Create and configure config.ini
4. Run CustomsAutomation.exe
5. Verify all functionality works

## Distribution

### Creating Distribution Package

The build script automatically creates `CustomsAutomation.zip` containing:
- Executable and all dependencies
- Documentation files
- Configuration sample
- Empty logs directory

### Distribution Checklist

Before distributing:

- [ ] Test executable on clean Windows machine
- [ ] Verify all dependencies are included
- [ ] Include README.md with installation instructions
- [ ] Include USER_GUIDE.md for end users
- [ ] Include DEPLOYMENT.md for IT staff
- [ ] Include config.ini.sample
- [ ] Document WebDriver requirement
- [ ] Test with both ChromeDriver and EdgeDriver
- [ ] Verify database connectivity
- [ ] Test barcode retrieval (API and web scraping)

### Distribution Methods

**Method 1: ZIP File**
- Distribute `CustomsAutomation.zip`
- Users extract and run
- Requires WebDriver installation

**Method 2: Installer**
- Use NSIS or Inno Setup to create installer
- Can include WebDriver in installer
- Provides uninstall capability
- More professional appearance

**Method 3: Network Share**
- Place on shared network drive
- Users run directly from network
- Centralized updates
- Requires good network connectivity

## Troubleshooting

### Build Issues

**Problem**: "PyInstaller not found"

**Solution**:
```cmd
python -m pip install pyinstaller
```

**Problem**: "Module not found" during build

**Solution**:
1. Add missing module to `hiddenimports` in `customs_automation.spec`
2. Rebuild

**Problem**: Build succeeds but executable crashes

**Solution**:
1. Run with console enabled to see errors:
   - Edit `customs_automation.spec`
   - Change `console=False` to `console=True`
   - Rebuild
2. Check error messages
3. Add missing dependencies to spec file

### Runtime Issues

**Problem**: "DLL load failed" error

**Solution**:
1. Ensure Visual C++ Redistributable is installed
2. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
3. Install and retry

**Problem**: "WebDriver not found"

**Solution**:
1. Download ChromeDriver or EdgeDriver
2. Place in same directory as executable
3. Or add to system PATH

**Problem**: Executable is very large (>100MB)

**Solution**:
This is normal. PyInstaller includes:
- Python interpreter (~30MB)
- All dependencies (~50MB)
- Application code (~10MB)
- PyInstaller overhead (~10MB)

**Problem**: Antivirus flags executable

**Solution**:
1. This is common with PyInstaller executables
2. Add exception in antivirus software
3. Or sign the executable with code signing certificate

### Performance Issues

**Problem**: Slow startup time

**Solution**:
1. This is normal for PyInstaller executables (2-5 seconds)
2. Consider using `--onefile` option (creates single EXE but slower)
3. Or keep current `--onedir` option (faster but multiple files)

**Problem**: Large memory usage

**Solution**:
1. PyInstaller executables use more memory than Python scripts
2. This is expected behavior
3. Ensure target machines have adequate RAM (4GB minimum)

## Advanced Configuration

### Customizing the Build

Edit `customs_automation.spec` to customize:

**Add Icon**:
```python
exe = EXE(
    ...
    icon='path/to/icon.ico',
    ...
)
```

**Create Single File**:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Add this
    a.zipfiles,  # Add this
    a.datas,     # Add this
    [],
    name='CustomsAutomation',
    ...
)
```

**Add Version Information**:
```python
exe = EXE(
    ...
    version='version_info.txt',
    ...
)
```

### Optimizing Size

**Exclude Unnecessary Modules**:
```python
excludes=['pytest', 'hypothesis', 'test', 'unittest'],
```

**Use UPX Compression**:
```python
upx=True,
upx_exclude=[],
```

**Remove Debug Symbols**:
```python
strip=True,
```

### Including WebDriver

To bundle WebDriver with the executable:

1. Download ChromeDriver or EdgeDriver
2. Add to spec file:
```python
datas = [
    ('chromedriver.exe', '.'),
    ('config.ini.sample', '.'),
    ...
]
```
3. Rebuild

**Note**: WebDriver must match the browser version on target machines.

## Continuous Integration

### Automated Builds

For automated builds in CI/CD:

```yaml
# Example GitHub Actions workflow
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build executable
        run: python -m PyInstaller customs_automation.spec --clean
      - name: Create distribution
        run: |
          Copy-Item config.ini.sample dist\CustomsAutomation\
          Copy-Item README.md dist\CustomsAutomation\
          Compress-Archive -Path dist\CustomsAutomation -DestinationPath CustomsAutomation.zip
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: CustomsAutomation
          path: CustomsAutomation.zip
```

## Version Management

### Versioning the Executable

Create `version_info.txt`:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Customs Department'),
        StringStruct(u'FileDescription', u'Customs Barcode Automation'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'CustomsAutomation'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2023'),
        StringStruct(u'OriginalFilename', u'CustomsAutomation.exe'),
        StringStruct(u'ProductName', u'Customs Barcode Automation'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

Add to spec file:
```python
exe = EXE(
    ...
    version='version_info.txt',
    ...
)
```

## Support

For build issues:
1. Check PyInstaller documentation: https://pyinstaller.org/
2. Review error messages carefully
3. Test on clean machine
4. Check antivirus logs
5. Verify all dependencies are installed

## Appendix

### Build Environment

Recommended build environment:
- Windows 10 or later (64-bit)
- Python 3.8 or higher
- 8GB RAM minimum
- 2GB free disk space
- Fast CPU for quicker builds

### Build Time

Typical build times:
- First build: 2-5 minutes
- Subsequent builds: 1-3 minutes
- Clean build: 2-5 minutes

### File Sizes

Approximate sizes:
- Executable: 5-10 MB
- Dependencies: 80-100 MB
- Total distribution: 90-110 MB
- ZIP file: 30-40 MB (compressed)
