"""
Tests for seal status auto-correction feature (v1.5.4).

Tests cover the _auto_correct_seal_status method in BarcodePdfGenerator
which automatically corrects the seal note ("ghi_chu") on PDF output
based on the channel (luồng) and declaration status.
"""

import pytest
from unittest.mock import patch, MagicMock
from web_utils.qrcode_api_client import ContainerDeclarationInfo
from web_utils.barcode_pdf_generator import BarcodePdfGenerator


# The original unchecked text from the customs system
UNCHECKED_SEAL = "Tờ khai chưa được kiểm tra điều kiện niêm phong"
# Expected results after auto-correction
GREEN_YELLOW_CORRECTED = "Tờ khai không phải niêm phong"
RED_CORRECTED = "Tờ khai chưa xác nhận niêm phong"


@pytest.fixture
def generator():
    """Create a BarcodePdfGenerator instance without logger."""
    return BarcodePdfGenerator(logger=None)


@pytest.fixture
def mock_prefs_enabled():
    """Mock preferences with both auto-correct options enabled."""
    mock_svc = MagicMock()
    mock_svc.auto_correct_seal_green_yellow = True
    mock_svc.auto_correct_seal_red = True
    return mock_svc


@pytest.fixture
def mock_prefs_disabled():
    """Mock preferences with both auto-correct options disabled."""
    mock_svc = MagicMock()
    mock_svc.auto_correct_seal_green_yellow = False
    mock_svc.auto_correct_seal_red = False
    return mock_svc


class TestSealStatusAutoCorrection:
    """Tests for _auto_correct_seal_status method."""

    # ===== Green channel + Cleared =====

    def test_green_cleared_corrects_seal(self, generator, mock_prefs_enabled):
        """Luồng Xanh + Thông quan → 'Tờ khai không phải niêm phong'"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == GREEN_YELLOW_CORRECTED

    # ===== Yellow channel + Cleared =====

    def test_yellow_cleared_corrects_seal(self, generator, mock_prefs_enabled):
        """Luồng Vàng + Thông quan → 'Tờ khai không phải niêm phong'"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Vàng",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == GREEN_YELLOW_CORRECTED

    # ===== Red channel + Transfer =====

    def test_red_transfer_corrects_seal(self, generator, mock_prefs_enabled):
        """Luồng Đỏ + Chuyển địa điểm kiểm tra → 'Tờ khai chưa xác nhận niêm phong'"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Đỏ",
            trang_thai_to_khai="Chuyển địa điểm kiểm tra",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == RED_CORRECTED

    # ===== Already correct - no change =====

    def test_already_correct_no_change(self, generator, mock_prefs_enabled):
        """Ghi chú đã đúng → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        # Already shows the correct text
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(GREEN_YELLOW_CORRECTED, info)
        assert result == GREEN_YELLOW_CORRECTED

    def test_different_note_no_change(self, generator, mock_prefs_enabled):
        """Ghi chú khác → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        original = "Tờ khai chưa xác nhận niêm phong"
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(original, info)
        assert result == original

    # ===== Settings disabled - no change =====

    def test_green_yellow_disabled_no_change(self, generator, mock_prefs_disabled):
        """Tính năng Xanh/Vàng tắt → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_disabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == UNCHECKED_SEAL

    def test_red_disabled_no_change(self, generator, mock_prefs_disabled):
        """Tính năng Đỏ tắt → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Đỏ",
            trang_thai_to_khai="Chuyển địa điểm kiểm tra",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_disabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == UNCHECKED_SEAL

    # ===== Edge cases: status not matching =====

    def test_green_not_cleared_no_change(self, generator, mock_prefs_enabled):
        """Luồng Xanh nhưng chưa thông quan → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="Đã phân luồng",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == UNCHECKED_SEAL

    def test_red_not_transfer_no_change(self, generator, mock_prefs_enabled):
        """Luồng Đỏ nhưng trạng thái khác → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Đỏ",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == UNCHECKED_SEAL

    # ===== Edge cases: empty/None fields =====

    def test_empty_channel_no_change(self, generator, mock_prefs_enabled):
        """Luồng rỗng → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == UNCHECKED_SEAL

    def test_empty_status_no_change(self, generator, mock_prefs_enabled):
        """Trạng thái rỗng → không thay đổi"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == UNCHECKED_SEAL

    # ===== Case-insensitive and variant handling =====

    def test_vang_without_diacritics(self, generator, mock_prefs_enabled):
        """Luồng 'Vang' (không dấu) + Thông quan → vẫn sửa"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Vang",
            trang_thai_to_khai="Thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == GREEN_YELLOW_CORRECTED

    def test_chap_nhan_thong_quan(self, generator, mock_prefs_enabled):
        """Trạng thái 'Chấp nhận thông quan' → vẫn sửa (chứa 'thông quan')"""
        info = ContainerDeclarationInfo(
            luong_to_khai="Xanh",
            trang_thai_to_khai="Chấp nhận thông quan",
            so_to_khai="123456789012"
        )
        with patch("config.preferences_service.get_preferences_service", return_value=mock_prefs_enabled):
            result = generator._auto_correct_seal_status(UNCHECKED_SEAL, info)
        assert result == GREEN_YELLOW_CORRECTED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
