# Design Document

## Overview

The Customs Declaration Printing feature enables users to generate formatted Excel customs declarations directly from the application. The system automatically detects declaration types, retrieves data from ECUS database or XML files, and populates appropriate Excel templates to create print-ready documents.

## Architecture

The feature follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI Layer      │    │  Business Logic  │    │  Data Layer     │
│                 │    │                  │    │                 │
│ - Print Button  │───▶│ - Declaration    │───▶│ - ECUS DB       │
│ - Progress UI   │    │   Type Detector  │    │ - XML Parser    │
│ - File Dialog   │    │ - Template       │    │ - File System   │
│                 │    │   Manager        │    │                 │
└─────────────────┘    │ - Data Mapper    │    └─────────────────┘
                       │ - Excel Generator│
                       └──────────────────┘
```

## Components and Interfaces

### 1. PreviewPanelIntegration (UI Integration)
```python
class PreviewPanelIntegration:
    def add_print_button_to_preview_panel(self) -> None
    def update_print_button_state(self, selected_declarations: List[str]) -> None
    def handle_print_button_click(self, selected_declarations: List[str]) -> None
    def show_print_progress_in_preview(self, current: int, total: int) -> None
```

**Button Layout in Preview Panel:**
```
[Lấy mã vạch] [In TKTQ] [Dừng] [Tải lại lỗi] [Xuất Excel]
```

### 2. DeclarationPrinter (Main Controller)
```python
class DeclarationPrinter:
    def print_declarations(self, declaration_numbers: List[str]) -> PrintResult
    def print_single_declaration(self, declaration_number: str) -> bool
    def validate_declaration_for_printing(self, declaration_number: str) -> bool
```

### 3. DeclarationTypeDetector
```python
class DeclarationTypeDetector:
    def detect_type(self, declaration_number: str) -> DeclarationType
    def is_export_declaration(self, declaration_number: str) -> bool
    def is_import_declaration(self, declaration_number: str) -> bool
```

### 4. TemplateManager
```python
class TemplateManager:
    def get_template_path(self, declaration_type: DeclarationType) -> str
    def validate_template(self, template_path: str) -> bool
    def load_template_mapping(self, template_path: str) -> Dict[str, str]
```

### 5. DeclarationDataExtractor
```python
class DeclarationDataExtractor:
    def extract_from_database(self, declaration_number: str) -> DeclarationData
    def extract_from_xml(self, xml_path: str) -> DeclarationData
    def merge_data_sources(self, db_data: DeclarationData, xml_data: DeclarationData) -> DeclarationData
```

### 6. ExcelGenerator
```python
class ExcelGenerator:
    def create_from_template(self, template_path: str, data: DeclarationData) -> str
    def populate_fields(self, workbook: Workbook, data: DeclarationData, mapping: Dict) -> None
    def format_output_filename(self, declaration_number: str, declaration_type: DeclarationType) -> str
```

## Data Models

### DeclarationData
```python
@dataclass
class DeclarationData:
    # Basic Information
    declaration_number: str
    declaration_type: DeclarationType
    customs_office: str
    declaration_date: datetime
    
    # Company Information
    company_tax_code: str
    company_name: str
    company_address: str
    
    # Trade Information
    partner_name: str
    partner_address: str
    country_of_origin: str
    country_of_destination: str
    
    # Financial Information
    total_value: Decimal
    currency: str
    exchange_rate: Decimal
    
    # Goods Information
    goods_list: List[GoodsItem]
    total_weight: Decimal
    total_packages: int
    
    # Transport Information
    transport_method: str
    bill_of_lading: str
    container_numbers: List[str]
    
    # Additional Fields
    additional_data: Dict[str, Any]
```

### GoodsItem
```python
@dataclass
class GoodsItem:
    item_number: int
    hs_code: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total_value: Decimal
    origin_country: str
```

### DeclarationType
```python
class DeclarationType(Enum):
    EXPORT_CLEARANCE = "export_clearance"  # ToKhaiHQ7X_QDTQ
    IMPORT_CLEARANCE = "import_clearance"  # ToKhaiHQ7N_QDTQ
    EXPORT_ROUTING = "export_routing"      # ToKhaiHQ7X_PL
    IMPORT_ROUTING = "import_routing"      # ToKhaiHQ7N_PL
```

## 
## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:

- Properties 1.2 and 1.3 (template selection for export/import) can be combined with 2.1 and 2.2 (classification logic) into comprehensive template selection properties
- Properties 2.4 and 7.1 (batch processing) can be combined into a single batch processing property
- Properties 4.1, 4.3, 4.4, and 4.5 (template management) can be consolidated into template handling properties
- Properties 6.1, 6.2, 6.3, 6.4 (data validation and formatting) can be combined into data formatting properties

### Core Properties

Property 1: Declaration type classification and template selection
*For any* valid declaration number, the system should correctly classify it as export (30...) or import (10...) and select the corresponding template (ToKhaiHQ7X_QDTQ or ToKhaiHQ7N_QDTQ)
**Validates: Requirements 1.2, 1.3, 2.1, 2.2**

Property 2: Excel file generation with data population
*For any* valid declaration data and template, generating an Excel file should populate all available data fields and create a file with the standardized naming convention
**Validates: Requirements 1.1, 1.4, 1.5, 5.1**

Property 3: Data source priority and fallback
*For any* declaration number, the system should attempt database extraction first, then XML parsing if database fails, then basic template creation if both fail
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

Property 4: Error handling and continuation
*For any* batch of declarations containing invalid items, the system should log errors for invalid items and continue processing valid ones
**Validates: Requirements 2.3, 2.5, 7.2**

Property 5: Template management and validation
*For any* template file in the templates directory, the system should load it dynamically, validate its integrity, and attempt to map data to available fields
**Validates: Requirements 4.1, 4.3, 4.4, 4.5**

Property 6: Data formatting consistency
*For any* data being populated into templates, numeric fields should follow Vietnamese customs formatting, dates should use DD/MM/YYYY format, and text should be truncated with warnings if exceeding limits
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

Property 7: Batch processing with progress tracking
*For any* set of multiple declarations, the system should process them sequentially, provide progress indication, and generate a summary of results
**Validates: Requirements 2.4, 7.1, 7.3**

Property 8: Preview Panel integration and button state management
*For any* selected declarations in the preview panel, the "In TKTQ" button should be enabled only for cleared declarations (TTTK = "T") and work alongside existing buttons without conflicts
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

## Error Handling

### Error Categories

1. **Data Errors**
   - Missing declaration data
   - Invalid declaration numbers
   - Corrupted XML files
   - Database connection failures

2. **Template Errors**
   - Missing template files
   - Corrupted Excel templates
   - Invalid field mappings
   - Template version mismatches

3. **File System Errors**
   - Insufficient disk space
   - Permission denied
   - Invalid output paths
   - File locking conflicts

4. **Processing Errors**
   - Data validation failures
   - Excel generation errors
   - Batch processing interruptions
   - Memory limitations

### Error Handling Strategy

```python
class ErrorHandler:
    def handle_data_error(self, error: DataError) -> ErrorResponse
    def handle_template_error(self, error: TemplateError) -> ErrorResponse
    def handle_file_error(self, error: FileError) -> ErrorResponse
    def handle_processing_error(self, error: ProcessingError) -> ErrorResponse
```

## Testing Strategy

### Unit Testing Approach

Unit tests will focus on individual components:
- DeclarationTypeDetector: Test classification logic with various number patterns
- TemplateManager: Test template loading and validation
- DataExtractor: Test data extraction from different sources
- ExcelGenerator: Test Excel file creation and field population

### Property-Based Testing Approach

Property-based tests will verify universal behaviors using **Hypothesis** library with minimum 100 iterations per test:

- **Property 1 Test**: Generate random declaration numbers and verify correct classification and template selection
- **Property 2 Test**: Generate random declaration data and verify Excel file creation with proper naming
- **Property 3 Test**: Test data source fallback behavior with various availability scenarios
- **Property 4 Test**: Generate batches with mixed valid/invalid declarations and verify error handling
- **Property 5 Test**: Test template loading and validation with various template conditions
- **Property 6 Test**: Generate random data and verify formatting consistency
- **Property 7 Test**: Test batch processing with random declaration sets
- **Property 8 Test**: Test UI state management with various declaration statuses

Each property-based test will be tagged with comments referencing the specific correctness property:
- Format: `# Feature: customs-declaration-printing, Property X: [property_text]`

### Integration Testing

Integration tests will verify end-to-end workflows:
- Complete declaration printing process
- Database and XML integration
- File system operations
- UI integration with existing application

### Test Data Management

Test data will include:
- Sample XML files from ECUS
- Template Excel files
- Mock database responses
- Various declaration number patterns
- Edge cases and error conditions

## Performance Considerations

### Optimization Strategies

1. **Template Caching**: Load templates once and reuse for multiple declarations
2. **Database Connection Pooling**: Reuse database connections for batch processing
3. **Asynchronous Processing**: Process multiple declarations concurrently where possible
4. **Memory Management**: Stream large XML files instead of loading entirely into memory
5. **Progress Reporting**: Update UI progress without blocking main processing thread

### Scalability Requirements

- Support batch processing of up to 1000 declarations
- Handle template files up to 50MB
- Process XML files up to 100MB
- Complete single declaration processing within 5 seconds
- Maintain responsive UI during batch operations

## Security Considerations

### Data Protection

1. **Sensitive Data Handling**: Ensure declaration data is not logged in plain text
2. **File Permissions**: Set appropriate permissions on generated Excel files
3. **Database Security**: Use parameterized queries to prevent SQL injection
4. **XML Parsing**: Validate XML structure to prevent XXE attacks

### Access Control

1. **User Permissions**: Respect existing application permission system
2. **File Access**: Validate user access to output directories
3. **Template Security**: Validate template files before processing
4. **Audit Logging**: Log all declaration printing activities for audit trails

## Deployment Considerations

### Dependencies

- **openpyxl**: For Excel file manipulation
- **lxml**: For XML parsing
- **pyodbc**: For ECUS database connectivity
- **pathlib**: For file system operations

### Configuration

```python
class PrintingConfig:
    template_directory: str = "templates"
    output_directory: str = "output"
    database_connection_string: str
    xml_backup_directory: str = "xml_backup"
    max_batch_size: int = 100
    enable_progress_reporting: bool = True
```

### Installation Requirements

1. Template files must be installed in the templates directory
2. Database connection must be configured for ECUS access
3. Output directory must have write permissions
4. Required Python packages must be installed

This design provides a robust foundation for implementing the customs declaration printing feature while maintaining integration with the existing application architecture.