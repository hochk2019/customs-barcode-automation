# Requirements Document

## Introduction

This feature adds customs declaration printing capability to the Customs Barcode Automation application. Users can generate formatted Excel customs declarations directly from the application instead of manually printing each declaration from ECUS system.

## Glossary

- **TKTQ**: Tờ Khai Thông Quan (Customs Clearance Declaration)
- **ECUS**: Electronic Customs System - Vietnam's customs management system
- **Template**: Excel file format used by ECUS for printing declarations
- **Declaration_Number**: 12-digit customs declaration number
- **Export_Declaration**: Declaration starting with "30..." (e.g., 305254403660)
- **Import_Declaration**: Declaration starting with "10..." (e.g., 107772836360)
- **Clearance_Template**: Excel template for cleared declarations (QDTQ)
- **Routing_Template**: Excel template for routing declarations (PL)
- **XML_Data**: Raw declaration data exported from ECUS database

## Requirements

### Requirement 1

**User Story:** As a customs officer, I want to print customs clearance declarations directly from the application, so that I can generate formatted documents without accessing ECUS for each declaration.

#### Acceptance Criteria

1. WHEN a user selects a cleared declaration and clicks "In TKTQ" button THEN the system SHALL generate an Excel file using the appropriate template
2. WHEN the system processes an export declaration (30...) THEN the system SHALL use the ToKhaiHQ7X_QDTQ template
3. WHEN the system processes an import declaration (10...) THEN the system SHALL use the ToKhaiHQ7N_QDTQ template
4. WHEN the Excel file is generated THEN the system SHALL populate all available data fields from the declaration data
5. WHEN the file generation is complete THEN the system SHALL save the file with a standardized naming convention

### Requirement 2

**User Story:** As a system administrator, I want the application to automatically detect declaration types, so that the correct template is used for each declaration.

#### Acceptance Criteria

1. WHEN the system receives a declaration number starting with "30" THEN the system SHALL classify it as an export declaration
2. WHEN the system receives a declaration number starting with "10" THEN the system SHALL classify it as an import declaration
3. WHEN the system cannot determine the declaration type THEN the system SHALL display an error message and halt processing
4. WHEN multiple declarations are selected THEN the system SHALL process each declaration with its appropriate template
5. WHEN the system encounters an unsupported declaration format THEN the system SHALL log the error and continue with remaining declarations

### Requirement 3

**User Story:** As a data processor, I want the system to extract declaration data from multiple sources, so that complete information is available for template population.

#### Acceptance Criteria

1. WHEN processing a declaration THEN the system SHALL attempt to retrieve data from the ECUS database first
2. WHEN database data is unavailable THEN the system SHALL attempt to parse XML files if available
3. WHEN both sources are unavailable THEN the system SHALL create a template with available basic information only
4. WHEN data extraction is successful THEN the system SHALL validate all required fields are present
5. WHEN critical data is missing THEN the system SHALL prompt the user for manual input or skip the declaration

### Requirement 4

**User Story:** As a template designer, I want the system to support Excel template customization, so that declaration formats can be updated without code changes.

#### Acceptance Criteria

1. WHEN templates are stored in the templates directory THEN the system SHALL load them dynamically at runtime
2. WHEN a template file is missing THEN the system SHALL display an error message and provide guidance for template installation
3. WHEN template fields are modified THEN the system SHALL attempt to map data to new field locations
4. WHEN field mapping fails THEN the system SHALL log unmapped fields and continue with available mappings
5. WHEN templates are updated THEN the system SHALL validate template integrity before use

### Requirement 5

**User Story:** As a file manager, I want generated declaration files to follow a consistent naming and storage pattern, so that documents are easily organized and retrieved.

#### Acceptance Criteria

1. WHEN an Excel file is generated THEN the system SHALL name it using the pattern "ToKhaiHQ7[X/N]_QDTQ_[DeclarationNumber].xlsx"
2. WHEN saving files THEN the system SHALL use the configured output directory from application settings
3. WHEN a file with the same name exists THEN the system SHALL prompt the user to overwrite or create a new version
4. WHEN the output directory is inaccessible THEN the system SHALL prompt the user to select an alternative location
5. WHEN file saving fails THEN the system SHALL display an error message and allow retry with different settings

### Requirement 6

**User Story:** As a quality controller, I want the system to validate generated declarations, so that output files contain accurate and complete information.

#### Acceptance Criteria

1. WHEN populating template fields THEN the system SHALL validate data types match expected formats
2. WHEN numeric fields are populated THEN the system SHALL format numbers according to Vietnamese customs standards
3. WHEN date fields are populated THEN the system SHALL use the format DD/MM/YYYY consistently
4. WHEN text fields exceed maximum length THEN the system SHALL truncate text and log a warning
5. WHEN required fields cannot be populated THEN the system SHALL mark them clearly for manual completion

### Requirement 7

**User Story:** As a batch processor, I want to generate multiple declarations simultaneously, so that I can efficiently process large numbers of cleared declarations.

#### Acceptance Criteria

1. WHEN multiple declarations are selected THEN the system SHALL process them in sequence with progress indication
2. WHEN batch processing encounters an error THEN the system SHALL log the error and continue with remaining declarations
3. WHEN batch processing completes THEN the system SHALL display a summary of successful and failed generations
4. WHEN the user cancels batch processing THEN the system SHALL stop after completing the current declaration
5. WHEN batch processing is interrupted THEN the system SHALL provide options to resume or restart the process

### Requirement 8

**User Story:** As a system integrator, I want the printing feature to integrate seamlessly with existing application workflows, so that users have a consistent experience.

#### Acceptance Criteria

1. WHEN the "In TKTQ" button is added to the preview panel THEN it SHALL appear next to the existing "Lấy mã vạch" button in the action button row
2. WHEN a declaration is not cleared THEN the "In TKTQ" button SHALL be disabled with appropriate tooltip
3. WHEN the feature is accessed THEN it SHALL use the same error handling and logging systems as other features
4. WHEN processing completes THEN the system SHALL update the declaration status if applicable
5. WHEN the feature is used THEN it SHALL respect all existing user permissions and access controls