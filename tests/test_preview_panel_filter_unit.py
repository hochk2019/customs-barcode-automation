import tkinter as tk
import pytest

from gui.preview_panel import PreviewPanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def _get_visible_numbers(panel: PreviewPanel):
    numbers = []
    for item_id in panel.preview_tree.get_children():
        values = panel.preview_tree.item(item_id, "values")
        if len(values) > 1:
            numbers.append(str(values[1]))
    return numbers


def test_preview_panel_filter_import_export(root):
    panel = PreviewPanel(root)

    declarations = [
        {"declaration_number": "100001", "tax_code": "010", "date": "01/01/2024", "status": "", "result": ""},
        {"declaration_number": "100002", "tax_code": "010", "date": "01/01/2024", "status": "", "result": ""},
        {"declaration_number": "300001", "tax_code": "010", "date": "01/01/2024", "status": "", "result": ""},
        {"declaration_number": "400001", "tax_code": "010", "date": "01/01/2024", "status": "", "result": ""},
    ]

    # Preselect import filter before preview, like real usage.
    panel.filter_combo.current(1)
    panel.filter_combo.event_generate("<<ComboboxSelected>>")
    root.update_idletasks()

    panel.populate_preview(declarations)

    # Import-only filter (starts with 10)
    panel.filter_combo.current(1)
    panel.filter_combo.event_generate("<<ComboboxSelected>>")
    root.update_idletasks()
    numbers = _get_visible_numbers(panel)
    assert numbers == ["100001", "100002"]

    # Export-only filter (starts with 30)
    panel.filter_combo.current(2)
    panel.filter_combo.event_generate("<<ComboboxSelected>>")
    root.update_idletasks()
    numbers = _get_visible_numbers(panel)
    assert numbers == ["300001"]

    # All declarations
    panel.filter_combo.current(0)
    panel.filter_combo.event_generate("<<ComboboxSelected>>")
    root.update_idletasks()
    numbers = _get_visible_numbers(panel)
    assert numbers == ["100001", "100002", "300001", "400001"]
