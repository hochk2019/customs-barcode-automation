# Implementation Plan

- [x] 1. Extend Declaration model with SoHSTK field






  - [x] 1.1 Add `so_hstk` field to Declaration dataclass in `models/declaration_models.py`

    - Add optional string field `so_hstk: Optional[str] = None`
    - Add `is_xnktc` property to check XNK TC patterns
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 1.2 Write property test for XNK TC pattern detection


    - **Property 1: XNK TC Pattern Detection**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.5**
  - [x] 1.3 Write property test for null/empty SoHSTK handling


    - **Property 4: Null/Empty SoHSTK Handling**
    - **Validates: Requirements 2.4**

- [x] 2. Extend database query to include SoHSTK field





  - [x] 2.1 Update `get_declarations_by_date_range()` in `database/ecus_connector.py`


    - Add `tk.SoHSTK as so_hstk` to SELECT clause
    - Update `_map_row_to_declaration()` to map so_hstk field
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 2.2 Write unit tests for database query with SoHSTK


    - Test that so_hstk field is correctly mapped
    - _Requirements: 2.1_

- [x] 3. Implement XNK TC filtering in PreviewManager





  - [x] 3.1 Add `filter_xnktc_declarations()` method to `processors/preview_manager.py`


    - Implement filtering logic based on `is_xnktc` property
    - Log number of excluded declarations
    - _Requirements: 1.3, 1.4, 3.2_

  - [x] 3.2 Write property test for filter exclusion completeness

    - **Property 2: Filter Exclusion Completeness**
    - **Validates: Requirements 1.3**

  - [x] 3.3 Write property test for filter inclusion completeness
    - **Property 3: Filter Inclusion Completeness**
    - **Validates: Requirements 1.4**

- [x] 4. Add filter checkbox to GUI




  - [x] 4.1 Add checkbox in `gui/enhanced_manual_panel.py`


    - Add `exclude_xnktc_var` BooleanVar with default True
    - Add checkbox "Không lấy mã vạch tờ khai XNK TC" in control_row
    - Implement `_on_exclude_xnktc_changed()` callback
    - _Requirements: 1.1, 1.2, 1.5_

  - [x] 4.2 Integrate filter with preview operation

    - Update `preview_declarations()` to apply XNK TC filter
    - Update selection count after filtering
    - Update status message to show filtered count
    - _Requirements: 1.3, 1.4, 3.1, 3.3, 4.1, 4.2_

  - [x] 4.3 Write property test for filter state consistency






    - **Property 5: Filter State Consistency**
    - **Validates: Requirements 4.1, 4.2**
  - [x] 4.4 Write unit tests for GUI checkbox




    - Test default checkbox state is True
    - Test checkbox toggle triggers refresh
    - _Requirements: 1.1, 1.2, 1.5_

- [x] 5. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
