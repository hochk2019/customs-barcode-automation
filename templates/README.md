# Templates Directory

This directory contains Excel templates and mapping configurations for the customs declaration printing feature.

## Contents

### Template Files
- `ToKhaiHQ7X_QDTQ.xlsx` - Export clearance declaration template
- `ToKhaiHQ7N_QDTQ.xlsx` - Import clearance declaration template

### Mapping Files
- `ToKhaiHQ7X_QDTQ_mapping.json` - Field mapping for export declarations
- `ToKhaiHQ7N_QDTQ_mapping.json` - Field mapping for import declarations

## Template Structure

Each template consists of:
1. **Excel file** (.xlsx or .xls) - Contains the layout and formatting
2. **Mapping file** (.json) - Defines where data fields are placed in the Excel file

## Installation

### Automatic Setup
```bash
# Install templates from sample directory
python scripts/setup_templates.py

# Validate installation
python scripts/validate_templates.py
```

### Manual Installation
1. Copy Excel template files to this directory
2. Create corresponding mapping JSON files
3. Run validation: `python scripts/validate_templates.py`

## Validation

Use the validation script to check template integrity:
```bash
# Basic validation
python scripts/validate_templates.py

# Detailed validation with verbose output
python scripts/validate_templates.py --verbose

# Automatic fixes
python scripts/validate_templates.py --fix
```

## Customization

See `docs/TEMPLATE_CUSTOMIZATION_GUIDE.md` for detailed instructions on:
- Modifying existing templates
- Creating new templates
- Updating field mappings
- Troubleshooting issues

## File Naming Convention

Templates must follow this naming pattern:
- `ToKhaiHQ[7X/7N]_[QDTQ/PL].xlsx` - Excel template
- `ToKhaiHQ[7X/7N]_[QDTQ/PL]_mapping.json` - Mapping configuration

Where:
- `7X` = Export declarations
- `7N` = Import declarations  
- `QDTQ` = Clearance declarations
- `PL` = Routing declarations

## Mapping File Format

Mapping files use JSON format to define field positions:
```json
{
  "declaration_number": "B5",
  "company_name": "B10",
  "total_value": "F20"
}
```

Each key is a data field name, and each value is an Excel cell reference.

## Supported Data Fields

| Field | Description | Type |
|-------|-------------|------|
| `declaration_number` | Declaration number | Text |
| `declaration_date` | Declaration date | Date |
| `company_name` | Company name | Text |
| `company_tax_code` | Tax code | Text |
| `company_address` | Company address | Text |
| `partner_name` | Partner name | Text |
| `partner_address` | Partner address | Text |
| `country_of_origin` | Country of origin | Text |
| `country_of_destination` | Country of destination | Text |
| `total_value` | Total value | Number |
| `currency` | Currency code | Text |
| `exchange_rate` | Exchange rate | Number |
| `total_weight` | Total weight | Number |
| `total_packages` | Total packages | Number |
| `transport_method` | Transport method | Text |
| `bill_of_lading` | Bill of lading | Text |
| `customs_office` | Customs office | Text |

## Troubleshooting

### Common Issues

1. **Template not found**
   - Check file name matches expected pattern
   - Ensure file is in templates directory

2. **Invalid mapping file**
   - Validate JSON syntax
   - Check cell references are valid Excel format

3. **Template validation fails**
   - Ensure Excel file is not corrupted
   - Check file is not password protected

### Getting Help

1. Run validation with verbose output: `python scripts/validate_templates.py --verbose`
2. Check application logs in `logs/` directory
3. Refer to customization guide: `docs/TEMPLATE_CUSTOMIZATION_GUIDE.md`

## Backup

Always backup templates before making changes:
```bash
# Backup entire templates directory
xcopy templates templates_backup /E /I

# Backup specific template
copy ToKhaiHQ7N_QDTQ.xlsx ToKhaiHQ7N_QDTQ_backup.xlsx
```

## Requirements

- Excel files must be in .xlsx or .xls format
- Mapping files must be valid JSON
- Cell references must use Excel format (e.g., "B5", "C10")
- Files must be readable by the application user account