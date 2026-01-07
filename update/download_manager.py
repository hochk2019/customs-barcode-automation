"""
Download manager for update files.
"""

import hashlib
import logging
import os
import re
import tempfile
import time
import zipfile
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Error during download."""
    pass


class DownloadCancelledError(Exception):
    """Download was cancelled by user."""
    pass


class DownloadManager:
    """Manage file downloads with progress tracking."""
    
    def __init__(self, download_dir: str = None):
        """
        Initialize download manager.
        
        Args:
            download_dir: Directory to save downloads (default: temp directory)
        """
        self.download_dir = download_dir or tempfile.gettempdir()
        self._cancel_flag = False
    
    def download_file(
        self,
        url: str,
        filename: str,
        expected_size: int = None,
        progress_callback: Callable[[int, int, float], None] = None
    ) -> str:
        """
        Download file with progress tracking.
        
        Args:
            url: URL to download from
            filename: Name for the downloaded file
            expected_size: Expected file size for verification
            progress_callback: Callback(downloaded_bytes, total_bytes, speed_bps)
            
        Returns:
            Path to downloaded file
            
        Raises:
            DownloadError: If download fails
            DownloadCancelledError: If download is cancelled
        """
        import requests
        
        self._cancel_flag = False
        filepath = os.path.join(self.download_dir, filename)
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            if expected_size and total_size == 0:
                total_size = expected_size
            
            downloaded = 0
            start_time = time.time()
            last_callback_time = start_time
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._cancel_flag:
                        f.close()
                        self._cleanup_partial_file(filepath)
                        raise DownloadCancelledError("Download cancelled by user")
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Calculate speed and call progress callback
                        current_time = time.time()
                        if progress_callback and (current_time - last_callback_time) >= 0.1:
                            elapsed = current_time - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            progress_callback(downloaded, total_size, speed)
                            last_callback_time = current_time
            
            # Final progress callback
            if progress_callback:
                elapsed = time.time() - start_time
                speed = downloaded / elapsed if elapsed > 0 else 0
                progress_callback(downloaded, total_size, speed)
            
            # Verify file size
            if expected_size and not self.verify_file(filepath, expected_size):
                self._cleanup_partial_file(filepath)
                raise DownloadError(f"File size mismatch. Expected {expected_size}, got {os.path.getsize(filepath)}")
            
            logger.info(f"Download complete: {filepath}")
            return filepath
            
        except DownloadCancelledError:
            raise
        except requests.RequestException as e:
            self._cleanup_partial_file(filepath)
            raise DownloadError(f"Download failed: {e}")
        except Exception as e:
            self._cleanup_partial_file(filepath)
            raise DownloadError(f"Download failed: {e}")
    
    def cancel_download(self) -> None:
        """Cancel the current download."""
        self._cancel_flag = True
        logger.info("Download cancellation requested")
    
    def verify_file(self, filepath: str, expected_size: int) -> bool:
        """
        Verify downloaded file size.
        
        Args:
            filepath: Path to file
            expected_size: Expected file size in bytes
            
        Returns:
            True if file size matches expected
        """
        try:
            actual_size = os.path.getsize(filepath)
            return actual_size == expected_size
        except OSError:
            return False

    def download_checksum_file(self, url: str, filename: str = None) -> Optional[str]:
        """
        Download checksum file to the download directory.

        Args:
            url: URL to checksum file
            filename: Optional filename override

        Returns:
            Path to checksum file or None on failure
        """
        import requests

        if not url:
            return None

        if not filename:
            filename = os.path.basename(url) or "update.sha256"

        filepath = os.path.join(self.download_dir, filename)
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(response.content)
            logger.info(f"Checksum file downloaded: {filepath}")
            return filepath
        except Exception as e:
            logger.warning(f"Failed to download checksum file: {e}")
            return None

    def parse_sha256_file(self, filepath: str) -> Optional[str]:
        """
        Parse sha256 checksum value from a checksum file.

        Args:
            filepath: Path to checksum file

        Returns:
            Hex digest string or None if not found
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except OSError:
            return None

        return self._extract_sha256_from_text(content)

    def _extract_sha256_from_text(self, content: str) -> Optional[str]:
        """Extract the first 64-hex sha256 hash from content."""
        if not content:
            return None
        match = re.search(r"\b[a-fA-F0-9]{64}\b", content)
        if match:
            return match.group(0).lower()
        return None

    def compute_sha256(self, filepath: str) -> str:
        """
        Compute sha256 checksum for a file.

        Args:
            filepath: Path to file

        Returns:
            Hex digest string
        """
        digest = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                digest.update(chunk)
        return digest.hexdigest()

    def verify_checksum(self, filepath: str, checksum_url: str) -> tuple:
        """
        Verify file checksum using a remote .sha256 file.

        Args:
            filepath: Path to downloaded file
            checksum_url: URL to checksum file

        Returns:
            (ok, reason, expected, actual)
        """
        if not checksum_url:
            return True, "no_checksum", "", ""

        checksum_path = self.download_checksum_file(checksum_url)
        if not checksum_path:
            return False, "download_failed", "", ""

        expected = self.parse_sha256_file(checksum_path)
        if not expected:
            return False, "parse_failed", "", ""

        try:
            actual = self.compute_sha256(filepath)
        except OSError as e:
            logger.warning(f"Failed to read downloaded file for checksum: {e}")
            return False, "read_failed", expected, ""

        if actual.lower() != expected.lower():
            return False, "mismatch", expected, actual

        logger.info("Checksum verified successfully")
        return True, "ok", expected, actual
    
    def _cleanup_partial_file(self, filepath: str) -> None:
        """Remove partial download file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Removed partial file: {filepath}")
        except OSError as e:
            logger.warning(f"Failed to remove partial file: {e}")

    def _is_within_directory(self, base_dir: str, target_path: str) -> bool:
        """Return True when target_path is inside base_dir."""
        base_dir = os.path.abspath(base_dir)
        target_path = os.path.abspath(target_path)
        return os.path.commonpath([base_dir, target_path]) == base_dir
    
    def save_pending_installer(self, filepath: str, config_manager) -> None:
        """
        Save pending installer path to config.
        
        Args:
            filepath: Path to the downloaded installer
            config_manager: Configuration manager to save to
        """
        if config_manager:
            try:
                config_manager.set('Update', 'pending_installer', filepath)
                logger.info(f"Saved pending installer: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to save pending installer: {e}")
    
    def clear_pending_installer(self, config_manager) -> None:
        """
        Clear pending installer from config.
        
        Args:
            config_manager: Configuration manager to clear from
        """
        if config_manager:
            try:
                config_manager.set('Update', 'pending_installer', '')
                logger.info("Cleared pending installer")
            except Exception as e:
                logger.warning(f"Failed to clear pending installer: {e}")
    
    def get_pending_installer(self, config_manager) -> Optional[str]:
        """
        Get pending installer path from config.
        
        Args:
            config_manager: Configuration manager to read from
            
        Returns:
            Path to pending installer or None
        """
        if config_manager:
            try:
                path = config_manager.get('Update', 'pending_installer', fallback='')
                if path and os.path.exists(path):
                    return path
            except Exception as e:
                logger.warning(f"Failed to get pending installer: {e}")
        return None
    
    def extract_zip(self, zip_path: str, extract_dir: str = None) -> str:
        """
        Extract ZIP file to directory.
        
        Args:
            zip_path: Path to ZIP file
            extract_dir: Directory to extract to (default: same as ZIP location)
            
        Returns:
            Path to extracted directory
            
        Raises:
            DownloadError: If extraction fails
        """
        try:
            if extract_dir is None:
                extract_dir = os.path.dirname(zip_path)
            
            # Create extraction directory with ZIP filename (without extension)
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            target_dir = os.path.join(extract_dir, zip_name)
            
            logger.info(f"Extracting {zip_path} to {target_dir}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    dest_path = os.path.join(target_dir, member.filename)
                    if not self._is_within_directory(target_dir, dest_path):
                        raise DownloadError(f"Unsafe path in zip: {member.filename}")
                    zip_ref.extract(member, target_dir)
            
            logger.info(f"Extraction complete: {target_dir}")
            return target_dir
            
        except zipfile.BadZipFile as e:
            raise DownloadError(f"Invalid ZIP file: {e}")
        except Exception as e:
            raise DownloadError(f"Extraction failed: {e}")
    
    def is_zip_file(self, filepath: str) -> bool:
        """
        Check if file is a ZIP archive.
        
        Args:
            filepath: Path to file
            
        Returns:
            True if file is a valid ZIP
        """
        return filepath.lower().endswith('.zip') and zipfile.is_zipfile(filepath)
    
    def create_update_script(self, zip_path: str, target_dir: str, exe_name: str = "CustomsAutomation.exe") -> str:
        """
        Create a batch script to perform the update after app closes.
        
        The script will:
        1. Wait for the current app to close
        2. Extract ZIP contents to target directory (overwrite)
        3. Delete the ZIP file
        4. Restart the application
        
        Args:
            zip_path: Path to the downloaded ZIP file
            target_dir: Directory where the app is installed (to extract to)
            exe_name: Name of the executable to restart
            
        Returns:
            Path to the created batch script
        """
        import sys
        
        # Get current process ID
        current_pid = os.getpid()
        
        # Create batch script content
        # Important: Backup config.ini and .encryption_key before update, restore after
        script_content = f'''@echo off
chcp 65001 >nul
echo ========================================
echo   Đang cập nhật ứng dụng...
echo ========================================
echo.

REM Wait for the main application to close
echo Đang đợi ứng dụng đóng...
:waitloop
tasklist /FI "PID eq {current_pid}" 2>NUL | find /I "{current_pid}" >NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >nul
    goto waitloop
)

echo Ứng dụng đã đóng. Bắt đầu cập nhật...
timeout /t 2 /nobreak >nul

REM Backup important user files before update
echo Đang sao lưu cấu hình...
set "BACKUP_DIR=%TEMP%\\customs_backup_%RANDOM%"
mkdir "%BACKUP_DIR%" 2>nul
if exist "{target_dir}\\config.ini" copy /Y "{target_dir}\\config.ini" "%BACKUP_DIR%\\config.ini" >nul
if exist "{target_dir}\\.encryption_key" copy /Y "{target_dir}\\.encryption_key" "%BACKUP_DIR%\\.encryption_key" >nul
if exist "{target_dir}\\preferences.json" copy /Y "{target_dir}\\preferences.json" "%BACKUP_DIR%\\preferences.json" >nul
if exist "{target_dir}\\data" xcopy /E /I /Y "{target_dir}\\data" "%BACKUP_DIR%\\data" >nul 2>&1

REM Extract ZIP to temp directory first (handle nested structure)
echo Đang giải nén bản cập nhật...
set "TEMP_EXTRACT=%TEMP%\\customs_extract_%RANDOM%"
powershell -Command "Expand-Archive -Path '{zip_path}' -DestinationPath '%TEMP_EXTRACT%' -Force"

if %ERRORLEVEL% NEQ 0 (
    echo Lỗi: Không thể giải nén file cập nhật!
    pause
    exit /b 1
)

REM Check if ZIP has nested folder structure and copy files to target
echo Đang cài đặt bản cập nhật...
REM If there's a subfolder (e.g., CustomsAutomation), copy from there
for /d %%D in ("%TEMP_EXTRACT%\\*") do (
    if exist "%%D\\{exe_name}" (
        xcopy /E /Y "%%D\\*" "{target_dir}\\" >nul
        goto :done_copy
    )
)
REM Otherwise copy directly
xcopy /E /Y "%TEMP_EXTRACT%\\*" "{target_dir}\\" >nul
:done_copy

REM Clean up temp extract
rmdir /s /q "%TEMP_EXTRACT%" 2>nul

REM Restore user configuration files (don't overwrite with defaults from ZIP)
echo Đang khôi phục cấu hình...
if exist "%BACKUP_DIR%\\config.ini" copy /Y "%BACKUP_DIR%\\config.ini" "{target_dir}\\config.ini" >nul
if exist "%BACKUP_DIR%\\.encryption_key" copy /Y "%BACKUP_DIR%\\.encryption_key" "{target_dir}\\.encryption_key" >nul
if exist "%BACKUP_DIR%\\preferences.json" copy /Y "%BACKUP_DIR%\\preferences.json" "{target_dir}\\preferences.json" >nul
if exist "%BACKUP_DIR%\\data" xcopy /E /I /Y "%BACKUP_DIR%\\data" "{target_dir}\\data" >nul 2>&1

REM Clean up backup
rmdir /s /q "%BACKUP_DIR%" 2>nul

REM Delete the ZIP file
echo Đang dọn dẹp...
del /f /q "{zip_path}" 2>nul

REM Restart the application
echo Khởi động lại ứng dụng...
timeout /t 1 /nobreak >nul
start "" "{os.path.join(target_dir, exe_name)}"

REM Delete this script
del /f /q "%~f0" 2>nul
'''
        
        # Save script to temp directory
        script_path = os.path.join(tempfile.gettempdir(), "customs_update.bat")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Created update script: {script_path}")
        return script_path
    
    def run_update_and_restart(self, zip_path: str, target_dir: str, exe_name: str = "CustomsAutomation.exe") -> bool:
        """
        Create and run the update script, then signal the app to close.
        
        Args:
            zip_path: Path to the downloaded ZIP file
            target_dir: Directory where the app is installed
            exe_name: Name of the executable
            
        Returns:
            True if script was started successfully
        """
        import subprocess
        
        try:
            # Create the update script
            script_path = self.create_update_script(zip_path, target_dir, exe_name)
            
            # Run the script in a new process (detached)
            # Use CREATE_NEW_CONSOLE to show progress to user
            CREATE_NEW_CONSOLE = 0x00000010
            subprocess.Popen(
                ['cmd', '/c', script_path],
                creationflags=CREATE_NEW_CONSOLE,
                close_fds=True
            )
            
            logger.info("Update script started, app will close for update")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start update script: {e}")
            return False
    
    def get_app_directory(self) -> str:
        """
        Get the directory where the application is installed.
        
        Returns:
            Path to the application directory
        """
        import sys
        
        # If running as frozen exe (PyInstaller)
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            # Running as script - use current working directory
            return os.getcwd()
