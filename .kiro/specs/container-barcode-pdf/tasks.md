# Implementation Plan - Container Barcode PDF

## 1. Update Data Models

- [x] 1.1 Update ContainerInfo dataclass in qrcode_api_client.py
  - Add `stt: int` field
  - Add `so_seal_hq: str` field  
  - Add `barcode_image: str` field (base64 encoded PNG)
  - Add `ghi_chu: str` field
  - _Requirements: 7.2_

- [x] 1.2 Add is_container_declaration property to ContainerDeclarationInfo
  - Return True if ma_ptvc == "2"
  - _Requirements: 1.1, 1.2_

- [x] 1.3 Write property test for container declaration detection
  - **Property 1: Container Declaration Detection**
  - **Validates: Requirements 1.1, 1.2**

## 2. Update API Response Parsing

- [x] 2.1 Update _parse_bang_ke method in qrcode_api_client.py
  - Parse Table_BangKe elements from BangKe/diffgram/DocumentElement
  - Extract Stt, SoContainer, SoSeal, SoSealHQ, BarcodeImage, GhiChu fields
  - Trim whitespace from SoContainer and SoSeal
  - Handle "#####" value for SoSealHQ
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2.2 Write property test for BangKe parsing
  - **Property 6: BangKe Parsing Completeness**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

- [x] 2.3 Write property test for whitespace trimming
  - **Property 7: Whitespace Trimming**
  - **Validates: Requirements 7.5**

## 3. Checkpoint - Verify Data Model Changes

- [x] 3. Ensure all tests pass, ask the user if questions arise.

## 4. Implement Container PDF Layout

- [x] 4.1 Add _decode_qr_image method to BarcodePdfGenerator
  - Decode base64 string to bytes
  - Create BytesIO buffer
  - Return ReportLab Image object with ~2cm x 2cm size
  - Handle invalid base64 data gracefully
  - _Requirements: 6.1, 6.3, 6.4_

- [x] 4.2 Write property test for base64 image decoding
  - **Property 5: Base64 Image Decoding Round-Trip**
  - **Validates: Requirements 6.1**

- [x] 4.3 Add _build_container_table method to BarcodePdfGenerator
  - Create 6-column table with headers
  - Add one row per container with STT, SoContainer, SoSeal, SoSealHQ, empty, QR image
  - Handle "#####" SoSealHQ as empty cell
  - Set appropriate column widths
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 4.4 Write property test for container row count
  - **Property 3: Container Row Count**
  - **Validates: Requirements 5.2**

- [x] 4.5 Write property test for seal value display
  - **Property 4: Seal Value Display**
  - **Validates: Requirements 5.4, 5.5**

## 5. Implement Container PDF Content Builder

- [x] 5.1 Add _build_container_content method to BarcodePdfGenerator
  - Build header section (no barcode, show "- 2" indicator)
  - Build title section with "DANH SÁCH CONTAINER"
  - Build items 1-9 section (same as regular PDF)
  - Build container table using _build_container_table
  - Build notes section with column explanations
  - Build export timestamp
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 8.1, 8.2, 8.3_

- [x] 5.2 Update generate_pdf method to route to correct layout
  - Check is_container_declaration property
  - Call _build_container_content for container declarations
  - Call _build_content for regular declarations
  - _Requirements: 1.3_

- [x] 5.3 Write property test for PDF layout selection
  - **Property 2: PDF Layout Selection**
  - **Validates: Requirements 1.3, 3.1**

## 6. Checkpoint - Verify PDF Generation

- [x] 6. Ensure all tests pass, ask the user if questions arise.

## 7. Integration Testing

- [x] 7.1 Test with real API data from test file
  - Use data from 103.248.160.25-20251210T191933-436.xml
  - Verify PDF matches MV_container.pdf layout
  - _Requirements: All_

- [x] 7.2 Write unit tests for container PDF generation
  - Test _decode_qr_image with valid/invalid data
  - Test _build_container_table with various container counts
  - Test _build_container_content structure

## 8. Update CHANGELOG and Build

- [x] 8.1 Update CHANGELOG.md with V1.2.0 changes
  - Document container PDF support
  - List new features and changes

- [x] 8.2 Build new release
  - Run pyinstaller
  - Create release zip

## 9. Final Checkpoint

- [x] 9. Ensure all tests pass, ask the user if questions arise.
