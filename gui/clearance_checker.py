"""
Clearance Checker Background Service

Periodically checks status of pending declarations and triggers notifications.

Requirements: Phase 4
"""

import threading
import time
from datetime import datetime
from typing import List, Callable, Optional, Dict

from logging_system.logger import Logger
from database.tracking_database import TrackingDatabase
from database.ecus_connector import EcusDataConnector
from gui.notification_manager import NotificationManager
from config.user_preferences import get_preferences
from models.declaration_models import ClearanceStatus

class ClearanceChecker:
    """Background service for self-checking clearance status."""
    
    def __init__(
        self,
        tracking_db: TrackingDatabase,
        ecus_connector: EcusDataConnector,
        notification_manager: NotificationManager,
        logger: Logger
    ):
        """
        Initialize ClearanceChecker.
        
        Args:
            tracking_db: TrackingDatabase instance
            ecus_connector: EcusDataConnector instance
            notification_manager: NotificationManager instance
            logger: Logger instance
        """
        self.tracking_db = tracking_db
        self.ecus_connector = ecus_connector
        self.notification_manager = notification_manager
        self.logger = logger
        
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._cancel_check = threading.Event()  # New cancellation event
        
        # Default settings
        self.check_interval_minutes = 15
        self.auto_check_enabled = False
        
        # Callbacks
        self.on_status_changed: Optional[Callable[[], None]] = None
        
    def start(self):
        """Start background checking thread."""
        if self._thread and self._thread.is_alive():
            return

        self.is_running = True
        self._stop_event.clear()
        
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        # Perform cleanup on start
        try:
            prefs = get_preferences()
            retention_days = prefs.retention_days
            threading.Thread(target=self.tracking_db.cleanup_old_records, args=(retention_days,), daemon=True).start()
        except Exception as e:
            self.logger.warning(f"Failed to schedule cleanup: {e}")
            
        self.logger.info("ClearanceChecker service started")
        
    def stop(self):
        """Stop background checking thread."""
        self.is_running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.logger.info("ClearanceChecker service stopped")
        
    def set_config(self, enabled: bool, interval_minutes: int):
        """Update configuration dynamically."""
        self.auto_check_enabled = enabled
        self.check_interval_minutes = max(1, interval_minutes)
        self.logger.info(f"ClearanceChecker config updated: enabled={enabled}, interval={interval_minutes}m")
        
        # If disabled, we don't stop the thread, we just pause checking in the loop
        # triggering immediate check if re-enabled is handled by loop logic or manual trigger
        
    def check_now(self, ids_to_check: Optional[List[int]] = None, progress_callback: Optional[Callable] = None) -> int:
        """
        Force an immediate check.
        
        Args:
            ids_to_check: Optional list of declaration IDs to check. If None, check all pending.
            progress_callback: Optional callback(current, total, decl_id, status, last_checked, cleared_at)
        
        Returns:
            Number of declarations cleared in this check
        """
        return self._check_pending_declarations(ids_to_check, progress_callback)
        
    def _run_loop(self):
        """Main loop."""
        while not self._stop_event.is_set():
            try:
                if self.auto_check_enabled:
                    self._check_pending_declarations()
                
                # Sleep for interval or until stopped
                # We interpret check_interval_minutes as time BETWEEN checks
                # Check stop_event every second for responsive shutdown
                for _ in range(self.check_interval_minutes * 60):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error in ClearanceChecker loop: {e}", exc_info=True)
                time.sleep(60) # Wait a bit before retrying on error

    def stop_current_check(self):
        """Signal current check loop to stop."""
        self._cancel_check.set()
        self.logger.info("Signal received to stop current check")

    def _check_pending_declarations(self, ids_to_check: Optional[List[int]] = None, progress_callback: Optional[Callable] = None) -> int:
        """
        Check for pending declarations using API-first strategy with parallel processing.
        
        Strategy:
        1. Call API in parallel (with retry on failure)
        2. If API fails after retry, fallback to ECUS database
        
        Args:
            ids_to_check: Optional list of IDs to check.
            progress_callback: Optional callback for progress updates
            
        Returns:
            Number of cleared declarations
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        try:
            self._cancel_check.clear()
            
            # Get API timeout from preferences
            prefs = get_preferences()
            api_timeout = prefs.api_timeout
            
            # 1. Get pending declarations from Tracking DB
            if ids_to_check:
                all_tracking = self.tracking_db.get_all_tracking()
                pending_list = [d for d in all_tracking if d.id in ids_to_check]
            else:
                pending_list = self.tracking_db.get_pending_declarations()
            
            if not pending_list:
                # Still call callback to reset countdown timer even when nothing to check
                if self.on_status_changed:
                    self.on_status_changed()
                return 0
                
            self.logger.info(f"Checking status for {len(pending_list)} declarations (API-first, parallel)...")
            
            total_count = len(pending_list)
            cleared_count = 0
            results_lock = threading.Lock()
            
            def check_single_declaration(pending):
                """Check single declaration: API first, then DB fallback."""
                nonlocal cleared_count
                
                if self._cancel_check.is_set():
                    return None
                
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status_text = "Chưa thông quan"
                cleared_at_str = None
                new_status = ClearanceStatus.PENDING
                is_cleared = False
                is_transfer = False
                company_name = pending.company_name or ""
                
                # STEP 1: Try API first (with retry)
                api_success = False
                for attempt in range(2):  # 2 attempts = 1 original + 1 retry
                    if self._cancel_check.is_set():
                        break
                    try:
                        from web_utils.qrcode_api_client import QRCodeContainerApiClient
                        api_client = QRCodeContainerApiClient(logger=self.logger, timeout=api_timeout)
                        
                        # Convert declaration_date to datetime if it's a string
                        decl_date = pending.declaration_date
                        if isinstance(decl_date, str):
                            try:
                                # Try common date formats
                                if ' ' in decl_date:
                                    decl_date = decl_date.split(' ')[0]  # Remove time part
                                if '-' in decl_date:
                                    decl_date = datetime.strptime(decl_date, '%Y-%m-%d')
                                elif '/' in decl_date:
                                    decl_date = datetime.strptime(decl_date, '%d/%m/%Y')
                            except Exception as date_err:
                                self.logger.warning(f"Failed to parse date '{pending.declaration_date}': {date_err}")
                                decl_date = datetime.now()  # Fallback to today
                        
                        result = api_client.query_bang_ke(
                            ma_so_thue=pending.tax_code,
                            so_to_khai=pending.declaration_number,
                            ma_hai_quan=pending.customs_code if hasattr(pending, 'customs_code') and pending.customs_code else "",
                            ngay_dang_ky=decl_date
                        )
                        
                        if result and result.is_valid:
                            api_success = True
                            
                            # Check TrangThaiToKhai field for clearance status
                            # - "Thông quan" = cleared (green/yellow/red channel after inspection)
                            # - "Chuyển địa điểm kiểm tra" = red channel approved for inspection (can get barcode)
                            trang_thai = (result.trang_thai_to_khai or "").lower()
                            
                            # Keywords indicating full clearance
                            cleared_keywords = ["thông quan", "thong quan", "chấp nhận thông quan"]
                            # Keywords indicating red channel approved for inspection area transfer (can get barcode)
                            transfer_keywords = ["chuyển địa điểm", "chuyen dia diem"]
                            
                            is_cleared = any(kw in trang_thai for kw in cleared_keywords)
                            is_transfer = any(kw in trang_thai for kw in transfer_keywords)
                            
                            # Also check if barcode images available (indicates at least transfer/cleared)
                            if not is_cleared and not is_transfer and result.containers:
                                has_barcodes = any(c.barcode_image for c in result.containers)
                                if has_barcodes:
                                    # Has barcodes but no specific status - assume cleared
                                    is_cleared = True
                            
                            if result.ten_don_vi_xnk:
                                company_name = result.ten_don_vi_xnk
                            
                            self.logger.debug(f"API check {pending.declaration_number}: trang_thai='{trang_thai}', is_cleared={is_cleared}, is_transfer={is_transfer}")
                            break
                        elif result and result.has_error:
                            # Check if error message indicates pending status
                            error_msg = (result.thong_bao_loi or "").lower()
                            if "chưa được cấp phép" in error_msg or "chua duoc cap phep" in error_msg:
                                # This means the declaration exists but is not cleared yet
                                api_success = True  # API worked, just not cleared
                                is_cleared = False
                                self.logger.debug(f"API check {pending.declaration_number}: pending (chưa được cấp phép)")
                                break
                            
                    except ImportError:
                        self.logger.debug("QRCodeContainerApiClient not available")
                        break
                    except Exception as e:
                        if attempt == 0:
                            self.logger.debug(f"API check failed for {pending.declaration_number}, retrying... ({e})")
                        else:
                            self.logger.warning(f"API check failed after retry for {pending.declaration_number}: {e}")
                
                # STEP 2: If API failed, fallback to ECUS database
                if not api_success and not self._cancel_check.is_set():
                    self.logger.debug(f"Falling back to ECUS DB for {pending.declaration_number}")
                    try:
                        ecus_results = self.ecus_connector.check_declarations_status(
                            [(pending.tax_code, pending.declaration_number)]
                        )
                        if ecus_results:
                            ecus_decl = ecus_results[0]
                            is_cleared = ecus_decl.status == 'T'
                            if ecus_decl.company_name:
                                company_name = ecus_decl.company_name
                            self.logger.debug(f"ECUS check {pending.declaration_number}: is_cleared={is_cleared}")
                    except Exception as e:
                        self.logger.warning(f"ECUS DB check failed for {pending.declaration_number}: {e}")
                
                # STEP 3: Update status in tracking DB (method auto-sets last_checked)
                if is_cleared:
                    new_status = ClearanceStatus.CLEARED
                    status_text = "Đã thông quan"
                    cleared_at_str = now_str
                    
                    self.logger.info(f">>> UPDATING STATUS TO CLEARED: {pending.declaration_number} (id={pending.id})")
                    self.tracking_db.update_status(pending.id, new_status)
                    self._notify_cleared(pending.declaration_number, company_name)
                    
                    with results_lock:
                        cleared_count += 1
                elif is_transfer:
                    # Red channel - approved for inspection transfer (can get barcode)
                    new_status = ClearanceStatus.TRANSFER
                    status_text = "Chuyển địa điểm"
                    cleared_at_str = now_str  # Consider this as "cleared" for barcode purposes
                    
                    self.tracking_db.update_status(pending.id, new_status)
                    self._notify_transfer(pending.declaration_number, company_name)
                    
                    with results_lock:
                        cleared_count += 1
                else:
                    self.tracking_db.update_status(pending.id, new_status)
                
                return (pending.id, status_text, now_str, cleared_at_str)
            
            # Run parallel checks with ThreadPoolExecutor
            current_idx = 0
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_pending = {
                    executor.submit(check_single_declaration, p): p 
                    for p in pending_list
                }
                
                for future in as_completed(future_to_pending):
                    current_idx += 1
                    pending = future_to_pending[future]
                    
                    try:
                        result = future.result()
                        if result:
                            decl_id, status_text, now_str, cleared_at_str = result
                            
                            if progress_callback:
                                try:
                                    progress_callback(current_idx, total_count, decl_id, status_text, now_str, cleared_at_str)
                                except:
                                    pass
                    except Exception as e:
                        self.logger.error(f"Check failed for {pending.declaration_number}: {e}")
            
            # Always refresh UI after check completes (even if no status changes)
            if self.on_status_changed:
                self.on_status_changed()
                    
            return cleared_count

        except Exception as e:
            self.logger.error(f"Failed during _check_pending_declarations: {e}", exc_info=True)
            return 0
            
    def _notify_cleared(self, decl_number: str, company_name: str):
        """Send notification for cleared declaration."""
        title = "Thông quan thành công!"
        msg = f"Tờ khai {decl_number}\n{company_name}\nĐã được thông quan."
        try:
            self.notification_manager.show_notification(title, msg, icon='info')
        except Exception:
            pass

    def _notify_transfer(self, decl_number: str, company_name: str):
        """Send notification for red channel transfer (chuyển địa điểm kiểm tra)."""
        title = "Chuyển địa điểm kiểm tra!"
        msg = f"Tờ khai {decl_number}\n{company_name}\nĐã được duyệt chuyển địa điểm.\nCó thể lấy mã vạch."
        try:
            self.notification_manager.show_notification(title, msg, icon='info')
        except Exception:
            pass
