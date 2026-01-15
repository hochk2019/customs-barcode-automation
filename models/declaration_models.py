"""
Declaration data models

This module contains data classes for customs declarations and workflow results.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import os


@dataclass
class Declaration:
    """Customs declaration data model"""
    declaration_number: str
    tax_code: str
    declaration_date: datetime
    customs_office_code: str = ""
    transport_method: str = ""
    channel: str = ""  # 'Xanh' or 'Vang'
    status: str = ""  # 'T' for cleared
    goods_description: Optional[str] = None
    # Additional fields for preview display
    status_name: Optional[str] = None  # Trạng thái chi tiết: Nhập mới, Đã phân luồng, Thông quan
    company_name: Optional[str] = None  # Tên công ty (từ bảng DTOKHAIMD)
    declaration_type: Optional[str] = None  # Loại hình: A11, A12, B11...
    bill_of_lading: Optional[str] = None  # Số vận đơn
    invoice_number: Optional[str] = None  # Số hóa đơn
    so_hstk: Optional[str] = None  # Số hồ sơ tờ khai - dùng để nhận biết XNK TC
    
    # XNK TC patterns for detection
    XNKTC_PATTERNS = ['#&NKTC', '#&XKTC', '#&GCPTQ']

    def __post_init__(self) -> None:
        """Normalize declaration_date to datetime when passed as string/date."""
        if isinstance(self.declaration_date, str):
            parsed = self._parse_date_string(self.declaration_date)
            if parsed:
                self.declaration_date = parsed
        elif hasattr(self.declaration_date, "year") and not isinstance(self.declaration_date, datetime):
            # Convert date-like objects to datetime for consistent downstream usage.
            self.declaration_date = datetime(
                self.declaration_date.year,
                self.declaration_date.month,
                self.declaration_date.day
            )

    @staticmethod
    def _parse_date_string(value: str) -> Optional[datetime]:
        """Parse common declaration date string formats."""
        if not value:
            return None
        raw = value.strip()
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%Y%m%d",
        ):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return None
    
    @property
    def is_xnktc(self) -> bool:
        """
        Kiểm tra xem tờ khai có phải là XNK tại chỗ không
        
        Returns:
            True nếu là tờ khai XNK TC (NKTC, XKTC, hoặc GCPTQ), False nếu không
        """
        if not self.so_hstk:
            return False
        so_hstk_upper = self.so_hstk.upper()
        return any(pattern in so_hstk_upper for pattern in self.XNKTC_PATTERNS)
    
    @property
    def id(self) -> str:
        """Unique identifier for tracking"""
        date_str = self.declaration_date.strftime('%Y%m%d')
        return f"{self.tax_code}_{self.declaration_number}_{date_str}"
    
    @property
    def status_display(self) -> str:
        """Get display-friendly status name"""
        if self.status_name:
            # Return status_name directly if it's already formatted
            if 'Thông quan' in self.status_name:
                return self.status_name
            status_lower = self.status_name.lower()
            if 'thông quan' in status_lower or 'chấp nhận' in status_lower:
                return "Thông quan"
            elif 'phân luồng' in status_lower:
                return "Đã phân luồng"
            elif 'nhập mới' in status_lower:
                return "Nhập mới"
            return self.status_name[:20] if len(self.status_name) > 20 else self.status_name
        # Fallback: derive from channel if available
        if self.channel:
            if self.channel == 'Xanh':
                return "Luồng Xanh"
            elif self.channel == 'Vang':
                return "Luồng Vàng"
        return ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class ProcessedDeclaration:
    """Processed declaration record from tracking database"""
    id: int
    declaration_number: str
    tax_code: str
    declaration_date: str
    file_path: str
    processed_at: datetime
    updated_at: datetime
    
    @property
    def display_name(self) -> str:
        """Display name for UI"""
        return f"{self.tax_code}_{self.declaration_number}"
    
    def file_exists(self) -> bool:
        """Check if the PDF file still exists"""
        return os.path.exists(self.file_path)


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    total_fetched: int = 0
    total_eligible: int = 0
    success_count: int = 0
    error_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> timedelta:
        """Calculate execution duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return timedelta(0)


class OperationMode(Enum):
    """Operation mode for the scheduler"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class ClearanceStatus(Enum):
    """Declaration clearance status."""
    PENDING = "pending"          # Chưa thông quan
    CLEARED = "cleared"          # Đã thông quan
    TRANSFER = "transfer"        # Chuyển địa điểm kiểm tra (Luồng đỏ - có thể lấy mã vạch)
    ERROR = "error"              # Lỗi kiểm tra
    UNKNOWN = "unknown"          # Chưa xác định


@dataclass
class TrackingDeclaration:
    """A declaration being tracked for clearance."""
    id: Optional[int]
    tax_code: str
    declaration_number: str
    customs_code: str
    declaration_date: str
    company_name: str
    status: ClearanceStatus
    last_checked: Optional[datetime]
    cleared_at: Optional[datetime]
    added_at: datetime
    notified: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            'id': self.id,
            'tax_code': self.tax_code,
            'declaration_number': self.declaration_number,
            'customs_code': self.customs_code,
            'declaration_date': self.declaration_date,
            'company_name': self.company_name,
            'status': self.status.value,
            'last_checked': self.last_checked.strftime('%d/%m/%Y %H:%M') if self.last_checked else '',
            'cleared_at': self.cleared_at.strftime('%d/%m/%Y %H:%M') if self.cleared_at else '',
            'added_at': self.added_at.strftime('%d/%m/%Y %H:%M'),
            'notified': self.notified
        }
