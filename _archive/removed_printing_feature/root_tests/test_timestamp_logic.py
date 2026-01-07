
import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import sys
import os
import pyodbc
from pathlib import Path
sys.path.append(os.getcwd())

from declaration_printing.simple_template_generator import SimpleTemplateGenerator
from declaration_printing.models import DeclarationData

def verify_timestamp():
    generator = SimpleTemplateGenerator()
    
    # Test with declaration that has GIO_DK (107767905230)
    # This was the one used in previous step
    decl_number = "107767905230"
    
    print(f"Verifying timestamp for declaration: {decl_number}")
    
    # Get all DB values
    db_values = generator._get_all_db_values(decl_number)
    
    if "NGAY_DK_full" in db_values:
        print(f"SUCCESS: Found NGAY_DK_full: {db_values['NGAY_DK_full']}")
        print(f"NGAY_DK raw: {db_values.get('NGAY_DK')}")
        print(f"GIO_DK raw: {db_values.get('GIO_DK')}")
    else:
        print("FAILURE: NGAY_DK_full not found in db_values")
        print("Keys found:", list(db_values.keys()))

if __name__ == "__main__":
    verify_timestamp()
