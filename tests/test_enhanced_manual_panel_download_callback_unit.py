import threading
import tkinter as tk
from unittest.mock import MagicMock

import pytest

from gui.enhanced_manual_panel import EnhancedManualPanel
from models.declaration_models import Declaration


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


class _ImmediateThread:
    def __init__(self, target=None, daemon=None):
        self._target = target
        self.daemon = daemon

    def start(self):
        if self._target:
            self._target()


def test_perform_download_calls_on_download_complete(root, monkeypatch):
    barcode_retriever = MagicMock()
    file_manager = MagicMock()
    file_manager.pdf_naming_service = MagicMock(naming_format="tax_code")
    tracking_db = MagicMock()

    callback = MagicMock()

    panel = EnhancedManualPanel(
        root,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        barcode_retriever=barcode_retriever,
        file_manager=file_manager,
        tracking_db=tracking_db,
        on_download_complete=callback
    )

    # Avoid filesystem/config side effects and UI popups in test.
    panel._update_pdf_naming_service = MagicMock()
    panel._show_download_result_popup = MagicMock()
    panel._set_state = MagicMock()

    panel.after = lambda delay, func=None: func() if func else None

    decl1 = Declaration(
        declaration_number="100001",
        tax_code="010",
        declaration_date="20240101",
        customs_office_code="01",
        transport_method="1",
        channel="Xanh",
        status="T",
        goods_description=None,
    )
    decl2 = Declaration(
        declaration_number="300001",
        tax_code="010",
        declaration_date="20240101",
        customs_office_code="01",
        transport_method="1",
        channel="Xanh",
        status="T",
        goods_description=None,
    )

    results = [
        ("success", decl1, "path1.pdf", None),
        ("error", decl2, None, "Failed"),
    ]

    def fake_process(*args, **kwargs):
        return results.pop(0)

    panel._process_single_download = MagicMock(side_effect=fake_process)

    import concurrent.futures

    class _FakeFuture:
        def __init__(self, result):
            self._result = result

        def result(self):
            return self._result

    class _FakeExecutor:
        def __init__(self, max_workers=None):
            self._futures = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def submit(self, fn, *args, **kwargs):
            result = fn(*args, **kwargs)
            future = _FakeFuture(result)
            self._futures.append(future)
            return future

    monkeypatch.setattr(concurrent.futures, "ThreadPoolExecutor", _FakeExecutor)
    monkeypatch.setattr(concurrent.futures, "as_completed", lambda futures: futures)
    monkeypatch.setattr(threading, "Thread", _ImmediateThread)

    panel.perform_download([decl1, decl2])

    callback.assert_called_once_with(1, 1)
