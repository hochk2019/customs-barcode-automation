"""
Update checker for GitHub releases.
"""

import logging
import os
from typing import Optional, List

from update.models import UpdateInfo
from update.version_comparator import VersionComparator

logger = logging.getLogger(__name__)


class UpdateChecker:
    """Check for updates from GitHub releases."""
    
    GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    def __init__(self, current_version: str, github_repo: str, config_manager=None):
        """
        Initialize the update checker.
        
        Args:
            current_version: Current application version (e.g., "1.2.3")
            github_repo: GitHub repository path (e.g., "owner/repo-name")
            config_manager: Configuration manager for storing skipped versions
        """
        self.current_version = current_version
        self.github_repo = github_repo
        self.config_manager = config_manager
        self._cached_update_info: Optional[UpdateInfo] = None
        self._skipped_versions: List[str] = []
        
        # Load skipped versions from config
        self._load_skipped_versions()
    
    def _load_skipped_versions(self) -> None:
        """Load skipped versions from configuration."""
        if self.config_manager:
            try:
                skipped = self.config_manager.get('Update', 'skipped_versions', fallback='')
                self._skipped_versions = [v.strip() for v in skipped.split(',') if v.strip()]
            except Exception as e:
                logger.warning(f"Failed to load skipped versions: {e}")
                self._skipped_versions = []
    
    def _save_skipped_versions(self) -> None:
        """Save skipped versions to configuration."""
        if self.config_manager:
            try:
                self.config_manager.set('Update', 'skipped_versions', ','.join(self._skipped_versions))
            except Exception as e:
                logger.warning(f"Failed to save skipped versions: {e}")
    
    def check_for_updates(self, force: bool = False) -> Optional[UpdateInfo]:
        """
        Check for updates from GitHub.
        
        Args:
            force: If True, bypass cache and skipped versions
            
        Returns:
            UpdateInfo if update available, None otherwise
        """
        # Return cached result if available and not forcing
        if not force and self._cached_update_info is not None:
            return self._cached_update_info
        
        try:
            import requests
            
            # Build API URL
            parts = self.github_repo.split('/')
            if len(parts) != 2:
                logger.error(f"Invalid GitHub repo format: {self.github_repo}")
                return None
            
            owner, repo = parts
            url = self.GITHUB_API_URL.format(owner=owner, repo=repo)
            
            # Query GitHub API
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            update_info = self._parse_github_response(data)
            
            if update_info is None:
                return None
            
            # Check if version is skipped
            if not force and self.is_version_skipped(update_info.latest_version):
                logger.info(f"Version {update_info.latest_version} is skipped")
                return None
            
            # Check if newer
            if not VersionComparator.is_newer(update_info.latest_version, self.current_version):
                logger.info("Current version is up to date")
                return None
            
            # Cache result
            self._cached_update_info = update_info
            return update_info
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return None
    
    def _parse_github_response(self, data: dict) -> Optional[UpdateInfo]:
        """
        Parse GitHub API response to UpdateInfo.
        
        Args:
            data: GitHub API response JSON
            
        Returns:
            UpdateInfo or None if parsing fails
        """
        try:
            tag_name = data.get('tag_name', '')
            release_notes = data.get('body', '')
            published_at = data.get('published_at', '')
            
            # Find downloadable asset (.zip or .exe)
            # Priority: .zip first (contains full release), then .exe
            assets = data.get('assets', [])
            download_url = ''
            file_size = 0
            download_name = ''
            
            # First pass: look for .zip file
            for asset in assets:
                name = asset.get('name', '')
                if name.endswith('.zip'):
                    download_url = asset.get('browser_download_url', '')
                    file_size = asset.get('size', 0)
                    download_name = name
                    break
            
            # Second pass: look for .exe if no .zip found
            if not download_url:
                for asset in assets:
                    name = asset.get('name', '')
                    if name.endswith('.exe'):
                        download_url = asset.get('browser_download_url', '')
                        file_size = asset.get('size', 0)
                        download_name = name
                        break
            
            if not download_url:
                logger.warning("No .zip or .exe asset found in release")
                return None

            checksum_url = ''
            if download_name:
                candidates = [f"{download_name}.sha256"]
                stem, _ = os.path.splitext(download_name)
                if stem:
                    candidates.append(f"{stem}.sha256")

                for asset in assets:
                    name = asset.get('name', '')
                    if name in candidates:
                        checksum_url = asset.get('browser_download_url', '')
                        break

                if not checksum_url:
                    for asset in assets:
                        name = asset.get('name', '')
                        if not name.endswith('.sha256'):
                            continue
                        if download_name in name or (stem and stem in name):
                            checksum_url = asset.get('browser_download_url', '')
                            break
            
            return UpdateInfo(
                current_version=self.current_version,
                latest_version=tag_name,
                release_notes=release_notes,
                download_url=download_url,
                file_size=file_size,
                release_date=published_at,
                checksum_url=checksum_url
            )
            
        except Exception as e:
            logger.error(f"Failed to parse GitHub response: {e}")
            return None
    
    def skip_version(self, version: str) -> None:
        """
        Mark a version as skipped.
        
        Args:
            version: Version string to skip
        """
        # Normalize version
        normalized = version.strip()
        if normalized.lower().startswith('v'):
            normalized = normalized[1:]
        
        if normalized not in self._skipped_versions:
            self._skipped_versions.append(normalized)
            self._save_skipped_versions()
            logger.info(f"Skipped version: {normalized}")
    
    def is_version_skipped(self, version: str) -> bool:
        """
        Check if a version is skipped.
        
        Args:
            version: Version string to check
            
        Returns:
            True if version is skipped
        """
        # Normalize version
        normalized = version.strip()
        if normalized.lower().startswith('v'):
            normalized = normalized[1:]
        
        return normalized in self._skipped_versions
    
    def get_pending_installer(self) -> Optional[str]:
        """
        Get path of pending installer (downloaded but not installed).
        
        Returns:
            Path to installer or None
        """
        if self.config_manager:
            try:
                path = self.config_manager.get('Update', 'pending_installer', fallback='')
                if path:
                    import os
                    if os.path.exists(path):
                        return path
            except Exception as e:
                logger.warning(f"Failed to get pending installer: {e}")
        return None
