"""
Updater Controller v2.0

Handles application update checking, downloading, and installation.
Extracted from customs_gui.py to reduce GUI file size.
"""

import threading
from typing import Optional, Callable
from tkinter import messagebox
import tkinter as tk

from gui.branding import APP_VERSION
from logging_system.logger import Logger


class UpdaterController:
    """
    Controller for application updates.
    
    Manages:
    - Background update checking
    - Download progress UI
    - Installation prompts
    """
    
    def __init__(
        self,
        root: tk.Tk,
        config_manager,
        logger: Logger
    ):
        """
        Initialize updater controller.
        
        Args:
            root: Tkinter root window
            config_manager: Configuration manager
            logger: Logger instance
        """
        self.root = root
        self.config_manager = config_manager
        self.logger = logger
        
        self._is_checking = False
        self._download_in_progress = False
    
    def check_for_updates(self, silent: bool = False) -> None:
        """
        Check for updates in background.
        
        Args:
            silent: If True, don't show "already up to date" message
        """
        if self._is_checking:
            return
        
        self._is_checking = True
        
        def check():
            try:
                from update.update_checker import UpdateChecker
                from update.download_manager import DownloadManager, DownloadCancelledError
                
                github_repo = self.config_manager.get('Update', 'github_repo', fallback='')
                if not github_repo:
                    if not silent:
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Kiểm tra cập nhật",
                            "Chưa cấu hình GitHub repository cho cập nhật."
                        ))
                    return
                
                checker = UpdateChecker(APP_VERSION, github_repo, self.config_manager)
                update_info = checker.check_for_updates(force=True)
                
                if update_info:
                    self.root.after(0, lambda: self._show_update_dialog(update_info, checker))
                elif not silent:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Kiểm tra cập nhật",
                        "Bạn đang sử dụng phiên bản mới nhất."
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Update check failed: {e}")
                if not silent:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Lỗi",
                        f"Không thể kiểm tra cập nhật: {e}"
                    ))
            finally:
                self._is_checking = False
        
        threading.Thread(target=check, daemon=True).start()
    
    def _show_update_dialog(self, update_info, checker) -> None:
        """Show the update available dialog."""
        from gui.update_dialog import UpdateDialog, DownloadProgressDialog, InstallPromptDialog
        
        dialog = UpdateDialog(self.root, update_info)
        result = dialog.show()
        
        if result == "update_now":
            self._start_download(update_info)
        elif result == "skip_version":
            checker.skip_version(update_info.latest_version)
    
    def _start_download(self, update_info) -> None:
        """Start downloading the update."""
        from update.download_manager import DownloadManager, DownloadCancelledError
        from update.models import DownloadProgress
        from gui.update_dialog import DownloadProgressDialog
        
        if self._download_in_progress:
            return
        
        self._download_in_progress = True
        download_manager = DownloadManager()
        
        # Determine file extension
        download_url = update_info.download_url
        file_ext = '.zip' if download_url.endswith('.zip') else '.exe'
        filename = f"CustomsBarcodeAutomation_{update_info.latest_version}{file_ext}"
        
        progress_dialog = DownloadProgressDialog(self.root, filename)
        
        def progress_callback(downloaded, total, speed):
            progress = DownloadProgress(downloaded, total, speed)
            self.root.after(0, lambda: progress_dialog.update_progress(progress))
        
        def download():
            try:
                filepath = download_manager.download_file(
                    download_url,
                    filename,
                    update_info.file_size,
                    progress_callback
                )
                
                self.root.after(0, progress_dialog.close)
                
                if download_manager.is_zip_file(filepath):
                    self.root.after(0, lambda: self._handle_zip_update(download_manager, filepath))
                else:
                    self.root.after(0, lambda: self._handle_exe_update(filepath))
                    
            except DownloadCancelledError:
                self.logger.info("Download cancelled by user")
            except Exception as e:
                self.logger.error(f"Download failed: {e}")
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Tải xuống thất bại: {e}"))
            finally:
                self._download_in_progress = False
        
        threading.Thread(target=download, daemon=True).start()
    
    def _handle_zip_update(self, download_manager, filepath: str) -> None:
        """Handle ZIP archive update."""
        try:
            app_dir = download_manager.get_app_directory()
            
            result = messagebox.askyesno(
                "Cập nhật tự động",
                "Đã tải xong bản cập nhật.\n\n"
                "Bạn có muốn cập nhật tự động không?\n"
                "- Ấn 'Yes': Ứng dụng sẽ đóng và tự động cập nhật\n"
                "- Ấn 'No': Giải nén vào thư mục riêng để cập nhật thủ công"
            )
            
            if result:
                self.logger.info("Starting auto-update...")
                if download_manager.run_update_and_restart(filepath, app_dir):
                    self.root.after(500, self.root.destroy)
                else:
                    messagebox.showerror("Lỗi", "Không thể khởi động quá trình cập nhật!")
            else:
                extract_dir = download_manager.extract_zip(filepath)
                messagebox.showinfo(
                    "Tải xuống hoàn tất",
                    f"Đã giải nén phiên bản mới tại:\n{extract_dir}\n\n"
                    "Vui lòng đóng ứng dụng và copy các file vào thư mục cài đặt."
                )
                import subprocess
                subprocess.Popen(['explorer', extract_dir])
                
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            messagebox.showerror("Lỗi", f"Cập nhật thất bại: {e}")
    
    def _handle_exe_update(self, filepath: str) -> None:
        """Handle EXE installer update."""
        from gui.update_dialog import InstallPromptDialog
        from update.download_manager import DownloadManager
        
        download_manager = DownloadManager()
        install_dialog = InstallPromptDialog(self.root, filepath)
        result = install_dialog.show()
        
        if result == "install_now":
            import subprocess
            subprocess.Popen([filepath], shell=True)
            self.root.after(500, self.root.destroy)
        else:
            download_manager.save_pending_installer(filepath, self.config_manager)
