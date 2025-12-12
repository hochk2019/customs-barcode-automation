# What's New in Version 2.0

## 🎉 Tính năng mới

### 1. 🚀 Enhanced Manual Mode - Kiểm soát chi tiết hơn!

**Tính năng mới mạnh mẽ nhất trong phiên bản này!**

Enhanced Manual Mode cho phép bạn kiểm soát hoàn toàn quá trình xử lý tờ khai:

#### 🏢 Quét và quản lý công ty
- **Quét công ty**: Tự động quét database để lấy danh sách tất cả công ty có tờ khai
- **Lưu trữ lâu dài**: Danh sách công ty được lưu vào database, không cần quét lại mỗi lần
- **Làm mới nhanh**: Nút "Làm mới" để reload danh sách công ty đã lưu
- **Tên công ty tự động**: Hệ thống tự động lấy tên công ty từ bảng DaiLy_DoanhNghiep

**Cách sử dụng**:
```
1. Nhấn "Quét công ty" (lần đầu tiên)
2. Chờ 10-30 giây để quét hoàn tất
3. Danh sách công ty xuất hiện trong dropdown
4. Lần sau chỉ cần nhấn "Làm mới"
```

#### 📅 Chọn khoảng thời gian chính xác
- **Date Picker**: Chọn "Từ ngày" và "Đến ngày" thay vì chỉ số ngày
- **Validation thông minh**: 
  - Không cho phép ngày bắt đầu trong tương lai
  - Không cho phép ngày kết thúc trước ngày bắt đầu
  - Cảnh báo nếu khoảng thời gian > 90 ngày
- **Linh hoạt**: Chọn bất kỳ khoảng thời gian nào bạn muốn

**Ví dụ**:
```
Từ ngày: 01/12/2024
Đến ngày: 07/12/2024
→ Chỉ xử lý tờ khai trong tuần đầu tháng 12
```

#### 👁️ Xem trước tờ khai trước khi xử lý
- **Preview Table**: Hiển thị danh sách tất cả tờ khai sẽ được xử lý
- **Thông tin chi tiết**: Số tờ khai, mã số thuế, ngày tháng
- **Đếm tự động**: "Đã chọn: X/Y tờ khai"
- **Hủy preview**: Nút "Hủy" nếu query mất quá nhiều thời gian

**Lợi ích**:
- Xác nhận trước khi tải mã vạch
- Tránh xử lý nhầm
- Biết chính xác số lượng tờ khai

#### ✅ Chọn lọc từng tờ khai cụ thể
- **Checkbox cho mỗi tờ khai**: Chọn/bỏ chọn từng tờ khai
- **Chọn tất cả**: Nút "Chọn tất cả" để toggle tất cả checkbox
- **Selective download**: Chỉ tải mã vạch cho tờ khai đã chọn
- **Bỏ qua tờ khai**: Dễ dàng bỏ qua tờ khai đã xử lý hoặc có vấn đề

**Use cases**:
```
✓ Bỏ qua tờ khai đã xử lý
✓ Chỉ xử lý tờ khai mới
✓ Test với 2-3 tờ khai trước
✓ Bỏ qua tờ khai có lỗi
```

#### ⏸️ Dừng download đang chạy
- **Nút "Dừng"**: Xuất hiện khi đang tải mã vạch
- **Dừng an toàn**: Hoàn thành tờ khai hiện tại trước khi dừng
- **Lưu tiến trình**: Tất cả tờ khai đã xử lý được lưu lại
- **Tóm tắt kết quả**: Hiển thị số tờ khai đã xử lý và còn lại

**Khi nào dùng**:
```
✓ Phát hiện chọn nhầm
✓ Cần rời khỏi máy tính
✓ Quá trình mất quá nhiều thời gian
✓ Nhiều lỗi xảy ra
```

#### 🎯 Workflow rõ ràng từng bước
Enhanced Manual Mode có 5 trạng thái rõ ràng:

**State 1: Initial** → Chỉ nút "Quét công ty" hoạt động
**State 2: Companies Loaded** → Dropdown và date picker hoạt động
**State 3: Preview Displayed** → Bảng preview hiển thị, có thể chọn tờ khai
**State 4: Downloading** → Đang tải, hiển thị progress và nút "Dừng"
**State 5: Complete** → Hoàn tất, sẵn sàng cho thao tác tiếp theo

**Lợi ích**:
- Luôn biết đang ở bước nào
- Biết cần làm gì tiếp theo
- Không bị bối rối
- UI trực quan, dễ sử dụng

### 2. 📊 Trạng thái kết nối Database
Giờ bạn có thể thấy trạng thái kết nối đến database ngay trên màn hình chính:
- **● Connected** (xanh) - Kết nối tốt
- **● Disconnected** (đỏ) - Mất kết nối

### 2. ⚡ Chế độ tự động nhanh hơn
- Chế độ Automatic giờ chỉ quét **3 ngày** thay vì 7 ngày
- Nhanh hơn 50%, tiết kiệm tài nguyên
- Phù hợp cho sử dụng hàng ngày

### 3. 🏢 Quản lý danh sách công ty
- Tự động lưu tên công ty khi xử lý tờ khai
- Xem danh sách công ty đã xử lý
- Không cần nhập thủ công

### 4. 🎯 Lọc theo công ty (Manual Mode)
Giờ bạn có thể:
- Chọn số ngày quét (1-90 ngày)
- Chọn công ty cụ thể để lấy mã vạch
- Hoặc chọn "Tất cả công ty"

### 5. 📈 Thanh tiến trình chi tiết
- Hiển thị tiến trình xử lý real-time
- Biết đang xử lý tờ khai nào
- Thấy kết quả ngay lập tức

## 🐛 Sửa lỗi

### Lỗi kết nối Database
- ✅ Sửa lỗi "Failed to query declarations"
- ✅ Thêm kiểm tra kết nối tự động
- ✅ Thông báo lỗi rõ ràng hơn

### Lỗi Manual Mode
- ✅ Sửa lỗi không query được database
- ✅ Thêm hỗ trợ filter theo công ty

## 📖 Hướng dẫn nhanh

### Sử dụng hàng ngày (Automatic Mode)
```
1. Chọn "Automatic"
2. Nhấn "Start"
3. Xong!
```

### Sử dụng Enhanced Manual Mode

#### Workflow cơ bản
```
1. Chọn "Manual"
2. Nhấn "Quét công ty" (lần đầu tiên)
3. Chọn công ty từ dropdown
4. Chọn "Từ ngày" và "Đến ngày"
5. Nhấn "Xem trước"
6. Xem và chọn tờ khai
7. Nhấn "Lấy mã vạch"
8. Theo dõi tiến trình
```

#### Xử lý công ty cụ thể trong tuần
```
1. Chọn "Manual"
2. Chọn công ty: "CÔNG TY ABC"
3. Từ ngày: 7 ngày trước
4. Đến ngày: Hôm nay
5. Nhấn "Xem trước"
6. Nhấn "Lấy mã vạch"
```

#### Xử lý tất cả công ty trong tháng
```
1. Chọn "Manual"
2. Chọn "Tất cả công ty"
3. Từ ngày: 01/12/2024
4. Đến ngày: 31/12/2024
5. Nhấn "Xem trước"
6. Xem số lượng tờ khai
7. Nhấn "Lấy mã vạch"
```

#### Xử lý có chọn lọc
```
1. Làm theo workflow cơ bản đến bước 6
2. Bỏ chọn tờ khai không cần xử lý
3. Hoặc chọn chỉ một vài tờ khai cụ thể
4. Nhấn "Lấy mã vạch"
5. Chỉ tờ khai đã chọn được xử lý
```

#### Dừng download đang chạy
```
1. Đang tải mã vạch
2. Nhấn nút "Dừng"
3. Chờ tờ khai hiện tại hoàn tất
4. Xem tóm tắt kết quả
5. Tiến trình đã lưu
```

## 📚 Tài liệu

- **QUICK_START.md** - Bắt đầu nhanh
- **FEATURES_GUIDE.md** - Hướng dẫn chi tiết
- **CHANGELOG.md** - Danh sách thay đổi đầy đủ

## 🔧 Cài đặt

### Nếu đã có version cũ
```bash
# Cập nhật code
git pull

# Cài đặt dependencies mới (nếu có)
pip install -r requirements.txt

# Chạy
python main.py
```

### Cài đặt mới
```bash
# Cài đặt
.\install.ps1

# Cấu hình
copy config.ini.sample config.ini
notepad config.ini

# Test kết nối
python test_db_connection.py

# Chạy
python main.py
```

## ⚠️ Lưu ý

1. **Backup dữ liệu**: Backup file `data/tracking.db` trước khi cập nhật
2. **Test kết nối**: Chạy `python test_db_connection.py` trước
3. **Automatic mode**: Giờ chỉ quét 3 ngày (nếu cần nhiều hơn, dùng Manual)

## 🎯 Use Cases mới với Enhanced Manual Mode

### Use Case 1: Xử lý công ty mới
```
Scenario: Công ty mới có tờ khai, cần lấy mã vạch
Solution:
1. Nhấn "Quét công ty" để cập nhật danh sách
2. Chọn công ty mới từ dropdown
3. Chọn khoảng thời gian phù hợp
4. Xem trước và xử lý
```

### Use Case 2: Xử lý lại tờ khai có lỗi
```
Scenario: Một số tờ khai bị lỗi, cần xử lý lại
Solution:
1. Chọn công ty và khoảng thời gian
2. Nhấn "Xem trước"
3. Bỏ chọn tờ khai đã xử lý thành công
4. Chỉ chọn tờ khai bị lỗi
5. Nhấn "Lấy mã vạch"
```

### Use Case 3: Kiểm tra trước khi xử lý hàng loạt
```
Scenario: Cần xử lý nhiều tờ khai, muốn kiểm tra trước
Solution:
1. Chọn "Tất cả công ty"
2. Chọn khoảng thời gian dài (30-90 ngày)
3. Nhấn "Xem trước"
4. Xem số lượng: "Đã chọn: 150/150 tờ khai"
5. Quyết định xử lý tất cả hoặc chọn lọc
```

### Use Case 4: Xử lý từng phần cho batch lớn
```
Scenario: Có 200 tờ khai, muốn xử lý từng phần
Solution:
1. Xem trước tất cả 200 tờ khai
2. Chọn 50 tờ khai đầu tiên
3. Nhấn "Lấy mã vạch"
4. Sau khi xong, xem trước lại
5. Chọn 50 tờ khai tiếp theo
6. Lặp lại cho đến hết
```

### Use Case 5: Dừng khi phát hiện vấn đề
```
Scenario: Đang xử lý, phát hiện nhiều lỗi
Solution:
1. Nhấn nút "Dừng"
2. Xem log để tìm nguyên nhân
3. Sửa vấn đề (kết nối, cấu hình, etc.)
4. Xem trước lại và chọn tờ khai còn lại
5. Tiếp tục xử lý
```

### Use Case 6: Xử lý theo ngày cụ thể
```
Scenario: Chỉ cần xử lý tờ khai ngày 15/12/2024
Solution:
1. Từ ngày: 15/12/2024
2. Đến ngày: 15/12/2024
3. Chọn "Tất cả công ty"
4. Xem trước và xử lý
```

### Use Case 7: Theo dõi tiến trình chi tiết
```
Scenario: Muốn biết chính xác đang xử lý tờ khai nào
Solution:
1. Bắt đầu download
2. Xem progress bar: "Đang xử lý 15/50..."
3. Xem log panel: "Successfully saved barcode for 302934380950"
4. Biết chính xác tiến độ và kết quả
```

## 🚀 Cải tiến hiệu suất

- Automatic mode: **Nhanh hơn 50%** (3 ngày vs 7 ngày)
- Query database: **Tối ưu hơn** với filter
- UI: **Responsive hơn** với progress bar

## 💡 Tips

### Tips chung
1. Dùng **Automatic** cho hoạt động hàng ngày
2. Dùng **Enhanced Manual Mode** khi cần kiểm soát chi tiết
3. Kiểm tra **DB Status** nếu có vấn đề
4. Xem **Recent Logs** để debug
5. Backup **tracking.db** định kỳ

### Tips cho Enhanced Manual Mode
6. **Quét công ty 1 lần/tuần**: Không cần quét mỗi ngày, dùng "Làm mới"
7. **Luôn xem trước**: Đừng bỏ qua bước preview, giúp tránh sai sót
8. **Bắt đầu với khoảng ngắn**: Test với 7-14 ngày trước khi dùng 90 ngày
9. **Chọn lọc thông minh**: Bỏ chọn tờ khai đã xử lý để tránh duplicate
10. **Dùng "Dừng" khi cần**: Đừng ngại dừng nếu thấy có vấn đề
11. **Theo dõi progress**: Xem progress bar và log để biết tiến độ
12. **Test với ít tờ khai**: Chọn 2-3 tờ khai để test trước khi xử lý hàng loạt

## ❓ Câu hỏi thường gặp

### Câu hỏi chung
**Q: Tại sao Automatic chỉ quét 3 ngày?**
A: Để tối ưu hiệu suất. Dùng Enhanced Manual Mode nếu cần nhiều hơn.

**Q: DB Status màu đỏ?**
A: Chạy `python test_db_connection.py` để kiểm tra

### Câu hỏi về Enhanced Manual Mode

**Q: Enhanced Manual Mode khác gì với Manual Mode cũ?**
A: Enhanced Manual Mode có:
- Quét và lưu danh sách công ty
- Chọn khoảng thời gian chính xác (từ ngày - đến ngày)
- Xem trước tờ khai trước khi xử lý
- Chọn lọc từng tờ khai cụ thể
- Dừng download đang chạy

**Q: Phải quét công ty mỗi lần sử dụng không?**
A: Không! Chỉ cần quét 1 lần, danh sách được lưu lại. Lần sau chỉ cần nhấn "Làm mới".

**Q: Làm sao biết có bao nhiêu tờ khai sẽ được xử lý?**
A: Nhấn "Xem trước", hệ thống sẽ hiển thị: "Đã chọn: X/Y tờ khai"

**Q: Có thể bỏ qua một số tờ khai không?**
A: Có! Sau khi xem trước, bỏ chọn checkbox của tờ khai không muốn xử lý.

**Q: Nút "Lấy mã vạch" bị disable?**
A: Phải chọn ít nhất 1 tờ khai trong preview. Kiểm tra "Đã chọn: X/Y" - X phải > 0.

**Q: Làm sao dừng download đang chạy?**
A: Nhấn nút "Dừng". Hệ thống sẽ hoàn thành tờ khai hiện tại rồi dừng lại.

**Q: Dừng download có mất dữ liệu không?**
A: Không! Tất cả tờ khai đã xử lý được lưu lại. Chỉ tờ khai chưa xử lý bị bỏ qua.

**Q: Preview mất quá nhiều thời gian?**
A: Nhấn nút "Hủy" để dừng query. Thử giảm khoảng thời gian hoặc chọn công ty cụ thể.

**Q: Khoảng thời gian tối đa là bao nhiêu?**
A: Không giới hạn, nhưng hệ thống cảnh báo nếu > 90 ngày vì có thể mất nhiều thời gian.

**Q: Có thể xử lý nhiều công ty cùng lúc không?**
A: Có! Chọn "Tất cả công ty" trong dropdown.

**Q: Danh sách công ty có tự động cập nhật không?**
A: Không tự động. Nhấn "Quét công ty" để cập nhật khi có công ty mới.

**Q: Làm sao biết đang xử lý tờ khai nào?**
A: Xem progress bar ("Đang xử lý 15/50...") và log panel (hiển thị số tờ khai).

## 📞 Hỗ trợ

Nếu cần giúp đỡ:
1. Đọc **QUICK_START.md**
2. Đọc **FEATURES_GUIDE.md**
3. Chạy **test_db_connection.py**
4. Xem **logs/app.log**
5. Liên hệ IT support

---

**Enjoy the new features! 🎉**
