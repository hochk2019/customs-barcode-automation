import importlib.util
from pathlib import Path


PRINTING_FEATURE_ENABLED = False


def _has_declaration_printing() -> bool:
    return importlib.util.find_spec("declaration_printing") is not None


def _should_skip_printing_tests(path_str: str) -> bool:
    lowered = path_str.lower()
    if any(token in lowered for token in ("printing", "print_integration", "preview_panel_integration")):
        return True

    try:
        content = Path(path_str).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    return any(
        token in content
        for token in (
            "declaration_printing",
            "print_declarations",
            "print_btn",
            "In TKTQ",
            "preview_panel_integration",
        )
    )


def pytest_ignore_collect(collection_path, config):
    path_str = str(collection_path)
    if not path_str.endswith(".py"):
        return False

    if not PRINTING_FEATURE_ENABLED and _should_skip_printing_tests(path_str):
        return True

    if _has_declaration_printing():
        return False

    try:
        content = Path(path_str).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    return "declaration_printing" in content
