"""
Parallel Downloader

This module provides parallel download functionality.

Requirements: 9.1
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional, Any
from threading import Event, Lock
from dataclasses import dataclass


@dataclass
class DownloadResult:
    """Result of a single download"""
    declaration_id: str
    success: bool
    file_path: Optional[str] = None
    error: Optional[str] = None


class ParallelDownloader:
    """
    Parallel downloader using ThreadPoolExecutor.
    
    Requirements: 9.1
    """
    
    MAX_CONCURRENT = 3
    
    def __init__(
        self, 
        barcode_retriever, 
        file_manager, 
        max_concurrent: int = 3
    ):
        self.barcode_retriever = barcode_retriever
        self.file_manager = file_manager
        self.max_concurrent = min(max_concurrent, self.MAX_CONCURRENT)
        
        self._stop_event = Event()
        self._active_count = 0
        self._lock = Lock()
    
    def download_batch(
        self, 
        declarations: List[Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, bool]:
        """
        Download barcodes for multiple declarations in parallel.
        
        Args:
            declarations: List of Declaration objects
            progress_callback: Callback(completed, total) for progress updates
            
        Returns:
            Dictionary mapping declaration_id to success status
        """
        self._stop_event.clear()
        if self.barcode_retriever and hasattr(self.barcode_retriever, 'reset_method_skip_list'):
            self.barcode_retriever.reset_method_skip_list()
        results = {}
        total = len(declarations)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {}
            
            for decl in declarations:
                if self._stop_event.is_set():
                    break
                
                future = executor.submit(self._download_single, decl)
                futures[future] = decl.id
            
            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break
                
                decl_id = futures[future]
                try:
                    result = future.result()
                    results[decl_id] = result.success
                except Exception:
                    results[decl_id] = False
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        return results
    
    def _download_single(self, declaration) -> DownloadResult:
        """Download a single declaration"""
        with self._lock:
            self._active_count += 1
        
        try:
            if self._stop_event.is_set():
                return DownloadResult(declaration.id, False, error="Stopped")
            
            pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
            
            if pdf_content:
                file_path = self.file_manager.save_barcode(
                    declaration, pdf_content, overwrite=True
                )
                if file_path:
                    return DownloadResult(declaration.id, True, file_path=file_path)
            
            return DownloadResult(declaration.id, False, error="Failed to retrieve")
            
        except Exception as e:
            return DownloadResult(declaration.id, False, error=str(e))
        finally:
            with self._lock:
                self._active_count -= 1
    
    def stop(self) -> None:
        """Stop all downloads"""
        self._stop_event.set()
    
    def get_active_count(self) -> int:
        """Get number of active downloads"""
        with self._lock:
            return self._active_count
