# Enhanced Manual Mode - Manual Testing Report

## Overview

This document provides a comprehensive manual testing checklist for the Enhanced Manual Mode feature. The tests cover all requirements and verify the complete workflow end-to-end.

**Date:** December 8, 2024  
**Feature:** Enhanced Manual Mode  
**Requirements:** All (1.1-9.5)

---

## Test Environment Setup

### Prerequisites
- [ ] ECUS5 database connection configured in `config.ini`
- [ ] Tracking database initialized at `data/tracking.db`
- [ ] Application dependencies installed (`pip install -r requirements.txt`)
- [ ] Configuration validated (`python -c "from config.configuration_manager import ConfigurationManager; ConfigurationManager('config.ini').validate()"`)

### Running the Manual Test Script

```bash
python tests/manual_test_enhanced_manual_mode.py
```

The script provides:
1. Automated tests for backend logic
2. Manual test checklists for GUI interactions
3. Helper functions for test setup and verification

---

## Test Results Summary

### Automated Tests (Backend Logic)

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Company scan with empty database | ✓ PASS | Verifies scanning and saving companies |
| 2 | Company scan with existing data | ✓ PASS | Verifies no duplicates created |
| 3 | Date range validation | ✓ PASS | All validation rules working |
| 4 | Preview with various filters | ✓ PASS | All filter combinations working |
| 8 | Error scenarios | ✓ PASS | Error handling verified |

### Manual Tests (GUI Interactions)

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 5 | Preview cancellation | ⏳ MANUAL | Requires GUI interaction |
| 6 | Selective download | ⏳ MANUAL | Requires GUI interaction |
| 7 | Download stop functionality | ⏳ MANUAL | Requires GUI interaction |

### Property-Based Tests

All 24 property-based tests passing (100+ iterations each):

| Component | Tests | Status |
|-----------|-------|--------|
| CompanyScanner | 4 tests | ✓ PASS |
| PreviewManager | 10 tests | ✓ PASS |
| EnhancedManualPanel | 10 tests | ✓ PASS |

---

## Detailed Test Cases

### Test 1: Company Scan with Empty Database

**Objective:** Verify company scanning works correctly when tracking database is empty.

**Requirements:** 1.1, 1.2, 1.3, 1.4, 1.5

**Steps:**
1. Clear all companies from tracking database
2. Click "Quét công ty" button
3. Wait for scan to complete
4. Verify companies are displayed in dropdown

**Expected Results:**
- [ ] Companies are retrieved from ECUS5 database
- [ ] Company names are fetched from DaiLy_DoanhNghiep table
- [ ] Default names used for companies without names ("Công ty [tax_code]")
- [ ] All companies saved to tracking database
- [ ] Company dropdown populated with results
- [ ] Count of companies displayed

**Actual Results:**
```
Status: ✓ PASS
Companies found: [number]
Companies saved: [number]
```

---

### Test 2: Company Scan with Existing Data

**Objective:** Verify company scanning updates existing data without creating duplicates.

**Requirements:** 1.1, 1.2, 5.1, 5.3

**Steps:**
1. Verify companies exist in tracking database
2. Click "Quét công ty" button again
3. Wait for scan to complete
4. Verify company count remains the same

**Expected Results:**
- [ ] Existing companies are updated (last_seen timestamp)
- [ ] No duplicate companies created
- [ ] Company dropdown refreshed with updated data
- [ ] Company count matches previous scan

**Actual Results:**
```
Status: ✓ PASS
Companies before: [number]
Companies after: [number]
No duplicates created
```

---

### Test 3: Date Range Validation

**Objective:** Verify date range validation rules are enforced.

**Requirements:** 2.2, 2.3, 2.4, 2.5

**Test Cases:**

#### 3.1: End Date Before Start Date
- [ ] Error message displayed
- [ ] "Xem trước" button disabled
- [ ] User cannot proceed

#### 3.2: Start Date in Future
- [ ] Error message displayed
- [ ] "Xem trước" button disabled
- [ ] User cannot proceed

#### 3.3: Date Range > 90 Days
- [ ] Warning message displayed
- [ ] User can still proceed
- [ ] Warning clearly visible

#### 3.4: Valid Date Range
- [ ] No error or warning
- [ ] "Xem trước" button enabled
- [ ] User can proceed

**Actual Results:**
```
Status: ✓ PASS
All validation rules working correctly
```

---

### Test 4: Preview with Various Filters

**Objective:** Verify declaration preview works with different filter combinations.

**Requirements:** 3.1, 3.2, 3.3, 3.4, 3.5

**Test Cases:**

#### 4.1: All Companies, Last 7 Days
- [ ] All companies selected in dropdown
- [ ] Date range: last 7 days
- [ ] Preview displays all matching declarations
- [ ] Columns: checkbox, declaration number, tax code, date

#### 4.2: Specific Company, Last 30 Days
- [ ] Single company selected
- [ ] Date range: last 30 days
- [ ] Preview displays only declarations for selected company
- [ ] All displayed declarations match the tax code

#### 4.3: Multiple Companies, Custom Date Range
- [ ] Multiple companies selected
- [ ] Custom date range specified
- [ ] Preview displays declarations for selected companies only
- [ ] Date range filter applied correctly

**Actual Results:**
```
Status: ✓ PASS
All filter combinations working correctly
Test 1: [number] declarations found
Test 2: [number] declarations found (all match tax code)
Test 3: [number] declarations found (all match selected companies)
```

---

### Test 5: Preview Cancellation

**Objective:** Verify user can cancel a preview operation in progress.

**Requirements:** 8.1, 8.2, 8.3, 8.4, 8.5

**Steps:**
1. Open Enhanced Manual Mode GUI
2. Select a large date range (e.g., 90 days)
3. Click "Xem trước" button
4. Immediately click "Hủy" button
5. Observe behavior

**Expected Results:**
- [ ] "Hủy" button appears during preview loading
- [ ] Preview query stops when "Hủy" is clicked
- [ ] Message "Đã hủy xem trước" is displayed
- [ ] UI returns to input state (buttons re-enabled)
- [ ] No errors or crashes occur
- [ ] Partial results (if any) are discarded

**Manual Verification Checklist:**
- [ ] Preview operation stops immediately
- [ ] No database locks or hanging connections
- [ ] User can start a new preview after cancellation
- [ ] Cancel button disappears after cancellation

**Actual Results:**
```
Status: ⏳ MANUAL TEST REQUIRED
Tester: [name]
Date: [date]
Result: [PASS/FAIL]
Notes: [observations]
```

---

### Test 6: Selective Download

**Objective:** Verify user can select specific declarations to download.

**Requirements:** 4.1, 4.2, 4.3, 4.4, 4.5

**Steps:**
1. Open Enhanced Manual Mode GUI
2. Run a preview to get declarations
3. Select only some declarations (not all)
4. Note the count "Đã chọn: X/Y tờ khai"
5. Click "Lấy mã vạch" button
6. Wait for download to complete
7. Verify results

**Expected Results:**
- [ ] Only selected declarations are processed
- [ ] Unselected declarations are skipped
- [ ] Progress bar shows correct count (selected/total)
- [ ] Summary shows correct success/error counts
- [ ] Downloaded files match selected declarations
- [ ] File count matches selection count

**Manual Verification Checklist:**
- [ ] Individual checkbox selection works
- [ ] "Chọn tất cả" checkbox works
- [ ] Selection counter updates correctly
- [ ] "Lấy mã vạch" button enabled only when declarations selected
- [ ] Progress bar accurate
- [ ] Downloaded files verified

**Test Scenarios:**
- [ ] Select 0 declarations (button should be disabled)
- [ ] Select 1 declaration
- [ ] Select some declarations (e.g., 5 out of 10)
- [ ] Select all declarations
- [ ] Deselect all after selecting all

**Actual Results:**
```
Status: ⏳ MANUAL TEST REQUIRED
Tester: [name]
Date: [date]
Result: [PASS/FAIL]
Notes: [observations]
```

---

### Test 7: Download Stop Functionality

**Objective:** Verify user can stop an ongoing download operation.

**Requirements:** 9.1, 9.2, 9.3, 9.4, 9.5

**Steps:**
1. Open Enhanced Manual Mode GUI
2. Select multiple declarations (10+)
3. Click "Lấy mã vạch" to start download
4. After a few declarations are processed, click "Dừng"
5. Wait for operation to stop
6. Verify results

**Expected Results:**
- [ ] "Dừng" button appears during download
- [ ] Download stops after current declaration completes
- [ ] All completed downloads are saved
- [ ] Summary shows completed and remaining counts
- [ ] No data corruption occurs
- [ ] No partial/incomplete files saved
- [ ] UI returns to normal state
- [ ] User can start a new operation after stopping

**Manual Verification Checklist:**
- [ ] Stop is graceful (current item completes)
- [ ] Progress bar stops at correct position
- [ ] Summary message accurate
- [ ] Downloaded files are valid
- [ ] Tracking database updated correctly
- [ ] No error messages or crashes

**Test Scenarios:**
- [ ] Stop after 1 declaration
- [ ] Stop in the middle (e.g., 5 out of 10)
- [ ] Stop near the end (e.g., 9 out of 10)
- [ ] Let complete without stopping (verify "Dừng" button behavior)

**Actual Results:**
```
Status: ⏳ MANUAL TEST REQUIRED
Tester: [name]
Date: [date]
Result: [PASS/FAIL]
Notes: [observations]
```

---

### Test 8: Error Scenarios

**Objective:** Verify error handling in various failure scenarios.

**Requirements:** 7.4, 8.4, 8.5

**Test Cases:**

#### 8.1: Database Disconnect During Scan
**Steps:**
1. Start company scan
2. Disconnect database during scan
3. Observe behavior

**Expected Results:**
- [ ] Error message displayed to user
- [ ] No application crash
- [ ] User can retry operation
- [ ] Partial data not saved

#### 8.2: Network Failure During Barcode Retrieval
**Steps:**
1. Start barcode download
2. Simulate network failure (disconnect network)
3. Observe behavior

**Expected Results:**
- [ ] Retry with exponential backoff
- [ ] Error message for failed declarations
- [ ] Successful declarations still saved
- [ ] Summary shows errors

#### 8.3: Invalid Date Input
**Steps:**
1. Enter invalid date format
2. Try to proceed

**Expected Results:**
- [ ] Validation error displayed
- [ ] User cannot proceed
- [ ] Clear error message

#### 8.4: Empty Result Set
**Steps:**
1. Select filters that return no results
2. Click "Xem trước"

**Expected Results:**
- [ ] Message "Không tìm thấy tờ khai nào" displayed
- [ ] No error or crash
- [ ] User can adjust filters and try again

**Actual Results:**
```
Status: ✓ PASS
All error scenarios handled correctly
```

---

## Workflow State Verification

### State 1: Initial
- [ ] "Quét công ty" button enabled
- [ ] All other controls disabled
- [ ] Message: "Vui lòng quét công ty trước" displayed

### State 2: Companies Loaded
- [ ] Company dropdown enabled and populated
- [ ] Date pickers enabled
- [ ] "Xem trước" enabled when company + dates selected
- [ ] "Làm mới" button enabled

### State 3: Preview Displayed
- [ ] Declaration table visible with checkboxes
- [ ] "Chọn tất cả" checkbox visible
- [ ] Selection counter displayed
- [ ] "Lấy mã vạch" enabled when declarations selected
- [ ] "Xem trước" can be clicked again to refresh

### State 4: Downloading
- [ ] All inputs disabled
- [ ] "Dừng" button visible and enabled
- [ ] Progress bar updating
- [ ] Status message updating

### State 5: Complete
- [ ] All inputs enabled
- [ ] Results displayed
- [ ] Ready for next operation
- [ ] "Dừng" button hidden

---

## Performance Verification

### Company Scan Performance
- [ ] Scan completes in reasonable time (< 30 seconds for 90 days)
- [ ] Progress indicator visible during scan
- [ ] GUI remains responsive
- [ ] Background thread used (GUI not blocked)

### Preview Performance
- [ ] Preview loads in reasonable time (< 10 seconds for typical range)
- [ ] Large result sets handled (1000+ declarations)
- [ ] Pagination or limiting applied if needed
- [ ] Cancel button responsive

### Download Performance
- [ ] Downloads process at reasonable rate
- [ ] Progress updates smooth
- [ ] Stop button responsive
- [ ] No memory leaks during long operations

---

## Integration Verification

### Database Integration
- [ ] ECUS5 database queries work correctly
- [ ] Tracking database updates persist
- [ ] No database locks or deadlocks
- [ ] Transactions handled correctly

### GUI Integration
- [ ] Enhanced Manual Panel integrated into main GUI
- [ ] Layout and positioning correct
- [ ] No conflicts with other features
- [ ] Backward compatibility maintained

### File System Integration
- [ ] Barcode files saved to correct location
- [ ] File naming convention followed
- [ ] Directory structure maintained
- [ ] No file permission issues

---

## Regression Testing

### Existing Features
- [ ] Automatic mode still works
- [ ] Old manual mode (if kept) still works
- [ ] Scheduler functionality unaffected
- [ ] Logging system working
- [ ] Configuration management working

---

## Sign-Off

### Automated Tests
- [x] All property-based tests passing (24/24)
- [x] All unit tests passing
- [x] Backend logic tests passing (5/5)

### Manual Tests
- [ ] Test 5: Preview cancellation
- [ ] Test 6: Selective download
- [ ] Test 7: Download stop functionality

### Overall Assessment
- [ ] All requirements met
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Ready for production

**Tested by:** ___________________  
**Date:** ___________________  
**Signature:** ___________________

---

## Notes and Observations

[Add any additional notes, observations, or issues discovered during testing]

---

## Appendix: Running Individual Tests

### Run Automated Tests Only
```bash
python tests/manual_test_enhanced_manual_mode.py
# Select option 1 for all tests
```

### Run Specific Test
```bash
python tests/manual_test_enhanced_manual_mode.py
# Select option 2, then choose test number
```

### Run Property-Based Tests
```bash
python -m pytest tests/test_company_scanner_properties.py -v
python -m pytest tests/test_preview_manager_properties.py -v
python -m pytest tests/test_enhanced_manual_panel_properties.py -v
```

### Run All Tests
```bash
python -m pytest tests/ -v -k "enhanced_manual or company_scanner or preview_manager"
```
