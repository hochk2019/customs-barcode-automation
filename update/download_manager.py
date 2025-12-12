"""
Download manager for update files.
"""

import logging
import os
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
    
    def _cleanup_partial_file(self, filepath: str) -> None:
        """Remove partial download file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Removed partial file: {filepath}")
        except OSError as e:
            logger.warning(f"Failed to remove partial file: {e}")
    
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
                zip_ref.extractall(target_dir)
            
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
