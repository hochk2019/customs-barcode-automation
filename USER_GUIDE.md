# Customs Barcode Automation - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Understanding the Interface](#understanding-the-interface)
4. [Basic Operations](#basic-operations)
5. [Advanced Features](#advanced-features)
6. [Common Workflows](#common-workflows)
7. [Tips and Best Practices](#tips-and-best-practices)

## Introduction

The Customs Barcode Automation system is designed to streamline the process of retrieving barcode PDFs for customs declarations. This guide will walk you through all features and help you use the system effectively.

### What Does This System Do?

- **Automatically extracts** declaration information from your ECUS5 database
- **Filters** declarations based on customs rules (green/yellow channel, cleared status)
- **Retrieves** barcode PDFs from the customs authority website
- **Saves** PDFs with standardized filenames for easy management
- **Tracks** processed declarations to avoid duplicates
- **Provides** a user-friendly interface for monitoring and control

## Getting Started

### Initial Setup Checklist

Before using the system for the first time:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] WebDriver (ChromeDriver or EdgeDriver) downloaded and placed in project directory
- [ ] `config.ini` file created and configured with your database details
- [ ] Output directory created and accessible
- [ ] Database connection tested

### First Run

1. Open a command prompt in the project directory
2. Run: `python main.py`
3. The GUI window will appear
4. Check the log panel for any startup messages
5. If you see "Configuration loaded successfully", you're ready to go!

## Understanding the Interface

The application window is divided into three main sections:

### 1. Control Panel (Top Section)

```
┌─ Control Panel ──────────────────────────────────────────────┐
│ Status: ● Running                                             │
│ Mode: ○ Automatic  ○ Manual                                   │
│                                                                │
│ Statistics:                                                    │
│   Declarations Processed: 1,234                                │
│   Barcodes Retrieved: 1,180                                    │
│   Errors: 54                                                   │
│   Last Run: 2023-12-06 14:30:25                                │
│                                                                │
│ [Start] [Stop] [Run Once]                                      │
│                                                                │
│ Output Directory: C:\CustomsBarcodes  [Browse...]              │
└────────────────────────────────────────────────────────────────┘
```

**Status Indicator**:
- **Green dot (●)**: System is running
- **Red dot (●)**: System is stopped

**Mode Selection**:
- **Automatic**: System polls database every 5 minutes
- **Manual**: System only runs when you click "Run Once"

**Statistics Display**:
- **Declarations Processed**: Total count for current session
- **Barcodes Retrieved**: Successfully downloaded PDFs
- **Errors**: Failed operations (network issues, invalid data, etc.)
- **Last Run**: Timestamp of most recent polling cycle

**Control Buttons**:
- **Start**: Begin automatic polling (only in Automatic mode)
- **Stop**: Stop automatic polling
- **Run Once**: Manually trigger a single polling cycle

**Output Directory**:
- Shows where PDF files are saved
- Click **Browse** to change the location

### 2. Processed Declarations Panel (Middle Section)

```
┌─ Processed Declarations ─────────────────────────────────────┐
│ Search: [________________]  [Search]                          │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ☐ 2300782217_308010891440  | 05/01/2023 | 14:25:30       │ │
│ │ ☐ 0700798384_305254416960  | 30/12/2022 | 10:15:22       │ │
│ │ ☐ 2300646077_105205185850  | 05/01/2023 | 09:47:18       │ │
│ │ ...                                                        │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                                │
│ [Re-download Selected] [Open File Location] [Refresh]          │
└────────────────────────────────────────────────────────────────┘
```

**Search Box**:
- Enter declaration number or tax code
- Click **Search** to filter the list
- Leave empty and search to show all declarations

**Declaration List**:
- Each row shows: `TaxCode_DeclarationNumber | Date | Timestamp`
- Check the box to select declarations for re-download
- Double-click to open file location

**Action Buttons**:
- **Re-download Selected**: Retrieve barcodes again for checked items
- **Open File Location**: Open Windows Explorer to the PDF folder
- **Refresh**: Reload the list from the tracking database

### 3. Log Panel (Bottom Section)

```
┌─ Recent Logs ────────────────────────────────────────────────┐
│ 14:30:25 - INFO - Starting workflow cycle                     │
│ 14:30:26 - INFO - Fetched 15 new declarations                 │
│ 14:30:27 - INFO - 12 declarations eligible                    │
│ 14:30:35 - INFO - Successfully saved barcode for 2300782217   │
│ 14:30:36 - ERROR - Failed to retrieve barcode for 0700798384  │
└────────────────────────────────────────────────────────────────┘
```

**Log Messages**:
- **INFO** (blue text): Normal operations
- **WARNING** (yellow text): Non-critical issues
- **ERROR** (red text): Failures requiring attention
- **DEBUG** (gray text): Technical details (only in DEBUG mode)

**Auto-scroll**:
- The log panel automatically scrolls to show the latest messages
- Scroll up to review older messages

## Basic Operations

### Starting Automatic Processing

**When to use**: For continuous, hands-free operation

**Steps**:
1. Select **Automatic** mode (radio button)
2. Click **Start** button
3. Status indicator turns green
4. System polls database every 5 minutes
5. Monitor statistics and logs for progress

**What happens**:
- Every 5 minutes, the system:
  1. Connects to ECUS5 database
  2. Fetches new declarations (last 7 days)
  3. Filters by business rules
  4. Retrieves barcodes for eligible declarations
  5. Saves PDFs to output directory
  6. Updates tracking database

### Stopping Automatic Processing

**Steps**:
1. Click **Stop** button
2. Status indicator turns red
3. Current cycle completes before stopping
4. System waits for next manual trigger

### Manual Processing

**When to use**: For testing, controlled processing, or one-time operations

**Steps**:
1. Select **Manual** mode (radio button)
2. Click **Run Once** button
3. System executes a single polling cycle
4. Wait for completion (watch log panel)
5. Review statistics

**Tip**: Use Manual mode when first setting up the system to verify everything works correctly.

### Changing Output Directory

**Steps**:
1. Click **Browse** button next to Output Directory
2. Select a folder in the dialog
3. Click OK
4. New directory is saved to configuration
5. Future PDFs will be saved to the new location

**Note**: Existing PDFs are not moved automatically.

## Enhanced Manual Mode

Enhanced Manual Mode is a powerful feature that gives you fine-grained control over declaration processing. Instead of processing all declarations from the last N days, you can:

- **Scan and save** a list of companies from your database
- **Select specific companies** to process
- **Choose exact date ranges** (from date to date)
- **Preview declarations** before downloading barcodes
- **Select individual declarations** to process
- **Stop downloads** in progress if needed

This mode is ideal for:
- Processing specific companies or time periods
- Reviewing declarations before downloading
- Selective processing to save time and bandwidth
- Handling special cases or corrections

### Understanding Enhanced Manual Mode Interface

The Enhanced Manual Mode panel appears in the Manual Mode section of the application:

```
┌─ Enhanced Manual Mode ───────────────────────────────────────┐
│                                                                │
│ [Quét công ty]  [Làm mới]                                    │
│                                                                │
│ Lọc theo công ty: [Tất cả công ty ▼]                         │
│                                                                │
│ Từ ngày: [📅 01/12/2024]                                      │
│ Đến ngày: [📅 08/12/2024]                                     │
│                                                                │
│ [Xem trước]  [Lấy mã vạch]  [Dừng]                           │
│                                                                │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Preview: Đã chọn 15/20 tờ khai                         │   │
│ │ ☑ Chọn tất cả                                          │   │
│ │ ──────────────────────────────────────────────────────│   │
│ │ ☑ 302934380950 | 0700809357 | 01/12/2024             │   │
│ │ ☑ 302934380951 | 0700809357 | 02/12/2024             │   │
│ │ ☐ 302934380952 | 0700809357 | 03/12/2024             │   │
│ │ ...                                                    │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                                │
│ [▓▓▓▓▓▓░░░░] Đang xử lý 6/15...                              │
└────────────────────────────────────────────────────────────────┘
```

**UI Components**:

1. **Quét công ty** (Scan Companies): Scans database for all companies with declarations
2. **Làm mới** (Refresh): Reloads company list from saved data
3. **Company Dropdown**: Select a specific company or "Tất cả công ty" (All companies)
4. **Date Pickers**: Choose exact date range (from/to)
5. **Xem trước** (Preview): Display declarations matching your filters
6. **Preview Table**: Shows declarations with checkboxes for selection
7. **Chọn tất cả** (Select All): Toggle all checkboxes at once
8. **Lấy mã vạch** (Get Barcodes): Download barcodes for selected declarations
9. **Dừng** (Stop): Stop an ongoing download operation
10. **Progress Bar**: Shows download progress

### Workflow States

Enhanced Manual Mode follows a clear step-by-step workflow:

**State 1: Initial State**
- Only "Quét công ty" button is enabled
- Message displays: "Vui lòng quét công ty trước" (Please scan companies first)
- All other controls are disabled

**State 2: Companies Loaded**
- Company dropdown is enabled and populated
- Date pickers are enabled
- "Xem trước" button is enabled when company and dates are selected
- You can now filter and preview declarations

**State 3: Preview Displayed**
- Declaration table shows matching declarations
- Checkboxes allow individual selection
- "Lấy mã vạch" button is enabled when declarations are selected
- You can modify selections or preview again with different filters

**State 4: Downloading**
- All input controls are disabled
- "Dừng" button is visible
- Progress bar updates for each declaration
- You can stop the download at any time

**State 5: Complete**
- All controls are re-enabled
- Results summary is displayed
- Ready for next operation

### Company Scanning Workflow

**Step 1: Initial Scan**

When you first use Enhanced Manual Mode, you need to scan for companies:

1. Click **Quét công ty** button
2. System queries ECUS5 database for all unique tax codes
3. Progress indicator shows scanning is in progress
4. System retrieves company names from DaiLy_DoanhNghiep table
5. Companies are saved to local tracking database
6. Company dropdown is populated with results
7. Status message shows: "Đã tìm thấy X công ty" (Found X companies)

**What happens during scan**:
- Scans last 90 days of declarations by default
- Extracts unique tax codes (company identifiers)
- Looks up company names in database
- For companies without names: Uses format "Công ty [tax_code]"
- Saves to local database for future use
- Runs in background thread (GUI remains responsive)

**Time required**: 10-30 seconds depending on database size

**Step 2: Refresh Companies**

After initial scan, companies are saved locally. To update the list:

1. Click **Làm mới** button
2. System reloads companies from local database
3. Dropdown is updated immediately
4. No database query required (instant)

**When to refresh**:
- After scanning companies again
- If dropdown appears empty
- To verify saved companies

**Step 3: Select Company**

1. Click the company dropdown
2. Choose from:
   - **Tất cả công ty** (All companies): Process all companies
   - **Specific company**: Process only that company's declarations
3. Selection is saved for preview and download

**Tips**:
- Start with a specific company to test the workflow
- Use "Tất cả công ty" for comprehensive processing
- Company list is sorted alphabetically

### Date Range Selection

**Choosing Date Range**:

1. Click **Từ ngày** (From date) picker
2. Select start date from calendar
3. Click **Đến ngày** (To date) picker
4. Select end date from calendar
5. System validates the date range

**Date Validation Rules**:

✅ **Valid ranges**:
- Start date is not in the future
- End date is not before start date
- Both dates are selected

❌ **Invalid ranges**:
- Start date in the future → Error: "Ngày bắt đầu không thể trong tương lai"
- End date before start date → Error: "Ngày kết thúc phải sau ngày bắt đầu"
- Missing dates → Preview button remains disabled

⚠️ **Warnings**:
- Range exceeds 90 days → Warning: "Khoảng thời gian quá dài (>90 ngày), có thể mất nhiều thời gian"
- System still allows the operation but warns about performance

**Date Format**:
- Display format: DD/MM/YYYY (e.g., 01/12/2024)
- Calendar widget for easy selection
- Manual entry is also supported

**Best Practices**:
- Start with shorter ranges (7-14 days) to test
- Use longer ranges (30-90 days) for comprehensive processing
- Avoid ranges over 90 days unless necessary
- Consider database performance for very long ranges

### Declaration Preview Workflow

**Step 1: Generate Preview**

1. Select company from dropdown
2. Choose date range
3. Click **Xem trước** button
4. System queries database in background
5. "Hủy" (Cancel) button appears during query
6. Preview table populates with results

**What the preview shows**:
- **Checkbox**: Select/deselect individual declarations
- **Declaration Number**: Unique identifier (e.g., 302934380950)
- **Tax Code**: Company identifier (e.g., 0700809357)
- **Date**: Declaration date (DD/MM/YYYY)

**Preview header**:
- Shows: "Đã chọn: X/Y tờ khai" (Selected: X/Y declarations)
- X = number of selected declarations
- Y = total declarations in preview

**Step 2: Review Results**

After preview loads:

- **Zero results**: Message displays "Không tìm thấy tờ khai nào" (No declarations found)
  - Try different date range
  - Try different company
  - Verify data exists in database

- **Results found**: Table displays all matching declarations
  - All declarations are selected by default
  - Scroll through the list to review
  - Check declaration numbers and dates

**Step 3: Cancel Preview (if needed)**

If preview is taking too long:

1. Click **Hủy** button (appears during loading)
2. Query is stopped immediately
3. System returns to input state
4. Message displays: "Đã hủy xem trước" (Preview cancelled)
5. Adjust filters and try again

**When to cancel**:
- Query is taking over 30 seconds
- You realize filters are incorrect
- You want to change date range or company

### Selection and Filtering

**Selecting Declarations**:

**Method 1: Select All**
1. Click **Chọn tất cả** checkbox at top of table
2. All declarations are selected
3. Counter updates: "Đã chọn: Y/Y tờ khai"
4. Click again to deselect all

**Method 2: Individual Selection**
1. Click checkbox next to specific declaration
2. Declaration is selected/deselected
3. Counter updates automatically
4. Select as many or as few as needed

**Method 3: Mixed Selection**
1. Click "Chọn tất cả" to select all
2. Uncheck specific declarations to exclude
3. Or start with none selected and check specific ones

**Selection Counter**:
- Always visible: "Đã chọn: X/Y tờ khai"
- Updates in real-time as you select/deselect
- X must be > 0 to enable "Lấy mã vạch" button

**Use Cases**:

- **Process all**: Keep all selected (default)
- **Skip problematic declarations**: Deselect specific ones
- **Process only new declarations**: Deselect already processed ones
- **Test with small batch**: Select only 2-3 declarations first

### Selective Download Workflow

**Step 1: Initiate Download**

1. Ensure declarations are selected (X > 0)
2. Click **Lấy mã vạch** button
3. System begins processing selected declarations
4. All input controls are disabled
5. "Dừng" button appears
6. Progress bar starts updating

**What happens during download**:
- System processes declarations sequentially
- For each declaration:
  1. Retrieves barcode from customs website
  2. Saves PDF to output directory
  3. Updates tracking database
  4. Updates progress bar
  5. Logs success or error
- Skips unselected declarations completely

**Step 2: Monitor Progress**

**Progress Bar**:
- Shows: [▓▓▓▓▓▓░░░░] Đang xử lý 6/15...
- Updates after each declaration
- Percentage and count displayed

**Log Panel**:
- Shows real-time progress
- Success messages: "Successfully saved barcode for [number]"
- Error messages: "Failed to retrieve barcode for [number]"
- Monitor for issues

**Time Estimates**:
- ~5-10 seconds per declaration
- 10 declarations: ~1-2 minutes
- 50 declarations: ~5-10 minutes
- 100 declarations: ~10-20 minutes

**Step 3: Stop Download (if needed)**

If you need to stop the download:

1. Click **Dừng** button
2. System stops after current declaration completes
3. All successfully downloaded barcodes are saved
4. Summary displays:
   - "Đã xử lý: X tờ khai" (Processed: X declarations)
   - "Còn lại: Y tờ khai" (Remaining: Y declarations)
5. All controls are re-enabled
6. You can preview again or adjust selections

**When to stop**:
- Taking longer than expected
- Need to leave computer
- Noticed incorrect selections
- Errors are occurring frequently

**What is saved**:
- All declarations processed before clicking "Dừng"
- Tracking database is updated
- PDFs are saved to output directory
- Remaining declarations are not processed

**Step 4: Review Results**

After download completes or is stopped:

**Success Summary**:
- "Hoàn thành: X/Y tờ khai thành công" (Completed: X/Y declarations successful)
- "Lỗi: Z tờ khai" (Errors: Z declarations)

**Check Results**:
1. Review log panel for errors
2. Check output directory for PDFs
3. Verify file count matches success count
4. Investigate any errors

**Next Steps**:
- If errors occurred: Review error messages, retry failed declarations
- If successful: Process next batch or close application
- If stopped: Resume by previewing again and selecting remaining declarations

### Common Enhanced Manual Mode Workflows

**Workflow 1: Process Specific Company for Last Week**

1. Click **Quét công ty** (first time only)
2. Select company from dropdown
3. Set "Từ ngày" to 7 days ago
4. Set "Đến ngày" to today
5. Click **Xem trước**
6. Review declarations in preview
7. Keep all selected or adjust
8. Click **Lấy mã vạch**
9. Monitor progress
10. Review results

**Time**: 2-5 minutes for ~20-50 declarations

**Workflow 2: Process All Companies for Specific Date**

1. Ensure companies are scanned
2. Select **Tất cả công ty** from dropdown
3. Set both "Từ ngày" and "Đến ngày" to same date
4. Click **Xem trước**
5. Review declarations
6. Click **Lấy mã vạch**
7. Monitor progress

**Time**: 5-15 minutes depending on declaration count

**Workflow 3: Selective Processing with Preview**

1. Select company and date range
2. Click **Xem trước**
3. Review all declarations
4. Deselect declarations already processed
5. Deselect declarations with known issues
6. Keep only new/valid declarations selected
7. Click **Lấy mã vạch**
8. Monitor progress

**Time**: 3-10 minutes depending on review time

**Workflow 4: Large Batch with Stop Control**

1. Select **Tất cả công ty**
2. Set date range to 30-60 days
3. Click **Xem trước**
4. Review count (may be 100+ declarations)
5. Click **Lấy mã vạch**
6. Monitor progress for first 10-20 declarations
7. If issues arise, click **Dừng**
8. Review partial results
9. Adjust and continue

**Time**: 15-30 minutes for large batches

**Workflow 5: Daily Incremental Processing**

1. Companies already scanned (from previous day)
2. Click **Làm mới** to reload companies
3. Select **Tất cả công ty**
4. Set "Từ ngày" to yesterday
5. Set "Đến ngày" to today
6. Click **Xem trước**
7. Click **Lấy mã vạch** (all selected)
8. Review results

**Time**: 2-5 minutes for daily incremental

**Workflow 6: Re-scan Companies Monthly**

1. Click **Quét công ty** at start of month
2. Wait for scan to complete
3. Review company count
4. New companies are added automatically
5. Proceed with normal processing

**Time**: 30-60 seconds for scan

### Enhanced Manual Mode Best Practices

**Company Management**:
- Scan companies once per week or month
- Use "Làm mới" for daily operations
- Re-scan when new companies are added to database
- Company list persists across application restarts

**Date Range Selection**:
- Start with 7-14 day ranges for testing
- Use 30-day ranges for regular processing
- Avoid ranges over 90 days unless necessary
- Consider database performance for long ranges

**Preview Usage**:
- Always preview before downloading
- Review declaration count before proceeding
- Use preview to verify filters are correct
- Cancel and adjust if results are unexpected

**Selection Strategy**:
- Start with "Select All" for comprehensive processing
- Deselect problematic declarations individually
- For testing: Select only 2-3 declarations first
- For production: Process all selected declarations

**Download Management**:
- Monitor progress for first few declarations
- Use "Dừng" if errors are frequent
- Review log panel during download
- Don't close application during download

**Error Handling**:
- If preview fails: Check database connection
- If download fails: Check internet connection
- If specific declarations fail: Note numbers and retry later
- If many failures: Stop and investigate root cause

**Performance Tips**:
- Shorter date ranges = faster previews
- Specific companies = fewer declarations
- Smaller batches = easier to manage
- Background processing = GUI remains responsive

### Troubleshooting Enhanced Manual Mode

**Problem: "Quét công ty" button does nothing**
- Check database connection
- Review log panel for errors
- Verify ECUS5 database is accessible
- Try restarting application

**Problem: Company dropdown is empty**
- Click "Quét công ty" to scan
- Check if scan completed successfully
- Review log for scan errors
- Verify declarations exist in database

**Problem: Preview returns zero results**
- Verify date range is correct
- Check if selected company has declarations in that period
- Try "Tất cả công ty" instead of specific company
- Expand date range

**Problem: Preview is very slow**
- Date range may be too long (>90 days)
- Database may be slow
- Click "Hủy" and try shorter range
- Consider database performance optimization

**Problem: Cannot select declarations**
- Ensure preview has loaded completely
- Check if checkboxes are visible
- Try clicking "Chọn tất cả" first
- Refresh preview if needed

**Problem: "Lấy mã vạch" button is disabled**
- Ensure at least one declaration is selected
- Check selection counter: "Đã chọn: X/Y"
- If X = 0, select declarations
- Preview must be loaded first

**Problem: Download is very slow**
- Network connection may be slow
- Customs website may be slow
- Each declaration takes 5-10 seconds
- This is normal for large batches

**Problem: Many download errors**
- Check internet connection
- Verify WebDriver is working
- Check customs website availability
- Review specific error messages in log
- Try stopping and retrying later

**Problem: "Dừng" button doesn't work immediately**
- System completes current declaration first
- Wait 5-10 seconds for current operation
- Progress will stop after current declaration
- This is normal behavior

**Problem: Application freezes during operation**
- Operations run in background threads
- GUI should remain responsive
- If frozen: Wait 30 seconds
- If still frozen: Close and restart application
- Report issue with log files

### Enhanced Manual Mode vs. Standard Mode

**When to use Enhanced Manual Mode**:
- Need to process specific companies
- Need exact date range control
- Want to preview before downloading
- Need selective processing
- Handling special cases or corrections
- Testing or validation

**When to use Standard Mode**:
- Regular daily/weekly processing
- Process all declarations automatically
- Don't need preview or selection
- Hands-free operation preferred
- Continuous monitoring

**Key Differences**:

| Feature | Standard Mode | Enhanced Manual Mode |
|---------|--------------|---------------------|
| Company Selection | All companies | Specific or all |
| Date Selection | Last N days | Exact from/to dates |
| Preview | No preview | Full preview with details |
| Selection | All declarations | Individual selection |
| Control | Start/Stop only | Preview, Select, Download, Stop |
| Use Case | Automated processing | Controlled processing |
| Output Directory | Fixed in config | Selectable via UI |
| Date Picker | Manual entry | Calendar widget |
| Company Search | Dropdown only | Searchable dropdown |

**Recommendation**:
- Use Standard Mode for 80% of operations
- Use Enhanced Manual Mode for 20% of special cases
- Both modes can be used in same session
- Switch between modes as needed

### New Features in Enhanced Manual Mode (December 2024)

#### 1. Output Directory Selection

You can now choose where to save barcode PDFs directly from the UI:

**Location**: Enhanced Manual Mode panel, top section

**How to use**:
1. Look for "Thư mục lưu:" (Output Directory) field
2. Current directory is displayed in the text box
3. Click **"Chọn..."** (Browse) button
4. Select a folder in the dialog
5. Click OK to confirm

**Benefits**:
- No need to edit config.ini
- Change output location on the fly
- Different locations for different batches
- Selection is saved and remembered

**Example**:
```
Thư mục lưu: C:\CustomsData\December2024  [Chọn...]
```

#### 2. Calendar Date Picker

Date selection is now easier with a visual calendar:

**Location**: "Từ ngày" and "Đến ngày" fields

**How to use**:
1. Click on the date field
2. A calendar popup appears
3. Click on the desired date
4. Date is automatically filled in DD/MM/YYYY format
5. Or type the date manually if preferred

**Benefits**:
- No typing errors
- Visual date selection
- Faster than manual entry
- Automatic format validation

**Features**:
- Vietnamese locale support
- Highlights current date
- Easy month/year navigation
- Prevents invalid dates

#### 3. Searchable Company Dropdown

Finding companies is now much faster:

**Location**: "Lọc theo công ty" dropdown

**How to use**:
1. Click on the company dropdown
2. Start typing:
   - Tax code: Type "0700" to find companies with that tax code
   - Company name: Type "ABC" to find companies with "ABC" in name
3. List filters in real-time as you type
4. Select from filtered results
5. If no matches: "Không tìm thấy" is displayed

**Benefits**:
- No scrolling through long lists
- Fast search by tax code or name
- Case-insensitive matching
- Real-time filtering

**Example**:
```
Type: "0700"
Shows: 
  - CÔNG TY ABC (0700123456)
  - CÔNG TY XYZ (0700789012)
```

#### 4. Performance Improvements

The system is now significantly faster:

**API Timeout Reduction**:
- Old: 30 seconds per attempt
- New: 10 seconds per attempt
- Result: 67% faster failure detection

**Session Reuse**:
- Old: New connection for each request
- New: Reuse connection across batch
- Result: Faster processing for large batches

**Smart Method Skipping**:
- System learns which methods fail
- Skips consistently failing methods
- Focuses on methods that work
- Result: Less time wasted on failures

**Adaptive Selectors**:
- Multiple selector variations tried automatically
- Caches working selectors for reuse
- Adapts to website changes
- Result: More reliable barcode retrieval

**Overall Impact**:
- Faster downloads (average 5-10 seconds per declaration)
- Better success rate
- Less waiting time
- More efficient batch processing

## V1.1 Settings (December 2024)

### Settings Dialog

V1.1 introduces a new Settings dialog for easy configuration without editing config files.

**Accessing Settings**:
1. Click **"⚙ Cài đặt"** button in the Control Panel (next to "Cấu hình DB")
2. Settings dialog opens with current configuration

**Available Settings**:

#### Retrieval Method (Phương thức lấy mã vạch)
Choose how the system retrieves barcodes:
- **Tự động (Auto)**: Try API first, fallback to Web on failure (recommended)
- **Chỉ dùng API**: Use API only, no fallback
- **Chỉ dùng Web**: Use web scraping only

#### PDF Naming Format (Định dạng tên file PDF)
Choose how PDF files are named:
- **Mã số thuế + Số tờ khai**: `{tax_code}_{declaration_number}.pdf` (default)
  - Example: `2300944637_107784915560.pdf`
- **Số hóa đơn + Số tờ khai**: `{invoice_number}_{declaration_number}.pdf`
  - Example: `JYE-VN-P-25-259_107784915560.pdf`
- **Số vận đơn + Số tờ khai**: `{bill_of_lading}_{declaration_number}.pdf`
  - Example: `FCHAN2512025_107784915560.pdf`

**Note**: If the selected field (invoice number or bill of lading) is empty for a declaration, the system automatically falls back to tax_code format.

**Saving Settings**:
1. Select your preferred options
2. Click **"Lưu"** to save
3. Settings are persisted to config.ini
4. Click **"Hủy"** to cancel without saving

### Smart Company Search

V1.1 introduces intelligent company search:

**How it works**:
1. Type in the search field (name or tax code)
2. Company dropdown filters in real-time
3. If exact match found, company is auto-selected
4. If multiple matches, select from filtered dropdown

**Search examples**:
- Type `0700` → Shows all companies with tax codes starting with 0700
- Type `ABC` → Shows all companies with "ABC" in their name
- Type `0700123456` (exact tax code) → Auto-selects that company

**Benefits**:
- No scrolling through long company lists
- Fast lookup by tax code or name
- Case-insensitive matching

### Default Unchecked Declarations

V1.1 changes the default selection behavior in preview:

**Previous behavior**: All declarations checked by default
**New behavior**: All declarations unchecked by default

**Why this change**:
- Prevents accidental processing of unwanted declarations
- Gives you full control over what gets processed
- Reduces errors from processing wrong declarations

**How to use**:
1. Click **"Xem trước"** to load declarations
2. All declarations appear unchecked
3. Use **"Chọn tất cả"** to check all at once
4. Or click individual checkboxes to select specific declarations
5. Selection counter shows: "Đã chọn: X/Y tờ khai"

## Advanced Features

### Re-downloading Barcodes

**When to use**:
- PDF file was accidentally deleted
- File is corrupted
- Need to update an existing barcode

**Steps**:
1. Navigate to **Processed Declarations** panel
2. Find the declaration (use Search if needed)
3. Check the box next to the declaration
4. Click **Re-download Selected**
5. System retrieves the barcode again
6. Existing PDF is overwritten
7. Timestamp is updated in the tracking database

**Multiple re-downloads**:
- Check multiple boxes to re-download several declarations at once
- System processes them sequentially

### Searching Declarations

**By Declaration Number**:
1. Enter the declaration number in the search box
2. Example: `308010891440`
3. Click **Search**
4. List shows matching declarations

**By Tax Code**:
1. Enter the tax code in the search box
2. Example: `2300782217`
3. Click **Search**
4. List shows all declarations for that tax code

**Partial Search**:
- Enter part of a number: `3080` will match `308010891440`
- Search is case-insensitive

**Clear Search**:
- Clear the search box
- Click **Search** to show all declarations

### Opening File Location

**Steps**:
1. Select a declaration from the list (single-click)
2. Click **Open File Location**
3. Windows Explorer opens to the output directory
4. The PDF file is highlighted (if it exists)

**Use cases**:
- Quickly access PDF files
- Verify file was saved correctly
- Copy files to another location
- Email or print PDFs

## Common Workflows

### Daily Monitoring Workflow

**Recommended for regular operations**:

1. **Morning Setup** (9:00 AM)
   - Start the application
   - Verify Automatic mode is selected
   - Click Start
   - Check initial statistics

2. **Periodic Checks** (every 2-3 hours)
   - Review statistics for progress
   - Check log panel for errors
   - Investigate any ERROR messages

3. **End of Day** (5:00 PM)
   - Review final statistics
   - Check for any failed declarations
   - Re-download any failed items if needed
   - Click Stop (or leave running overnight)

### Handling Failed Declarations

**When you see errors in the log**:

1. **Identify the failure**
   - Note the declaration number from error message
   - Check error type (network, API, web scraping)

2. **Investigate the cause**
   - Network error: Check internet connection
   - API error: Verify API service is online
   - Web scraping error: Check WebDriver and browser
   - Data error: Verify declaration data in ECUS5

3. **Retry the declaration**
   - Search for the declaration in Processed Declarations
   - If listed: Check box and click Re-download Selected
   - If not listed: Wait for next polling cycle (automatic retry)

4. **Manual intervention**
   - If repeated failures: Manually retrieve barcode from customs website
   - Save PDF to output directory with correct filename format
   - System will detect it on next cycle

### Bulk Re-download Workflow

**When you need to refresh multiple barcodes**:

1. **Identify declarations to re-download**
   - Use Search to filter by date range or tax code
   - Or scroll through the list

2. **Select declarations**
   - Check boxes for all declarations to re-download
   - Tip: Select 10-20 at a time for manageable batches

3. **Initiate re-download**
   - Click Re-download Selected
   - Monitor log panel for progress

4. **Verify completion**
   - Check statistics for success/error counts
   - Review log for any failures
   - Retry failed items if needed

### End of Month Processing

**For monthly reporting or archival**:

1. **Generate full list**
   - Click Refresh in Processed Declarations panel
   - Clear search box and search to show all

2. **Export data** (manual process)
   - Copy declaration numbers from the list
   - Paste into Excel or reporting tool

3. **Archive PDFs**
   - Open File Location
   - Copy all PDFs to archive folder
   - Organize by month: `Archive\2023-12\`

4. **Clean up** (optional)
   - Delete old PDFs from output directory
   - Keep tracking database intact (for duplicate prevention)

## Tips and Best Practices

### Performance Optimization

**For high-volume operations**:
- Use Automatic mode for continuous processing
- Set polling interval to 3-5 minutes (balance between responsiveness and load)
- Ensure adequate disk space for PDFs
- Monitor system resources (CPU, memory, network)

**For low-volume operations**:
- Use Manual mode to conserve resources
- Run once or twice per day
- Increase polling interval to 10-15 minutes if using Automatic mode

### Error Prevention

**Database connectivity**:
- Test connection before starting automatic mode
- Ensure SQL Server is stable and accessible
- Use a dedicated database user with read-only permissions

**Network reliability**:
- Use wired connection instead of WiFi when possible
- Ensure firewall allows outbound connections to customs websites
- Keep WebDriver updated to match browser version

**File management**:
- Choose output directory on a drive with ample space
- Regularly archive old PDFs
- Don't manually rename or move PDFs while system is running

### Monitoring Best Practices

**What to watch**:
- **Error count**: Should be low (< 5% of total)
- **Log messages**: Review ERROR and WARNING messages
- **Statistics trends**: Track daily/weekly processing volumes

**When to investigate**:
- Sudden increase in errors
- No declarations processed for extended period
- Repeated failures for same declaration
- Disk space warnings

### Maintenance Tasks

**Daily**:
- Review error logs
- Check statistics for anomalies
- Verify PDFs are being saved correctly

**Weekly**:
- Archive old PDFs
- Review log files for patterns
- Check disk space

**Monthly**:
- Backup tracking database
- Backup configuration files
- Review and optimize polling interval
- Update WebDriver if needed

### Security Best Practices

**Configuration**:
- Keep `config.ini` secure (contains encrypted passwords)
- Backup `.encryption_key` file
- Don't share configuration files

**Access control**:
- Restrict access to output directory
- Use Windows file permissions
- Consider encrypting sensitive directories

**Updates**:
- Keep Python and dependencies updated
- Update WebDriver regularly
- Apply Windows security patches

### Troubleshooting Tips

**Before contacting support**:
1. Check the log files (`logs/app.log`)
2. Review error messages in GUI
3. Verify configuration settings
4. Test database connection
5. Test internet connectivity
6. Restart the application

**Information to provide**:
- Error messages (exact text)
- Log file excerpts (last 50-100 lines)
- Configuration details (without passwords)
- Steps to reproduce the issue
- Screenshots of GUI (if applicable)

### Troubleshooting New Features (December 2024)

**Problem: Output directory selection not working**

Symptoms:
- "Chọn..." button doesn't respond
- Selected directory not saved

Solutions:
1. Ensure you have write permissions to the selected directory
2. Create the directory if it doesn't exist
3. Avoid paths with special characters
4. Check Windows file permissions
5. Try selecting a different directory

**Problem: Calendar date picker not appearing**

Symptoms:
- Clicking date field shows only text box
- No calendar popup

Solutions:
1. Install tkcalendar: `pip install tkcalendar>=1.6.1`
2. Restart the application
3. Verify requirements.txt is updated
4. Check for import errors in logs

**Problem: Company dropdown search not filtering**

Symptoms:
- Typing in dropdown doesn't filter results
- All companies still shown

Solutions:
1. Restart the application
2. Re-scan companies using "Quét công ty"
3. Ensure you're using the latest version
4. Check if dropdown is in correct state (editable)

**Problem: Download speed not improved**

Symptoms:
- Still taking 30+ seconds per declaration
- No performance improvement noticed

Solutions:
1. Check internet connection speed
2. Verify config.ini has new settings:
   ```ini
   [BarcodeService]
   api_timeout = 10
   web_timeout = 15
   max_retries = 1
   session_reuse = true
   ```
3. Restart application after config changes
4. Check if customs website is slow
5. Review logs for timeout messages

**Problem: Duplicate declarations still appearing**

Symptoms:
- Same declaration appears multiple times in preview
- Duplicate downloads occurring

Solutions:
1. Ensure you're using the latest version
2. Check database query is using DISTINCT
3. Review logs for duplicate detection warnings
4. Restart application
5. Contact support if issue persists

## Keyboard Shortcuts

While the application doesn't have built-in keyboard shortcuts, you can use standard Windows shortcuts:

- **Alt + Tab**: Switch between applications
- **Ctrl + C**: Copy selected text from log panel
- **F5**: Refresh (when focused on Processed Declarations)
- **Alt + F4**: Close application (stops processing)

## Conclusion

This user guide covers all aspects of the Customs Barcode Automation system. For technical details, refer to the README.md file. For troubleshooting, consult the Troubleshooting section in README.md.

Remember:
- Start with Manual mode to familiarize yourself with the system
- Monitor logs regularly to catch issues early
- Keep configuration and tracking database backed up
- Contact support if you encounter persistent issues

Happy automating!
