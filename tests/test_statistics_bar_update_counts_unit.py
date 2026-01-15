import tkinter as tk
from datetime import datetime

import pytest

from gui.statistics_bar import StatisticsBar


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_statistics_bar_update_counts_updates_values(root):
    bar = StatisticsBar(root)

    before = datetime.now()
    bar.update_counts(processed=5, retrieved=3, errors=2)
    after = datetime.now()

    assert bar.processed_var.get() == "5"
    assert bar.retrieved_var.get() == "3"
    assert bar.errors_var.get() == "2"
    assert bar._last_run is not None
    assert before <= bar._last_run <= after
