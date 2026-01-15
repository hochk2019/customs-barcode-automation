 # Chú ý:
 • Giữ trí nhớ xuyên suốt nhiều lượt trao đổi
 • Duy trì trạng thái công việc trong một “sổ tay” thống nhất
 • Tránh cảnh AI bị quên ngữ cảnh khi context bị nén hay reset

## Tasks
- [x] Cập nhật dropdown lọc tab "Xem trước tờ khai" thành "Chỉ TK nhập", "Chỉ TK Xuất", "Cả TK Nhập & Xuất" và ghi nhớ lựa chọn.
- [x] Bổ sung cột "Công ty" hiển thị tên công ty rút gọn (giữ lại tên đầy đủ trong dữ liệu).
- [x] Sắp xếp lại cột tab "Xem trước tờ khai" theo thứ tự yêu cầu và cho phép ẩn/hiện cột.
- [x] Chạy test sau các thay đổi (pytest -x dừng ở test_barcode_retriever_properties.py::test_property_barcode_retrieval_fallback_chain).



- [x] Update BarcodeRetriever order: API -> primary web -> backup web.
- [x] Update tests to accept MV_ prefix.
- [x] Run full test suite: `python -m pytest tests -x` (pass).


- [x] Fix statistics bar updates (update_counts alias + last run).
- [x] Add test for statistics bar update_counts.


- [x] Wire on_download_complete callback after batch download to update statistics.
- [x] Add test for download completion callback in EnhancedManualPanel.


- [x] Dọn dẹp cache/test artifacts.
- [x] Bump version v1.5.3 và cập nhật hướng dẫn nhanh.
- [x] Cập nhật CHANGELOG cho v1.5.3.
- [x] Commit và push lên GitHub.
- [x] Tạo source zip v1.5.3 và build release exe/zip.
