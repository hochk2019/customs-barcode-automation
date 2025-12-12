"""
Barcode PDF Generator Module

This module generates PDF documents with barcodes from API data,
matching the layout from pus.customs.gov.vn website.
"""

import io
import base64
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Barcode generation - explicit imports for PyInstaller compatibility
# Use Code39 (Free 3 of 9) to match ECUS barcode style
try:
    from barcode import Code39
    from barcode.writer import ImageWriter
except ImportError:
    # Fallback: try importing from barcode.codex module directly
    try:
        from barcode.codex import Code39
        from barcode.writer import ImageWriter
    except ImportError:
        Code39 = None
        ImageWriter = None

from web_utils.qrcode_api_client import ContainerDeclarationInfo, ContainerInfo
from logging_system.logger import Logger


@dataclass
class BarcodeRenderConfig:
    """Configuration for barcode PDF rendering"""
    page_width: float = A4[0]
    page_height: float = A4[1]
    margin_top: float = 1.5 * cm
    margin_bottom: float = 1.5 * cm
    margin_left: float = 2 * cm
    margin_right: float = 2 * cm
    barcode_height: float = 15 * mm  # Reduced to match ECUS barcode (no text below)
    barcode_width: float = 50 * mm   # Reduced width to match ECUS proportions
    qr_code_size: float = 2 * cm     # QR code size for container PDF (~2cm x 2cm)


class BarcodePdfGenerator:
    """
    Generates PDF documents with barcodes from declaration data.
    
    Creates PDF output matching the layout from pus.customs.gov.vn website.
    """
    
    def __init__(self, logger: Logger = None):
        """
        Initialize the PDF generator.
        
        Args:
            logger: Logger instance for logging.
        """
        self.logger = logger
        self.config = BarcodeRenderConfig()
        self._register_fonts()
    
    def _register_fonts(self):
        """Register Vietnamese-compatible fonts"""
        try:
            # Try to use Arial which supports Vietnamese
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Italic', 'ariali.ttf'))
            self.font_name = 'Arial'
            self.font_bold = 'Arial-Bold'
            self.font_italic = 'Arial-Italic'
        except Exception:
            # Fallback to Helvetica (built-in)
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
            self.font_italic = 'Helvetica-Oblique'
            if self.logger:
                self.logger.debug("Using Helvetica font (Vietnamese may not display correctly)")
    
    def generate_pdf(self, info: ContainerDeclarationInfo) -> Optional[bytes]:
        """
        Generate PDF document from declaration info.
        Routes to container layout if MaPTVC = 2, otherwise regular cargo layout.
        
        Args:
            info: ContainerDeclarationInfo object with declaration data.
            
        Returns:
            PDF content as bytes, or None if generation fails.
        """
        if not info or not info.is_valid:
            if self.logger:
                self.logger.error("Invalid declaration info for PDF generation")
            return None
        
        try:
            # Create PDF in memory
            buffer = io.BytesIO()
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=self.config.margin_top,
                bottomMargin=self.config.margin_bottom,
                leftMargin=self.config.margin_left,
                rightMargin=self.config.margin_right
            )
            
            # Build document content - route based on declaration type
            if info.is_container_declaration:
                elements = self._build_container_content(info)
                pdf_type = "container"
            else:
                elements = self._build_content(info)
                pdf_type = "cargo"
            
            # Generate PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            if self.logger:
                self.logger.info(f"Generated {pdf_type} PDF ({len(pdf_bytes)} bytes) for declaration {info.so_to_khai}")
            
            return pdf_bytes
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to generate PDF: {e}")
                import traceback
                self.logger.debug(traceback.format_exc())
            return None
    
    def _build_content(self, info: ContainerDeclarationInfo) -> list:
        """
        Build PDF content elements matching web layout.
        
        Args:
            info: ContainerDeclarationInfo object.
            
        Returns:
            List of flowable elements for PDF.
        """
        elements = []
        styles = self._get_styles()
        
        # Calculate available width
        available_width = A4[0] - self.config.margin_left - self.config.margin_right
        
        # ===== HEADER SECTION =====
        # Create header table with 2 columns: Left (customs office) | Right (barcode + date)
        
        # Generate barcode image
        barcode_img = self._generate_barcode_image(info.so_dinh_danh or info.so_to_khai)
        
        # Format date
        today = datetime.now()
        date_str = f"Ngày {today.day:02d} tháng {today.month:02d} năm {today.year}"
        
        # Left column: Customs office info
        # Use TenCucHaiQuan (e.g., "Chi cục Hải quan khu vực V") and TenChiCucHaiQuan (e.g., "Hải quan Bắc Ninh")
        ten_cuc_hq = info.ten_cuc_hai_quan or "Chi cục Hải quan khu vực V"
        ten_chi_cuc_hq = info.ten_chi_cuc_hai_quan or "Hải quan Bắc Ninh"
        
        # Line 1: "Chi cục Hải quan khu vực V" - bold, LEFT aligned
        # Line 2: "Hải quan Bắc Ninh" - bold, CENTER aligned under line 1
        header_line1 = Paragraph(ten_cuc_hq, styles['header_left_bold'])
        header_line2 = Paragraph(ten_chi_cuc_hq, styles['header_bold_center'])
        
        # Create a table with fixed width matching "Chi cục Hải quan khu vực V" text
        # Line 1 is LEFT aligned, Line 2 is CENTER aligned within the same width
        header_text_width = 160  # Width in points to match "Chi cục Hải quan khu vực V"
        header_inner_table = Table(
            [[header_line1], [header_line2]],
            colWidths=[header_text_width]
        )
        header_inner_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),      # Line 1: LEFT aligned
            ('ALIGN', (0, 1), (0, 1), 'CENTER'),    # Line 2: CENTER aligned
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        left_content = [header_inner_table]
        
        # Right column: Barcode and date
        right_content = []
        if barcode_img:
            right_content.append(barcode_img)
        right_content.append(Spacer(1, 2*mm))
        right_content.append(Paragraph(date_str, styles['date_right_italic']))
        
        # Create header table
        header_data = [[left_content, right_content]]
        header_table = Table(header_data, colWidths=[available_width * 0.5, available_width * 0.5])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 15*mm))
        
        # ===== TITLE SECTION =====
        elements.append(Paragraph("DANH SÁCH HÀNG HÓA", styles['title']))
        elements.append(Paragraph("ĐỦ ĐIỀU KIỆN QUA KHU VỰC GIÁM SÁT HẢI QUAN", styles['title']))
        
        # Sub-title (black text, not red)
        ghi_chu = info.ghi_chu or "Tờ khai không phải niêm phong"
        elements.append(Paragraph(ghi_chu, styles['subtitle_black']))
        elements.append(Spacer(1, 10*mm))
        
        # ===== DECLARATION INFO SECTION =====
        # Build full customs supervision location (Chi cục HQ GS + Địa điểm GS)
        chi_cuc_gs = info.ten_chi_cuc_hai_quan_gs or 'CC HQ CK Sân bay QT Nội Bài'
        # Add địa điểm giám sát (MaDDGS: TenDDGS - MaPTVC) if available
        # MaPTVC (Mã phương tiện vận chuyển) is the number at the end (e.g., "- 1", "- 2")
        if info.ma_ddgs and info.ten_ddgs:
            # Include MaPTVC number at the end (e.g., "- 1", "- 2", "- 3")
            ma_ptvc_str = f" - {info.ma_ptvc}" if info.ma_ptvc else ""
            chi_cuc_gs_full = f"{chi_cuc_gs} - {info.ma_ddgs}: {info.ten_ddgs}{ma_ptvc_str}"
        elif info.ten_ddgs:
            ma_ptvc_str = f" - {info.ma_ptvc}" if info.ma_ptvc else ""
            chi_cuc_gs_full = f"{chi_cuc_gs} - {info.ten_ddgs}{ma_ptvc_str}"
        else:
            chi_cuc_gs_full = chi_cuc_gs
        
        # Item 1 - full width (allow line wrap for long content)
        elements.append(Paragraph(
            f"<font name='{self.font_bold}'>1. Chi cục hải quan giám sát:</font> {chi_cuc_gs_full}",
            styles['info']
        ))
        
        # Item 2 - full width
        elements.append(Paragraph(
            f"<font name='{self.font_bold}'>2. Đơn vị XNK:</font> {info.ten_don_vi_xnk}",
            styles['info']
        ))
        
        # Items 3-5 (left) and 6-8 (right) in two columns
        left_items = [
            f"<font name='{self.font_bold}'>3. Mã số thuế:</font> {info.ma_so_thue}",
            f"<font name='{self.font_bold}'>4. Số tờ khai:</font> {info.so_to_khai}",
            f"<font name='{self.font_bold}'>5. Trạng thái tờ khai:</font> {info.trang_thai_to_khai}",
        ]
        
        right_items = [
            f"<font name='{self.font_bold}'>6. Ngày tờ khai:</font> {info.ngay_to_khai}",
            f"<font name='{self.font_bold}'>7. Loại hình:</font> {info.ten_loai_hinh}",
            f"<font name='{self.font_bold}'>8. Luồng:</font> {info.luong_to_khai}",
        ]
        
        # Build info table for items 3-8
        info_rows = []
        for i in range(len(left_items)):
            left_para = Paragraph(left_items[i], styles['info'])
            right_para = Paragraph(right_items[i], styles['info'])
            info_rows.append([left_para, right_para])
        
        info_table = Table(info_rows, colWidths=[available_width * 0.5, available_width * 0.5])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(info_table)
        
        # Item 9 - full width
        elements.append(Paragraph(
            f"<font name='{self.font_bold}'>9. Số quản lý hàng hóa:</font> {info.so_dinh_danh}",
            styles['info']
        ))
        elements.append(Spacer(1, 8*mm))
        
        # ===== CARGO TABLE =====
        table_header = [
            'STT',
            'SỐ LƯỢNG HÀNG\n(1)',
            'TỔNG TRỌNG LƯỢNG HÀNG\n(2)',
            'LƯỢNG HÀNG HÓA\nTHỰC TẾ QUA KHU VỰC\nGIÁM SÁT HẢI QUAN\n(3)',
            'XÁC NHẬN CỦA\nCÔNG CHỨC HẢI QUAN\n(4)'
        ]
        
        # Format cargo data - use Paragraph for automatic text wrapping
        so_luong_raw = f"{int(info.so_luong_hang)} {info.dvt_so_luong_hang}" if info.so_luong_hang else ""
        trong_luong_raw = f"{info.tong_trong_luong_hang} {info.dvt_tong_trong_luong_hang}" if info.tong_trong_luong_hang else ""
        
        # Create cell style for wrapping text in data cells
        cell_style = ParagraphStyle(
            'cell_wrap',
            parent=styles['info'],
            fontSize=9,
            alignment=TA_CENTER,
            wordWrap='CJK',  # Enable word wrap
            leading=11,  # Line spacing
        )
        
        # Wrap long text in Paragraph for automatic line breaking
        so_luong = Paragraph(so_luong_raw, cell_style) if so_luong_raw else ''
        trong_luong = Paragraph(trong_luong_raw, cell_style) if trong_luong_raw else ''
        
        table_data = [
            table_header,
            ['1', so_luong, trong_luong, '', '']
        ]
        
        col_widths = [1.2*cm, 3.5*cm, 4*cm, 4*cm, 4*cm]  # Slightly wider column for SỐ LƯỢNG HÀNG
        cargo_table = Table(table_data, colWidths=col_widths)
        cargo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Reverted to 8 to fit column width
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # Increased from 9
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWHEIGHT', (0, 0), (-1, 0), 45),
            # Remove fixed row height for data rows to allow auto-expand for wrapped text
        ]))
        elements.append(cargo_table)
        elements.append(Spacer(1, 5*mm))
        
        # ===== EXPORT INFO =====
        export_time = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        elements.append(Paragraph(
            f"Kết xuất dữ liệu lúc: {export_time}",
            styles['small_italic']
        ))
        elements.append(Spacer(1, 8*mm))
        
        # ===== NOTES SECTION =====
        notes = [
            "<i>Ghi chú:</i>",
            "- Cột số (1) lấy từ tiêu chí \"Số lượng\" trên phần \"General\" của tờ khai hải quan.",
            "- Cột số (2) lấy từ tiêu chí \"Tổng trọng lượng hàng\" trên phần \"General\" của tờ khai hải quan.",
            "- Trường hợp hàng hóa được đưa qua KVGS nhiều lần thì đối với từng lần đưa hàng qua KVGS, công chức hải quan thực hiện:",
            "    + Cột số (3): ghi rõ lượng hàng từng lần qua KVGS.",
            "    + Cột số (4): ghi ngày, tháng, năm; ký, đóng dấu công chức.",
            "- Trường hợp ghi rõ tại cột (1):",
            "    + Khác 1 thì theo dõi lượng hàng tại cột (3) tương ứng theo cột (1).",
        ]
        
        for note in notes:
            elements.append(Paragraph(note, styles['note']))
        
        return elements
    
    def _get_styles(self) -> dict:
        """Get paragraph styles for PDF"""
        styles = getSampleStyleSheet()
        
        return {
            'header_left': ParagraphStyle(
                'header_left',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,  # Increased from 10
                alignment=TA_LEFT,
            ),
            'header_bold': ParagraphStyle(
                'header_bold',
                parent=styles['Normal'],
                fontName=self.font_bold,
                fontSize=12,  # Increased from 11
                alignment=TA_LEFT,
            ),
            'header_bold_center': ParagraphStyle(
                'header_bold_center',
                parent=styles['Normal'],
                fontName=self.font_bold,
                fontSize=12,  # Increased from 11
                alignment=TA_CENTER,  # Center aligned under the first line
            ),
            'header_left_bold': ParagraphStyle(
                'header_left_bold',
                parent=styles['Normal'],
                fontName=self.font_bold,
                fontSize=12,  # Increased from 11
                alignment=TA_LEFT,
            ),
            'header_center_bold': ParagraphStyle(
                'header_center_bold',
                parent=styles['Normal'],
                fontName=self.font_bold,
                fontSize=12,  # Increased from 11
                alignment=TA_CENTER,
            ),
            'date_right_italic': ParagraphStyle(
                'date_right_italic',
                parent=styles['Normal'],
                fontName=self.font_italic,
                fontSize=11,  # Increased from 10
                alignment=TA_RIGHT,
            ),
            'title': ParagraphStyle(
                'title',
                parent=styles['Normal'],
                fontName=self.font_bold,
                fontSize=13,  # Increased from 12
                alignment=TA_CENTER,
                spaceAfter=2 * mm,
            ),
            'subtitle_black': ParagraphStyle(
                'subtitle_black',
                parent=styles['Normal'],
                fontName=self.font_bold,
                fontSize=12,  # Increased from 11
                alignment=TA_CENTER,
                textColor=colors.black,  # Black, not red
            ),
            'info': ParagraphStyle(
                'info',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,  # Increased from 9
                alignment=TA_LEFT,
                spaceAfter=1 * mm,
                wordWrap='CJK',  # Allow word wrap for long text
            ),
            'small_italic': ParagraphStyle(
                'small_italic',
                parent=styles['Normal'],
                fontName=self.font_italic,
                fontSize=9,  # Increased from 8
                alignment=TA_LEFT,
            ),
            'link_right': ParagraphStyle(
                'link_right',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,  # Increased from 9
                alignment=TA_RIGHT,
                textColor=colors.blue,
            ),
            'note': ParagraphStyle(
                'note',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=9,  # Increased from 8
                alignment=TA_LEFT,
                textColor=colors.black,  # Changed from gray to black
                spaceAfter=0.5 * mm,
            ),
        }
    
    def _generate_barcode_image(self, code: str) -> Optional[Image]:
        """
        Generate barcode image for PDF.
        
        Args:
            code: Barcode value (e.g., SoDinhDanh).
            
        Returns:
            ReportLab Image object, or None if generation fails.
        """
        if not code:
            return None
        
        # Check if barcode library is available
        if Code39 is None or ImageWriter is None:
            if self.logger:
                self.logger.error("Barcode library not available - Code39 or ImageWriter is None")
            return None
        
        try:
            # Generate barcode to bytes
            barcode_buffer = io.BytesIO()
            
            # Create Code39 barcode matching ECUS style (Free 3 of 9 font)
            # Code39 is the standard used by ECUS for customs barcodes
            barcode = Code39(code, writer=ImageWriter(), add_checksum=False)
            barcode.write(barcode_buffer, options={
                'module_width': 0.3,      # Standard bar width
                'module_height': 12,      # Reduced height to match ECUS
                'font_size': 0,           # No text below barcode (ECUS style)
                'text_distance': 1,       # Minimal text distance
                'quiet_zone': 2,          # Standard quiet zone
                'write_text': False,      # No text below barcode (ECUS style)
                'dpi': 300,               # Higher DPI for better quality
            })
            
            barcode_buffer.seek(0)
            
            # Verify barcode was generated
            barcode_data = barcode_buffer.getvalue()
            if not barcode_data or len(barcode_data) < 100:
                if self.logger:
                    self.logger.error(f"Barcode generation produced empty or too small data: {len(barcode_data)} bytes")
                return None
            
            # Reset buffer position for reading
            barcode_buffer.seek(0)
            
            # Create ReportLab Image with proper dimensions
            # Use larger dimensions to prevent compression/cropping
            img = Image(barcode_buffer, 
                       width=self.config.barcode_width, 
                       height=self.config.barcode_height)
            img.hAlign = 'RIGHT'
            
            if self.logger:
                self.logger.debug(f"Generated barcode image: {len(barcode_data)} bytes, {self.config.barcode_width}x{self.config.barcode_height}")
            
            return img
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to generate barcode: {e}")
                import traceback
                self.logger.debug(traceback.format_exc())
            return None

    def _decode_qr_image(self, base64_data: str) -> Optional[Image]:
        """
        Decode base64 encoded PNG to ReportLab Image.
        
        Args:
            base64_data: Base64 encoded PNG image data.
            
        Returns:
            ReportLab Image object, or None if decoding fails.
        """
        if not base64_data:
            return None
        
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_data)
            
            # Create BytesIO buffer
            image_buffer = io.BytesIO(image_bytes)
            
            # Create ReportLab Image with QR code size (~2cm x 2cm)
            img = Image(image_buffer, 
                       width=self.config.qr_code_size, 
                       height=self.config.qr_code_size)
            img.hAlign = 'CENTER'
            
            if self.logger:
                self.logger.debug(f"Decoded QR image: {len(image_bytes)} bytes")
            
            return img
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to decode QR image: {e}")
            return None
    
    def _build_container_table(self, containers: List[ContainerInfo]) -> Table:
        """
        Build 6-column table for container declarations.
        
        Args:
            containers: List of ContainerInfo objects.
            
        Returns:
            ReportLab Table object.
        """
        styles = self._get_styles()
        
        # Table header
        table_header = [
            'STT',
            'SỐ HIỆU\nCONTAINER\n(1)',
            'SỐ SEAL\nCONTAINER\n(Nếu có)\n(2)',
            'SỐ SEAL\nHẢI QUAN\n(Nếu có)\n(3)',
            'XÁC NHẬN\nCỦA\nCÔNG CHỨC\nHẢI QUAN\n(4)',
            'MÃ VẠCH\n(5)'
        ]
        
        table_data = [table_header]
        
        # Add container rows
        for cont in containers:
            # Decode QR image
            qr_img = self._decode_qr_image(cont.barcode_image)
            
            row = [
                str(cont.stt),
                cont.so_container,
                cont.so_seal if cont.so_seal else "",  # Show "NA" if that's the value
                cont.so_seal_hq,  # Already handled "#####" in parsing
                '',  # Empty for customs officer signature
                qr_img if qr_img else ''
            ]
            table_data.append(row)
        
        # Column widths (total ~17cm for A4 with margins - increased to match original)
        col_widths = [1.2*cm, 3*cm, 2.8*cm, 2.8*cm, 3.2*cm, 3*cm]
        
        container_table = Table(table_data, colWidths=col_widths)
        container_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # Increased from 9
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 11),  # Increased from 10
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWHEIGHT', (0, 0), (-1, 0), 60),  # Increased header row height
            ('ROWHEIGHT', (0, 1), (-1, -1), 65),  # Increased data row height for QR codes
        ]))
        
        return container_table
    
    def _build_container_content(self, info: ContainerDeclarationInfo) -> list:
        """
        Build PDF content elements for container declarations.
        
        Args:
            info: ContainerDeclarationInfo object.
            
        Returns:
            List of flowable elements for PDF.
        """
        elements = []
        styles = self._get_styles()
        
        # Calculate available width
        available_width = A4[0] - self.config.margin_left - self.config.margin_right
        
        # ===== HEADER SECTION (no barcode, no "- 2" indicator) =====
        # Format date
        today = datetime.now()
        date_str = f"Ngày {today.day:02d} tháng {today.month:02d} năm {today.year}"
        
        # Left column: Customs office info (same as regular PDF, no "- 2" indicator)
        ten_cuc_hq = info.ten_cuc_hai_quan or "Chi cục Hải quan khu vực V"
        ten_chi_cuc_hq = info.ten_chi_cuc_hai_quan or "Hải quan Bắc Ninh"
        
        header_line1 = Paragraph(ten_cuc_hq, styles['header_left_bold'])
        header_line2 = Paragraph(ten_chi_cuc_hq, styles['header_bold_center'])
        
        header_text_width = 160
        header_inner_table = Table(
            [[header_line1], [header_line2]],
            colWidths=[header_text_width]
        )
        header_inner_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (0, 1), (0, 1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # No "- 2" indicator - removed as per user feedback
        left_content = [header_inner_table]
        
        # Right column: Date only (no barcode for container PDF)
        right_content = [Paragraph(date_str, styles['date_right_italic'])]
        
        # Create header table
        header_data = [[left_content, right_content]]
        header_table = Table(header_data, colWidths=[available_width * 0.5, available_width * 0.5])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 15*mm))
        
        # ===== TITLE SECTION =====
        elements.append(Paragraph("DANH SÁCH CONTAINER", styles['title']))
        elements.append(Paragraph("ĐỦ ĐIỀU KIỆN QUA KHU VỰC GIÁM SÁT HẢI QUAN", styles['title']))
        
        # Sub-title
        ghi_chu = info.ghi_chu or "Tờ khai không phải niêm phong"
        elements.append(Paragraph(ghi_chu, styles['subtitle_black']))
        elements.append(Spacer(1, 8*mm))
        
        # ===== DECLARATION INFO SECTION (same as regular PDF) =====
        chi_cuc_gs = info.ten_chi_cuc_hai_quan_gs or 'CC HQ CK Sân bay QT Nội Bài'
        if info.ma_ddgs and info.ten_ddgs:
            ma_ptvc_str = f" - {info.ma_ptvc}" if info.ma_ptvc else ""
            chi_cuc_gs_full = f"{chi_cuc_gs} - {info.ma_ddgs}: {info.ten_ddgs}{ma_ptvc_str}"
        elif info.ten_ddgs:
            ma_ptvc_str = f" - {info.ma_ptvc}" if info.ma_ptvc else ""
            chi_cuc_gs_full = f"{chi_cuc_gs} - {info.ten_ddgs}{ma_ptvc_str}"
        else:
            chi_cuc_gs_full = chi_cuc_gs
        
        # Item 1 - full width
        elements.append(Paragraph(
            f"<font name='{self.font_bold}'>1. Chi cục hải quan giám sát:</font> {chi_cuc_gs_full}",
            styles['info']
        ))
        
        # Item 2 - full width
        elements.append(Paragraph(
            f"<font name='{self.font_bold}'>2. Đơn vị XNK:</font> {info.ten_don_vi_xnk}",
            styles['info']
        ))
        
        # Items 3-5 (left) and 6-8 (right)
        left_items = [
            f"<font name='{self.font_bold}'>3. Mã số thuế:</font> {info.ma_so_thue}",
            f"<font name='{self.font_bold}'>4. Số tờ khai:</font> {info.so_to_khai}",
            f"<font name='{self.font_bold}'>5. Trạng thái tờ khai:</font> {info.trang_thai_to_khai}",
        ]
        
        right_items = [
            f"<font name='{self.font_bold}'>6. Ngày tờ khai:</font> {info.ngay_to_khai}",
            f"<font name='{self.font_bold}'>7. Loại hình:</font> {info.ten_loai_hinh}",
            f"<font name='{self.font_bold}'>8. Luồng:</font> {info.luong_to_khai}",
        ]
        
        info_rows = []
        for i in range(len(left_items)):
            left_para = Paragraph(left_items[i], styles['info'])
            right_para = Paragraph(right_items[i], styles['info'])
            info_rows.append([left_para, right_para])
        
        info_table = Table(info_rows, colWidths=[available_width * 0.5, available_width * 0.5])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        elements.append(info_table)
        
        # Item 9 - full width
        elements.append(Paragraph(
            f"<font name='{self.font_bold}'>9. Số quản lý hàng hóa:</font> {info.so_dinh_danh}",
            styles['info']
        ))
        elements.append(Spacer(1, 6*mm))
        
        # ===== CONTAINER TABLE =====
        container_table = self._build_container_table(info.containers)
        elements.append(container_table)
        elements.append(Spacer(1, 5*mm))
        
        # ===== EXPORT INFO =====
        export_time = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        elements.append(Paragraph(
            f"Kết xuất dữ liệu lúc: {export_time}",
            styles['small_italic']
        ))
        elements.append(Spacer(1, 6*mm))
        
        # ===== NOTES SECTION =====
        notes = [
            "<i>Ghi chú:</i>",
            "- Cột số (1):",
            "    + Đối với hàng nhập khẩu: lấy từ Danh sách container do người khai hải quan gửi đến hệ thống.",
            "    + Đối với hàng xuất khẩu: lấy từ tiêu chí \"Số container\" trên tờ khai xuất.",
            "    Trường hợp có sự thay đổi số container đã khai báo, căn cứ chứng từ do người khai hải quan nộp; xuất trình, công chức hải quan cập nhật số container vào hệ thống để in lại danh sách container.",
            "- Cột số (2): Đối với hàng nhập khẩu: lấy từ Danh sách container do người khai hải quan gửi đến hệ thống.",
        ]
        
        for note in notes:
            elements.append(Paragraph(note, styles['note']))
        
        return elements
