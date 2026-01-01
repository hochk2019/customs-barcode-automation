# Security Implementation Guide

## Overview

This document describes the comprehensive security features implemented in the Customs Declaration Printing system to protect against various security threats and ensure data integrity.

## Security Features Implemented

### 1. XML Security and XXE Prevention

**Location**: `declaration_printing/security_validator.py` - `DataSanitizer` class

**Features**:
- **XXE Attack Prevention**: Detects and blocks XML External Entity (XXE) attacks
- **DOCTYPE Removal**: Automatically removes potentially malicious DOCTYPE declarations
- **XML Structure Validation**: Validates XML structure against expected ECUS formats
- **Content Sanitization**: Removes comments and processing instructions that could contain malicious content

**Implementation**:
```python
# Example usage
sanitizer = DataSanitizer(logger)
safe_xml = sanitizer.sanitize_xml_content(raw_xml)
is_valid = sanitizer.validate_xml_structure(safe_xml)
```

**Security Patterns Detected**:
- `<!ENTITY ... SYSTEM ...>` - External entity declarations
- `<!ENTITY ... PUBLIC ...>` - Public entity declarations  
- `&entity;` - Entity references
- `<!DOCTYPE ... [...]>` - DOCTYPE with internal subset

### 2. SQL Injection Prevention

**Location**: `declaration_printing/security_validator.py` - `SecureQueryBuilder` class
**Location**: `database/ecus_connector.py` - Enhanced with parameter validation

**Features**:
- **Parameterized Queries**: All database queries use parameterized statements
- **Input Validation**: SQL parameters are validated and sanitized
- **Injection Pattern Detection**: Detects common SQL injection patterns
- **Parameter Length Limits**: Prevents buffer overflow attacks

**Implementation**:
```python
# Secure query building
query_builder = SecureQueryBuilder(logger)
query, params = query_builder.build_declaration_query(declaration_number)
cursor.execute(query, params)  # Safe parameterized execution
```

**SQL Injection Patterns Detected**:
- SQL keywords: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.
- Comment patterns: `--`, `#`, `/*`, `*/`
- System procedures: `xp_cmdshell`, `sp_executesql`
- Boolean conditions: `OR 1=1`, `AND 1=1`

### 3. File Security and Path Validation

**Location**: `declaration_printing/security_validator.py` - `FilePermissionValidator` class

**Features**:
- **Directory Traversal Prevention**: Blocks `../` and similar path traversal attempts
- **File Permission Validation**: Checks and validates file/directory permissions
- **Secure File Writing**: Atomic file operations with backup creation
- **Template File Validation**: Validates Excel template files for security
- **File Size Limits**: Prevents processing of excessively large files

**Implementation**:
```python
# Secure file operations
file_validator = FilePermissionValidator(logger)
validated_path = file_validator.validate_file_path(user_input_path)
success = file_validator.secure_file_write(file_path, content, backup_existing=True)
```

**Security Checks**:
- Path traversal patterns: `../`, `..\\`, absolute paths
- File permissions: Read/write/execute permissions
- File size limits: Maximum 50MB for template files
- File extensions: Only `.xlsx` and `.xls` for templates

### 4. Sensitive Data Protection in Logging

**Location**: `logging_system/logger.py` - `SensitiveDataFilter` class
**Location**: `declaration_printing/security_validator.py` - `DataSanitizer.sanitize_for_logging()`

**Features**:
- **Automatic Data Redaction**: Automatically redacts sensitive data in log messages
- **Pattern-Based Filtering**: Uses regex patterns to identify sensitive information
- **Configurable Patterns**: Easy to add new sensitive data patterns
- **Audit Trail Protection**: Ensures audit logs don't contain sensitive data

**Implementation**:
```python
# Automatic filtering in logger
logger = Logger(config)  # Automatically includes sensitive data filter

# Manual sanitization
sanitized_message = sanitizer.sanitize_for_logging(raw_message)
```

**Sensitive Data Patterns**:
- Declaration numbers: 12-digit numbers → `[DECLARATION_NUMBER]`
- Tax codes: 10-11 digit numbers → `[TAX_CODE]`
- Document numbers: Alphanumeric patterns → `[DOCUMENT_NUMBER]`
- Passwords: `password=...` → `password=[REDACTED]`
- Tokens: `token=...` → `token=[REDACTED]`

### 5. Security Audit Logging

**Location**: `declaration_printing/security_validator.py` - `SecurityAuditLogger` class

**Features**:
- **Comprehensive Audit Trail**: Logs all security-relevant events
- **Event Categorization**: Categorizes security events by type
- **Sanitized Logging**: All audit logs are sanitized to protect sensitive data
- **Structured Logging**: Uses structured format for easy analysis

**Implementation**:
```python
# Security event logging
audit_logger = SecurityAuditLogger(base_logger)
audit_logger.log_security_event('FILE_ACCESS', user_context, details)
audit_logger.log_database_access('SELECT', 'DTOKHAIMD', param_count, success)
```

**Event Types Logged**:
- File access operations (read, write, delete)
- Database access operations (query type, table, parameters)
- XML processing operations (validation, sanitization)
- Security violations (XXE attempts, SQL injection, path traversal)

## Integration Points

### 1. Data Extraction Security

**File**: `declaration_printing/data_extractor.py`

**Security Enhancements**:
- XML files are sanitized before parsing
- Database queries use parameterized statements
- File paths are validated before access
- All operations are logged for audit

### 2. Database Connection Security

**File**: `database/ecus_connector.py`

**Security Enhancements**:
- All SQL parameters are validated and sanitized
- Sensitive data is redacted from log messages
- SQL injection patterns are detected and blocked
- Connection errors are logged securely

### 3. File Management Security

**File**: `declaration_printing/file_manager.py`

**Security Enhancements**:
- File operations use secure validation
- Directory permissions are checked
- File conflicts are resolved securely
- All file operations are audited

## Security Configuration

### Environment Variables

```bash
# Optional: Enable additional security logging
SECURITY_AUDIT_LEVEL=verbose

# Optional: Custom sensitive data patterns
CUSTOM_SENSITIVE_PATTERNS="pattern1,pattern2"
```

### Configuration Options

```python
# In application configuration
security_config = {
    'enable_xxe_protection': True,
    'enable_sql_injection_protection': True,
    'enable_path_traversal_protection': True,
    'enable_sensitive_data_filtering': True,
    'max_template_file_size': 50 * 1024 * 1024,  # 50MB
    'audit_log_level': 'INFO'
}
```

## Security Testing

### Test Coverage

The security implementation includes comprehensive tests:

- **XML Security Tests**: XXE prevention, DOCTYPE removal, structure validation
- **SQL Injection Tests**: Parameter validation, injection pattern detection
- **File Security Tests**: Path traversal prevention, permission validation
- **Logging Security Tests**: Sensitive data redaction, audit logging
- **Integration Tests**: End-to-end security workflow validation

### Running Security Tests

```bash
# Run all security tests
python -m pytest tests/test_security_validation.py -v

# Run specific security test categories
python -m pytest tests/test_security_validation.py::TestDataSanitizer -v
python -m pytest tests/test_security_validation.py::TestFilePermissionValidator -v
python -m pytest tests/test_security_validation.py::TestSecureQueryBuilder -v
```

## Security Best Practices

### 1. Input Validation

- **Always validate user input** before processing
- **Use parameterized queries** for all database operations
- **Sanitize file paths** before file system operations
- **Validate XML content** before parsing

### 2. Output Sanitization

- **Redact sensitive data** from log messages
- **Use structured logging** for audit trails
- **Sanitize error messages** shown to users
- **Protect debug information** in production

### 3. File Operations

- **Validate file permissions** before operations
- **Use atomic file operations** when possible
- **Create backups** before overwriting files
- **Limit file sizes** to prevent resource exhaustion

### 4. Database Security

- **Use parameterized queries** exclusively
- **Validate connection strings** and credentials
- **Log database operations** for audit
- **Handle connection errors** securely

## Monitoring and Alerting

### Security Events to Monitor

1. **XXE Attack Attempts**: Monitor for XML parsing security violations
2. **SQL Injection Attempts**: Monitor for malicious SQL parameter patterns
3. **Path Traversal Attempts**: Monitor for directory traversal patterns
4. **File Permission Violations**: Monitor for unauthorized file access attempts
5. **Unusual Database Activity**: Monitor for suspicious query patterns

### Log Analysis

Security events are logged with structured format for easy analysis:

```
SECURITY_AUDIT: EVENT_TYPE | User: context | Details: {...}
```

Example log entries:
```
SECURITY_AUDIT: XXE_ATTEMPT_DETECTED | Details: {'pattern': '<!ENTITY', 'content_length': 1024}
SECURITY_AUDIT: SQL_INJECTION_ATTEMPT | Details: {'pattern': 'DROP TABLE', 'parameter': '[REDACTED]'}
SECURITY_AUDIT: FILE_ACCESS | Details: {'file_path': '[SANITIZED]', 'operation': 'write', 'success': True}
```

## Compliance and Standards

### Security Standards Addressed

- **OWASP Top 10**: Protection against injection attacks, XXE, insecure file handling
- **CWE-89**: SQL Injection prevention
- **CWE-611**: XXE attack prevention  
- **CWE-22**: Path traversal prevention
- **CWE-532**: Information exposure through log files

### Data Protection

- **PII Protection**: Automatic redaction of personally identifiable information
- **Business Data Protection**: Protection of declaration numbers, tax codes, and business information
- **Audit Compliance**: Comprehensive audit trails for security events
- **Data Integrity**: Validation and sanitization of all input data

## Troubleshooting

### Common Security Issues

1. **XML Parsing Errors**: Check for XXE patterns in XML content
2. **Database Connection Failures**: Verify parameterized query usage
3. **File Access Denied**: Check file permissions and path validation
4. **Sensitive Data in Logs**: Verify sensitive data filter is enabled

### Debug Mode

For debugging security issues (development only):

```python
# Enable verbose security logging
security_logger = SecurityAuditLogger(logger)
security_logger.log_level = 'DEBUG'

# Disable sensitive data filtering (development only)
logger.remove_filter(SensitiveDataFilter)
```

**Warning**: Never disable security features in production environments.

## Future Enhancements

### Planned Security Improvements

1. **Rate Limiting**: Implement rate limiting for API endpoints
2. **Encryption**: Add encryption for sensitive data at rest
3. **Digital Signatures**: Implement digital signatures for generated files
4. **Advanced Threat Detection**: Machine learning-based anomaly detection
5. **Security Metrics**: Enhanced security metrics and reporting

### Security Updates

Regular security updates should include:
- Review and update sensitive data patterns
- Update XXE and SQL injection detection patterns
- Review file permission validation rules
- Update security test coverage
- Review audit log analysis procedures

## Contact and Support

For security-related questions or to report security issues:
- Review security logs for detailed error information
- Check test coverage for security validation
- Consult this documentation for implementation details
- Follow security best practices outlined above