# Codex Review v1 – Customs Barcode Automation

## Các phát hiện (ưu tiên theo mức độ)

### Critical
1) **DB connector v2.0 vẫn gọi `_connection` cũ → workflow có thể crash**
   - **Vấn đề**: Sau khi chuyển sang ConnectionPool, `self._connection` không còn được khởi tạo, nhưng `get_new_declarations()` và `get_company_name()` vẫn dùng `_connection.cursor()`. Đây là đường chạy chính của Scheduler nên sẽ gây `AttributeError` và làm workflow dừng.
   - **Chứng cứ**: `database/ecus_connector.py:333`, `database/ecus_connector.py:458`, `scheduler/scheduler.py:267`.
   - **Tác động**: Tự động/manual workflow (Scheduler) có thể hỏng hoàn toàn khi truy vấn tờ khai mới hoặc lấy tên công ty.
   - **Hướng xử lý**:
     - Thay `_connection.cursor()` bằng `self.get_connection().cursor()` trong các hàm trên.
     - Xóa hoặc deprecate `_connection` để tránh sử dụng nhầm.
     - Thêm test smoke cho `get_new_declarations()` và `get_company_name()` với pool.

2) **Cột “Kết quả” ở tab “Xem trước tờ khai” cập nhật không ổn định**
   - **Vấn đề**: `PreviewPanel.update_item_result()` so sánh trực tiếp `values[1] == declaration_number` (không normalize), nên nếu `declaration_number` là int/chuỗi có khoảng trắng/leading zeros thì không match. Đồng thời hàm này set tag `success|error` và *ghi đè toàn bộ tags* (mất `oddrow/evenrow` và tag kết quả), khiến màu kết quả không đúng/không hiện rõ.
   - **Chứng cứ**: `gui/preview_panel.py:723`, `gui/styles.py:514`, `tests/test_v151_bugfixes.py:122`.
   - **Tác động**: Cột “Kết quả” không hiển thị hoặc hiển thị sai; màu sắc/row style bị mất; test hiện tại sẽ fail.
   - **Hướng xử lý** (chi tiết ở phần “Hướng xử lý cụ thể…” bên dưới):
     - Normalize `declaration_number` khi so sánh (str/strip).
     - Không ghi đè tags; giữ `oddrow/evenrow` và thêm `success_result/error_result`.
     - Cập nhật lại dữ liệu `_declarations` để đồng bộ.

### High
3) **PreviewPanel có filter UI nhưng không có logic lọc**
   - **Vấn đề**: `_on_filter_change()` chỉ cập nhật state, không lọc bảng.
   - **Chứng cứ**: `gui/preview_panel.py:569`.
   - **Tác động**: Người dùng đổi filter nhưng không thấy thay đổi; dễ hiểu lầm là lỗi dữ liệu/kết quả.
   - **Hướng xử lý**: Tích hợp `PreviewTableController` hoặc viết filter riêng cho PreviewPanel (chú ý cấu trúc cột khác `PreviewTableController`). Đồng bộ lại selection count sau lọc.

4) **TrackingDatabase không dùng `_get_connection()` → nguy cơ “database is locked” khi tải song song**
   - **Vấn đề**: Đã có `_get_connection()` với `busy_timeout`, nhưng nhiều hàm dùng `sqlite3.connect()` trực tiếp.
   - **Chứng cứ**: `database/tracking_database.py:347`, `database/tracking_database.py:387`.
   - **Tác động**: Khi `ThreadPoolExecutor` tải song song (`enhanced_manual_panel`), ghi SQLite có thể bị lock/random fail.
   - **Hướng xử lý**:
     - Dùng `_get_connection()` trong mọi thao tác DB.
     - Cân nhắc bật WAL (`PRAGMA journal_mode=WAL`) trong `_initialize_database()`.
     - Bọc thao tác ghi bằng retry ngắn khi bị lock.

5) **Module `gui/preview_panel_integration.py` bị thiếu nhưng docs/tests yêu cầu**
   - **Vấn đề**: Nhiều tài liệu & test import module này nhưng file không tồn tại.
   - **Chứng cứ**: `docs/DECLARATION_PRINTING_DOCUMENTATION_README.md:210`, `tests/test_preview_panel_print_integration.py:13`.
   - **Tác động**: Tính năng in TKTQ/print integration không chạy; test suite fail ngay từ import.
   - **Hướng xử lý**: Khôi phục module hoặc cập nhật docs/tests cho đúng. Nếu đã bỏ tính năng, cần remove/mark deprecated toàn bộ references.

### Medium
6) **Duplicate method `get_selected_declarations_data()` trong `PreviewPanel`**
   - **Vấn đề**: Hàm bị khai báo 2 lần, bản sau override bản trước (mất nhánh fallback). Dễ gây nhầm lẫn và bug khó trace.
   - **Chứng cứ**: `gui/preview_panel.py:626`, `gui/preview_panel.py:697`.
   - **Tác động**: Hành vi không nhất quán; khó maintain.
   - **Hướng xử lý**: Gộp thành một hàm duy nhất, giữ fallback rõ ràng.

7) **Mapping `_declarations` theo `declaration_number` có thể rơi dữ liệu nếu trùng số tờ khai**
   - **Vấn đề**: `decl_map = {declaration_number: d}` sẽ overwrite nếu trùng số tờ khai khác MST/ngày.
   - **Chứng cứ**: `gui/preview_panel.py:638`, `gui/preview_panel.py:712`.
   - **Tác động**: Chọn tờ khai có thể trả về sai record trong trường hợp trùng số.
   - **Hướng xử lý**: Dùng key composite (`tax_code + declaration_number + date`) hoặc lưu map theo item_id của treeview.

8) **`PreviewPanel.update_item_status()` thêm tag `cleared` nhưng không có style**
   - **Vấn đề**: Tag `cleared` không được `configure_treeview_tags` định nghĩa.
   - **Chứng cứ**: `gui/preview_panel.py:662`, `gui/styles.py:514`.
   - **Tác động**: Trạng thái “Thông quan” không đổi màu như kỳ vọng.
   - **Hướng xử lý**: Đổi sang tag `success` hoặc định nghĩa `cleared` trong styles.

### Low
9) **Mã nguồn GUI/phần xử lý quá lớn, trộn UI + business logic**
   - **Vấn đề**: `enhanced_manual_panel.py` và `customs_gui.py` rất dài, trộn nhiều trách nhiệm.
   - **Tác động**: Khó test, khó maintain, dễ phát sinh lỗi tương tác.
   - **Hướng xử lý**: Tách thành controller/service lớp trung gian (PreviewController, DownloadController, SelectionController), tách view components nhỏ hơn.


## Hướng xử lý cụ thể cho lỗi cột “Kết quả” (tab “Xem trước tờ khai”)

### 1) Sửa `PreviewPanel.update_item_result()` để match ID chắc chắn và giữ tags
- **File**: `gui/preview_panel.py:723`.
- **Ý tưởng sửa**:
  - Normalize `declaration_number` trước khi so sánh: `target = str(declaration_number).strip()`.
  - Lấy `values[1]` cũng normalize: `current = str(values[1]).strip()`.
  - Khi update tags, *không* set `(tag,)` mà cần giữ `oddrow/evenrow` và thêm `success_result/error_result`.
  - Nếu muốn tô cả hàng, thêm `success/error` nhưng giữ tags hiện có.
- **Pseudo**:
  ```python
  target = str(declaration_number).strip()
  for item in self.preview_tree.get_children():
      values = self.preview_tree.item(item, "values")
      if not values:
          continue
      current = str(values[1]).strip()
      if current != target:
          continue
      new_values = list(values)
      new_values[8] = result
      self.preview_tree.item(item, values=tuple(new_values))

      tags = list(self.preview_tree.item(item, "tags"))
      tags = [t for t in tags if t not in ("success_result", "error_result", "success", "error")]
      tags.append("success_result" if is_success else "error_result")
      self.preview_tree.item(item, tags=tuple(tags))
      break
  ```

### 2) Đồng bộ dữ liệu `_declarations`
- **Lý do**: `get_selected_declarations_data()` trả về data gốc. Nếu không cập nhật `result`, thông tin luôn rỗng.
- **Cách làm**: Khi update kết quả, tìm bản ghi trong `_declarations` có `declaration_number` khớp và set `result`.

### 3) Update `get_failed_declarations()` để dựa vào result column
- **Hiện tại**: `get_failed_declarations()` đọc tags `error` → dễ sai khi đổi tags.
- **Cách làm**: Dựa vào giá trị `values[8] == "✘"` hoặc tag `error_result`.

### 4) Bổ sung test
- **Tối thiểu**:
  - test match `int` vs `str` (đã có nhưng đang fail) → `tests/test_v151_bugfixes.py:122`.
  - test update giữ `oddrow/evenrow` và add `success_result/error_result`.
  - test `get_failed_declarations()` trả đúng khi kết quả “✘”.


## Đề xuất nâng cấp/refactor (không bắt buộc, nhưng nên làm)
1) **Chuẩn hóa controller cho PreviewPanel**
   - Tạo `PreviewPanelController` dùng chung cho cả internal/external panel.
   - Cho phép cấu hình index cột (`result_index`, `decl_index`) để tránh hardcode.

2) **Tách logic download khỏi GUI**
   - Hiện tại `EnhancedManualPanel` vừa quản lý UI, vừa download, vừa update DB.
   - Gợi ý tách `DownloadService` (download + save + update DB), trả về events để UI subscribe.

3) **Chuẩn hóa data model trả về từ UI**
   - `PreviewPanel.get_selected_declarations_data()` trả dict; nơi khác dùng `Declaration`.
   - Nên thống nhất 1 dạng (dataclass hoặc DTO) để tránh lỗi parse `date`.

4) **Chuẩn hóa encoding & string resources**
   - Nhiều chuỗi UI đang hiển thị dạng mojibake khi đọc file (ví dụ “Xem tru?c t? khai”).
   - Kiểm tra encoding file (`UTF-8`), và cân nhắc đưa string vào file resource để dễ maintain/translate.


## Gợi ý kiểm thử sau khi sửa
1) Chạy test liên quan preview & kết quả:
   - `tests/test_v151_bugfixes.py::test_update_item_result_safety`
   - (Nếu phục hồi module in) `tests/test_preview_panel_print_integration.py`
2) Chạy luồng thực tế:
   - Xem trước tờ khai → tải mã vạch → kiểm tra cột “Kết quả” hiển thị ✔/✘ và màu đúng.
   - Retry failed → đảm bảo chỉ chọn các dòng “✘”.
3) Chạy luồng scheduler (nếu còn dùng):
   - `Scheduler.run_once()` để xác nhận `get_new_declarations()` không còn lỗi `_connection`.
