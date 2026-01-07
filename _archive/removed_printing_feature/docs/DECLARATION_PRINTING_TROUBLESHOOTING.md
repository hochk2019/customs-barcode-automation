# Hướng dẫn khắc phục sự cố - Tính năng In Tờ Khai

## Mục lục

1. [Lỗi kết nối và cấu hình](#1-lỗi-kết-nối-và-cấu-hình)
2. [Lỗi template và file](#2-lỗi-template-và-file)
3. [Lỗi dữ liệu và xử lý](#3-lỗi-dữ-liệu-và-xử-lý)
4. [Lỗi giao diện và tương tác](#4-lỗi-giao-diện-và-tương-tác)
5. [Lỗi hiệu suất và tài nguyên](#5-lỗi-hiệu-suất-và-tài-nguyên)
6. [Công cụ chẩn đoán](#6-công-cụ-chẩn-đoán)

---

## 1. Lỗi kết nối và cấu hình

### 1.1. Nút "In TKTQ" bị vô hiệu hóa

**Triệu chứng:**
- Nút "In TKTQ" màu xám, không thể click
- Tooltip hiển thị lý do vô hiệu hóa

**Nguyên nhân và giải pháp:**

#### Nguyên nhân 1: Chưa chọn tờ khai
```
Tooltip: "Vui lòng chọn ít nhất một tờ khai"
```
**Giải pháp:**
1. Chọn ít nhất 1 tờ khai trong Preview Panel
2. Đảm bảo checkbox được tích ☑
3. Kiểm tra counter "Đã chọn: X/Y tờ khai" (X > 0)

#### Nguyên nhân 2: Tờ khai chưa thông quan
```
Tooltip: "Tờ khai được chọn chưa thông quan (TTTK ≠ 'T')"
```
**Giải pháp:**
1. Kiểm tra cột TTTK trong danh sách tờ khai
2. Chỉ chọn tờ khai có TTTK = "T"
3. Bỏ chọn tờ khai có TTTK = "N", "P", hoặc trống

#### Nguyên nhân 3: Mất kết nối database
```
Tooltip: "Không thể kết nối database"
```
**Giải pháp:**
1. Kiểm tra DB Status trong Control Panel
2. Nếu "Disconnected": Kiểm tra kết nối SQL Server
3. Chạy test: `python test_db_connection.py`
4. Kiểm tra config.ini có đúng thông tin database

#### Nguyên nhân 4: Template không hợp lệ
```
Tooltip: "Template Excel không tìm thấy hoặc không hợp lệ"
```
**Giải pháp:**
1. Chạy: `python scripts/validate_templates.py`
2. Nếu lỗi: Chạy `python scripts/setup_templates.py`
3. Kiểm tra thư mục `templates/` có đủ 4 file:
   - ToKhaiHQ7X_QDTQ.xlsx
   - ToKhaiHQ7X_QDTQ_mapping.json
   - ToKhaiHQ7N_QDTQ.xlsx
   - ToKhaiHQ7N_QDTQ_mapping.json

### 1.2. Lỗi "Database connection failed"

**Triệu chứng:**
```
ERROR: Database connection failed: [Errno 2] No such file or directory
```

**Nguyên nhân và giải pháp:**

#### Kiểm tra SQL Server
```bash
# Kiểm tra SQL Server đang chạy
services.msc → SQL Server (MSSQLSERVER) → Status: Running
```

#### Kiểm tra ODBC Driver
```bash
# Kiểm tra ODBC Driver đã cài đặt
odbcad32.exe → Drivers → Tìm "ODBC Driver 17 for SQL Server"
```

#### Kiểm tra config.ini
```ini
[Database]
server = localhost          # Hoặc IP server
database = ECUS5VNACCS     # Tên database chính xác
username = sa              # User có quyền đọc
password = your_password   # Mật khẩu đúng
timeout = 30
```

#### Test kết nối
```bash
python test_db_connection.py
```

**Kết quả mong đợi:**
```
✓ Kết nối database thành công
✓ Truy vấn test thành công
✓ Tìm thấy 1,234 tờ khai trong 7 ngày gần nhất
```

### 1.3. Lỗi "Permission denied"

**Triệu chứng:**
```
ERROR: Permission denied: Cannot write to output directory
```

**Giải pháp:**

#### Kiểm tra quyền thư mục
1. Right-click thư mục output → Properties → Security
2. Đảm bảo user hiện tại có quyền "Full Control" hoặc "Modify"
3. Nếu không có quyền: Add user và cấp quyền

#### Thay đổi thư mục output
1. Mở Enhanced Manual Mode
2. Click "Chọn..." bên cạnh "Thư mục lưu:"
3. Chọn thư mục khác có quyền ghi
4. Ví dụ: `C:\Users\[Username]\Documents\CustomsDeclarations`

#### Chạy với quyền Administrator
1. Right-click ứng dụng → "Run as administrator"
2. Hoặc thay đổi properties → Compatibility → "Run as administrator"

---

## 2. Lỗi template và file

### 2.1. Lỗi "Template not found"

**Triệu chứng:**
```
ERROR: Template file not found: ToKhaiHQ7N_QDTQ.xlsx
```

**Giải pháp:**

#### Kiểm tra file template
```bash
# Liệt kê file trong thư mục templates
dir templates\
```

**Kết quả mong đợi:**
```
ToKhaiHQ7N_QDTQ.xlsx
ToKhaiHQ7N_QDTQ_mapping.json
ToKhaiHQ7X_QDTQ.xlsx
ToKhaiHQ7X_QDTQ_mapping.json
```

#### Cài đặt lại template
```bash
# Tự động cài đặt template
python scripts/setup_templates.py

# Hoặc thủ công copy từ thư mục sample
copy sample\ToKhaiHQ7N_QDTQ.xlsx templates\
copy sample\ToKhaiHQ7N_QDTQ_mapping.json templates\
```

#### Kiểm tra đường dẫn template
```ini
# Trong config.ini
[DeclarationPrinting]
template_directory = templates    # Đường dẫn tương đối
# Hoặc
template_directory = C:\CustomsBarcodeAutomation\templates  # Đường dẫn tuyệt đối
```

### 2.2. Lỗi "Invalid template format"

**Triệu chứng:**
```
ERROR: Invalid template format: File is not a valid Excel file
```

**Nguyên nhân:**
- File template bị hỏng
- File không phải định dạng Excel
- File bị khóa bởi Excel

**Giải pháp:**

#### Kiểm tra file template
1. Mở file template bằng Excel
2. Nếu không mở được: File bị hỏng
3. Nếu Excel báo lỗi: File không đúng định dạng

#### Tải lại template gốc
```bash
# Backup file hiện tại
copy templates\ToKhaiHQ7N_QDTQ.xlsx templates\ToKhaiHQ7N_QDTQ_backup.xlsx

# Copy từ sample
copy sample\ToKhaiHQ7N_QDTQ.xlsx templates\

# Kiểm tra lại
python scripts\validate_templates.py
```

#### Đóng Excel trước khi chạy
- Đảm bảo không có file Excel nào đang mở
- Đặc biệt là file template
- Excel có thể khóa file và gây lỗi

### 2.3. Lỗi "Mapping file invalid"

**Triệu chứng:**
```
ERROR: Invalid mapping file: JSON decode error
```

**Nguyên nhân:**
- File mapping JSON bị lỗi cú pháp
- File bị thiếu hoặc hỏng
- Encoding không đúng

**Giải pháp:**

#### Kiểm tra cú pháp JSON
```bash
# Sử dụng Python để kiểm tra
python -m json.tool templates\ToKhaiHQ7N_QDTQ_mapping.json
```

**Nếu lỗi cú pháp:**
```
Expecting ',' delimiter: line 15 column 5 (char 234)
```

#### Sửa file mapping
1. Mở file bằng text editor (Notepad++, VS Code)
2. Kiểm tra:
   - Dấu phẩy cuối dòng
   - Dấu ngoặc kép đúng
   - Không có ký tự đặc biệt
3. Lưu với encoding UTF-8

#### Khôi phục file mapping mẫu
```bash
copy sample\ToKhaiHQ7N_QDTQ_mapping.json templates\
```

### 2.4. Lỗi "File already exists"

**Triệu chứng:**
```
WARNING: File already exists: ToKhaiHQ7N_QDTQ_107772836360.xlsx
```

**Hành vi mặc định:**
- Hệ thống hiển thị dialog lựa chọn
- Có thể chọn: Ghi đè, Đổi tên, Bỏ qua

**Tùy chọn xử lý:**

#### Ghi đè (Overwrite)
- Thay thế file cũ bằng file mới
- Mất dữ liệu file cũ
- Phù hợp khi cần cập nhật

#### Đổi tên (Rename)
- Tạo file mới với tên khác
- Thêm số thứ tự: `ToKhaiHQ7N_QDTQ_107772836360_001.xlsx`
- Giữ nguyên file cũ

#### Bỏ qua (Skip)
- Không tạo file mới
- Giữ nguyên file cũ
- Tiếp tục với tờ khai khác

#### Cấu hình xử lý tự động
```ini
# Trong config.ini
[DeclarationPrinting]
file_conflict_action = overwrite    # overwrite, rename, skip
```

---

## 3. Lỗi dữ liệu và xử lý

### 3.1. Lỗi "Declaration data not found"

**Triệu chứng:**
```
WARNING: No data found for declaration: 107772836360
```

**Nguyên nhân:**
- Tờ khai không tồn tại trong database
- Tờ khai đã bị xóa
- Lỗi truy vấn database

**Giải pháp:**

#### Kiểm tra tờ khai trong database
```sql
-- Truy vấn trực tiếp database
SELECT * FROM ToKhai WHERE SoToKhai = '107772836360'
```

#### Kiểm tra kết nối database
```bash
python test_db_connection.py
```

#### Sử dụng file XML backup
1. Tìm file XML tương ứng trong thư mục `sample/`
2. Format: `ECUS5VNACCS2018_ToKhai_107772836360_STT*.xml`
3. Hệ thống tự động fallback sang XML nếu database fail

### 3.2. Lỗi "Invalid declaration number format"

**Triệu chứng:**
```
ERROR: Invalid declaration number format: ABC123
```

**Nguyên nhân:**
- Số tờ khai không đúng định dạng
- Chứa ký tự không hợp lệ
- Độ dài không đúng

**Định dạng hợp lệ:**
- **Xuất khẩu**: 30XXXXXXXXXX (12 số, bắt đầu bằng 30)
- **Nhập khẩu**: 10XXXXXXXXXX (12 số, bắt đầu bằng 10)
- **Ví dụ**: 305254403660, 107772836360

**Giải pháp:**
1. Kiểm tra lại số tờ khai trong ECUS
2. Đảm bảo copy đúng 12 số
3. Không có khoảng trắng hoặc ký tự đặc biệt

### 3.3. Lỗi "Data extraction failed"

**Triệu chứng:**
```
ERROR: Failed to extract data from all sources for: 107772836360
```

**Nguyên nhân:**
- Database và XML đều không khả dụng
- Dữ liệu bị hỏng
- Lỗi parsing XML

**Giải pháp:**

#### Kiểm tra database
```bash
python test_db_connection.py
```

#### Kiểm tra file XML
1. Tìm file XML trong thư mục `sample/`
2. Mở bằng text editor
3. Kiểm tra cấu trúc XML hợp lệ
4. Tìm tag `<SoToKhai>107772836360</SoToKhai>`

#### Tạo template với dữ liệu cơ bản
- Hệ thống sẽ tạo template với thông tin có sẵn
- Điền thủ công các trường còn thiếu
- Lưu file để tham khảo

### 3.4. Lỗi "Excel generation failed"

**Triệu chứng:**
```
ERROR: Failed to generate Excel file: Worksheet 'Sheet1' not found
```

**Nguyên nhân:**
- Template Excel bị hỏng cấu trúc
- Worksheet bị đổi tên hoặc xóa
- Lỗi thư viện openpyxl

**Giải pháp:**

#### Kiểm tra cấu trúc template
1. Mở template bằng Excel
2. Kiểm tra có worksheet tên "Sheet1"
3. Nếu không có: Đổi tên worksheet về "Sheet1"

#### Khôi phục template gốc
```bash
copy sample\ToKhaiHQ7N_QDTQ.xlsx templates\
```

#### Cập nhật thư viện
```bash
pip install --upgrade openpyxl
```

---

## 4. Lỗi giao diện và tương tác

### 4.1. Thanh tiến trình không cập nhật

**Triệu chứng:**
- Thanh tiến trình đứng yên
- Không hiển thị tờ khai đang xử lý
- UI bị đóng băng

**Nguyên nhân:**
- Thread UI bị block
- Lỗi callback progress
- Quá trình xử lý quá lâu

**Giải pháp:**

#### Đợi thêm thời gian
- Mỗi tờ khai mất 2-5 giây
- Batch lớn có thể mất 10-15 phút
- Kiểm tra log để xem có đang xử lý

#### Kiểm tra log real-time
```bash
tail -f logs\declaration_printing.log
```

#### Restart ứng dụng nếu cần
- Nếu UI đóng băng > 5 phút
- Ctrl+Alt+Del → Task Manager → End task
- Khởi động lại ứng dụng

### 4.2. Nút "Dừng" không hoạt động

**Triệu chứng:**
- Click "Dừng" nhưng quá trình vẫn tiếp tục
- Nút không phản hồi

**Nguyên nhân:**
- Hệ thống đang hoàn thành tờ khai hiện tại
- Thread không nhận signal dừng
- UI lag

**Giải pháp:**

#### Đợi tờ khai hiện tại hoàn thành
- Hệ thống sẽ dừng sau khi hoàn thành tờ khai đang xử lý
- Thường mất 5-10 giây
- Không click "Dừng" nhiều lần

#### Force stop nếu cần
- Nếu không dừng sau 30 giây
- Đóng ứng dụng và khởi động lại
- Kiểm tra file đã tạo trong output directory

### 4.3. Dialog xác nhận không hiển thị

**Triệu chứng:**
- Click "In TKTQ" nhưng không có dialog
- Không có phản hồi gì

**Nguyên nhân:**
- Dialog bị ẩn sau cửa sổ khác
- Lỗi UI thread
- Validation fail ngầm

**Giải pháp:**

#### Tìm dialog ẩn
- Alt+Tab để chuyển giữa các cửa sổ
- Kiểm tra taskbar có cửa sổ dialog
- Click vào icon ứng dụng trong taskbar

#### Kiểm tra log
```bash
tail -5 logs\app.log
```

#### Thử lại với ít tờ khai hơn
- Chọn chỉ 1-2 tờ khai
- Kiểm tra có dialog xuất hiện không

---

## 5. Lỗi hiệu suất và tài nguyên

### 5.1. Xử lý quá chậm

**Triệu chứng:**
- Mỗi tờ khai mất > 10 giây
- Batch nhỏ mất > 10 phút
- CPU hoặc Memory cao

**Nguyên nhân:**
- Database chậm
- Template lớn
- Thiếu RAM
- Ổ cứng chậm

**Giải pháp:**

#### Tối ưu database
- Đóng ECUS khi chạy batch lớn
- Chạy vào giờ ít tải
- Kiểm tra SQL Server performance

#### Giảm kích thước batch
- Thay vì 100 tờ khai → 20 tờ khai
- Chạy nhiều lần nhỏ thay vì 1 lần lớn

#### Kiểm tra tài nguyên hệ thống
```bash
# Task Manager → Performance
CPU: < 80%
Memory: < 80%
Disk: < 90%
```

#### Đóng ứng dụng khác
- Đóng Excel, Word, Browser
- Tạm dừng antivirus scan
- Đóng các ứng dụng không cần thiết

### 5.2. Lỗi "Out of memory"

**Triệu chứng:**
```
ERROR: MemoryError: Unable to allocate memory
```

**Nguyên nhân:**
- Batch quá lớn
- Template Excel quá lớn
- Memory leak
- RAM không đủ

**Giải pháp:**

#### Giảm kích thước batch
- Tối đa 50 tờ khai mỗi lần
- Chia thành nhiều batch nhỏ

#### Restart ứng dụng
- Đóng và mở lại ứng dụng
- Clear memory cache

#### Tăng RAM nếu có thể
- Khuyến nghị: ít nhất 8GB RAM
- Đóng các ứng dụng khác

### 5.3. Lỗi "Disk full"

**Triệu chứng:**
```
ERROR: No space left on device
```

**Giải pháp:**

#### Kiểm tra dung lượng ổ cứng
```bash
dir C:\ 
# Xem "bytes free"
```

#### Dọn dẹp file cũ
- Xóa file Excel cũ không cần thiết
- Dọn Recycle Bin
- Chạy Disk Cleanup

#### Chuyển thư mục output
1. Chọn ổ cứng khác có dung lượng
2. Cập nhật trong Enhanced Manual Mode
3. Hoặc sửa config.ini

---

## 6. Công cụ chẩn đoán

### 6.1. Script kiểm tra tổng thể

**Tạo file: `diagnosis.py`**
```python
import os
import sys
import json
from pathlib import Path

def check_templates():
    """Kiểm tra template files"""
    template_dir = Path("templates")
    required_files = [
        "ToKhaiHQ7N_QDTQ.xlsx",
        "ToKhaiHQ7N_QDTQ_mapping.json",
        "ToKhaiHQ7X_QDTQ.xlsx", 
        "ToKhaiHQ7X_QDTQ_mapping.json"
    ]
    
    print("=== KIỂM TRA TEMPLATE ===")
    for file in required_files:
        file_path = template_dir / file
        if file_path.exists():
            print(f"✓ {file}: OK ({file_path.stat().st_size} bytes)")
        else:
            print(f"✗ {file}: MISSING")

def check_output_directory():
    """Kiểm tra thư mục output"""
    print("\n=== KIỂM TRA THU MỤC OUTPUT ===")
    
    # Đọc từ config
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        output_dir = config.get('DeclarationPrinting', 'output_directory', fallback='output')
    except:
        output_dir = 'output'
    
    output_path = Path(output_dir)
    
    if output_path.exists():
        print(f"✓ Thư mục tồn tại: {output_path.absolute()}")
        
        # Kiểm tra quyền ghi
        test_file = output_path / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("✓ Có quyền ghi")
        except:
            print("✗ Không có quyền ghi")
            
        # Kiểm tra dung lượng
        import shutil
        total, used, free = shutil.disk_usage(output_path)
        free_gb = free // (1024**3)
        print(f"✓ Dung lượng trống: {free_gb} GB")
        
    else:
        print(f"✗ Thư mục không tồn tại: {output_path.absolute()}")

def check_database():
    """Kiểm tra kết nối database"""
    print("\n=== KIỂM TRA DATABASE ===")
    
    try:
        from config.configuration_manager import ConfigurationManager
        config_manager = ConfigurationManager()
        db_config = config_manager.get_database_config()
        
        print(f"✓ Server: {db_config.get('server', 'N/A')}")
        print(f"✓ Database: {db_config.get('database', 'N/A')}")
        print(f"✓ Username: {db_config.get('username', 'N/A')}")
        
        # Test connection
        from database.ecus_connector import ECUSConnector
        connector = ECUSConnector(db_config)
        
        if connector.test_connection():
            print("✓ Kết nối thành công")
        else:
            print("✗ Kết nối thất bại")
            
    except Exception as e:
        print(f"✗ Lỗi kiểm tra database: {e}")

def check_dependencies():
    """Kiểm tra Python packages"""
    print("\n=== KIỂM TRA DEPENDENCIES ===")
    
    required_packages = [
        'openpyxl',
        'lxml', 
        'pyodbc',
        'tkinter'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}: OK")
        except ImportError:
            print(f"✗ {package}: MISSING")

if __name__ == "__main__":
    print("CHẨN ĐOÁN HỆ THỐNG IN TỜ KHAI")
    print("=" * 40)
    
    check_templates()
    check_output_directory()
    check_database()
    check_dependencies()
    
    print("\n=== HOÀN THÀNH ===")
    print("Nếu có lỗi ✗, vui lòng khắc phục trước khi sử dụng tính năng in tờ khai.")
```

**Chạy chẩn đoán:**
```bash
python diagnosis.py
```

### 6.2. Log analysis script

**Tạo file: `analyze_logs.py`**
```python
import re
from pathlib import Path
from datetime import datetime, timedelta

def analyze_declaration_logs():
    """Phân tích log in tờ khai"""
    log_file = Path("logs/declaration_printing.log")
    
    if not log_file.exists():
        print("Không tìm thấy file log")
        return
    
    print("=== PHÂN TÍCH LOG IN TỜ KHAI ===")
    
    # Đọc log 24h gần nhất
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    errors = []
    successes = []
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Parse timestamp
            timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if not timestamp_match:
                continue
                
            timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
            if timestamp < cutoff_time:
                continue
            
            # Phân loại log
            if 'ERROR' in line:
                errors.append(line.strip())
            elif 'Successfully generated' in line:
                successes.append(line.strip())
    
    print(f"Thành công: {len(successes)}")
    print(f"Lỗi: {len(errors)}")
    
    if errors:
        print("\n=== LỖI GẦN NHẤT ===")
        for error in errors[-5:]:  # 5 lỗi gần nhất
            print(error)
    
    # Thống kê lỗi
    error_types = {}
    for error in errors:
        if 'Template not found' in error:
            error_types['Template'] = error_types.get('Template', 0) + 1
        elif 'Database' in error:
            error_types['Database'] = error_types.get('Database', 0) + 1
        elif 'Permission' in error:
            error_types['Permission'] = error_types.get('Permission', 0) + 1
        else:
            error_types['Other'] = error_types.get('Other', 0) + 1
    
    if error_types:
        print("\n=== THỐNG KÊ LỖI ===")
        for error_type, count in error_types.items():
            print(f"{error_type}: {count}")

if __name__ == "__main__":
    analyze_declaration_logs()
```

### 6.3. Quick fix script

**Tạo file: `quick_fix.py`**
```python
import os
import shutil
from pathlib import Path

def fix_templates():
    """Sửa lỗi template"""
    print("Đang sửa lỗi template...")
    
    # Tạo thư mục templates nếu chưa có
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    
    # Copy từ sample nếu có
    sample_dir = Path("sample")
    if sample_dir.exists():
        template_files = [
            "ToKhaiHQ7N_QDTQ.xlsx",
            "ToKhaiHQ7N_QDTQ_mapping.json",
            "ToKhaiHQ7X_QDTQ.xlsx",
            "ToKhaiHQ7X_QDTQ_mapping.json"
        ]
        
        for file in template_files:
            src = sample_dir / file
            dst = template_dir / file
            
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
                print(f"✓ Copied {file}")

def fix_output_directory():
    """Sửa lỗi thư mục output"""
    print("Đang sửa lỗi thư mục output...")
    
    # Tạo thư mục output mặc định
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Kiểm tra quyền ghi
    test_file = output_dir / "test.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Thư mục output OK")
    except:
        # Thử tạo trong Documents
        import os
        docs_dir = Path.home() / "Documents" / "CustomsDeclarations"
        docs_dir.mkdir(exist_ok=True)
        print(f"✓ Tạo thư mục backup: {docs_dir}")

def fix_config():
    """Sửa lỗi config cơ bản"""
    print("Đang kiểm tra config...")
    
    config_file = Path("config.ini")
    if not config_file.exists():
        # Tạo config mẫu
        sample_config = """[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = 
timeout = 30

[DeclarationPrinting]
output_directory = output
template_directory = templates
file_conflict_action = ask
"""
        config_file.write_text(sample_config, encoding='utf-8')
        print("✓ Tạo config.ini mẫu")

if __name__ == "__main__":
    print("QUICK FIX - SỬA LỖI NHANH")
    print("=" * 30)
    
    fix_templates()
    fix_output_directory()
    fix_config()
    
    print("\n✓ Hoàn thành quick fix")
    print("Vui lòng chạy lại ứng dụng và thử nghiệm tính năng in tờ khai")
```

### 6.4. Hướng dẫn sử dụng công cụ chẩn đoán

#### Khi gặp lỗi lần đầu:
```bash
# 1. Chạy chẩn đoán tổng thể
python diagnosis.py

# 2. Nếu có lỗi cơ bản, chạy quick fix
python quick_fix.py

# 3. Phân tích log nếu vẫn có vấn đề
python analyze_logs.py
```

#### Khi cần hỗ trợ:
1. Chạy `python diagnosis.py` và gửi kết quả
2. Chạy `python analyze_logs.py` và gửi 10 dòng lỗi gần nhất
3. Gửi file `config.ini` (ẩn mật khẩu)
4. Mô tả chi tiết các bước đã thực hiện

---

## Liên hệ hỗ trợ

**Khi cần hỗ trợ, vui lòng cung cấp:**

1. **Thông báo lỗi chính xác** (copy từ log hoặc dialog)
2. **Kết quả chẩn đoán** (`python diagnosis.py`)
3. **Log gần nhất** (10-20 dòng cuối trong `logs/declaration_printing.log`)
4. **Các bước tái hiện lỗi**
5. **Screenshot** (nếu là lỗi giao diện)

**Thông tin liên hệ:**
- Email: Hochk2019@gmail.com
- Điện thoại: 0868.333.606
- Tài liệu bổ sung: `docs/TEMPLATE_CUSTOMIZATION_GUIDE.md`

---

*Cập nhật: Tháng 12/2024 - Phiên bản 1.3.4*