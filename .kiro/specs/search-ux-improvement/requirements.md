# Requirements Document

## Introduction

Cải tiến trải nghiệm tìm kiếm công ty trong ô AutocompleteCombobox để đạt được trải nghiệm mượt mà như Google Search. Người dùng có thể gõ liên tục hoặc nghỉ mà không bị gián đoạn, kết quả hiển thị realtime và không làm mất text đã gõ.

## Glossary

- **AutocompleteCombobox**: Widget kết hợp ô nhập liệu và dropdown list với chức năng tự động lọc
- **Debounce**: Kỹ thuật trì hoãn thực thi để tránh gọi quá nhiều lần khi người dùng gõ nhanh
- **Dropdown**: Danh sách kết quả hiển thị bên dưới ô nhập liệu
- **Cursor**: Vị trí con trỏ trong ô nhập liệu
- **Selection**: Phần text được chọn (highlight) trong ô nhập liệu

## Requirements

### Requirement 1

**User Story:** As a user, I want to type continuously without interruption, so that I can search for companies smoothly.

#### Acceptance Criteria

1. WHEN a user types in the search box THEN the system SHALL NOT select or highlight any existing text
2. WHEN a user pauses typing and resumes THEN the system SHALL preserve the cursor position at the end of text
3. WHEN the dropdown opens THEN the system SHALL NOT move or reset the cursor position
4. WHEN a user types THEN the system SHALL NOT close and reopen the dropdown repeatedly

### Requirement 2

**User Story:** As a user, I want to see search results quickly, so that I can find companies efficiently.

#### Acceptance Criteria

1. WHEN a user types THEN the system SHALL filter results within 150ms debounce delay
2. WHEN filtering completes THEN the system SHALL update the dropdown list without closing it
3. WHEN no matches are found THEN the system SHALL display "Không tìm thấy" message
4. WHEN search text is empty THEN the system SHALL show all available companies

### Requirement 3

**User Story:** As a user, I want visual feedback about search results, so that I know how many matches were found.

#### Acceptance Criteria

1. WHEN filtering completes THEN the system SHALL display the count of matching results
2. WHEN results are displayed THEN the system SHALL show format "Tìm thấy X công ty"
3. WHEN no matches are found THEN the system SHALL show "Không tìm thấy kết quả"

### Requirement 4

**User Story:** As a user, I want the dropdown to behave predictably, so that I can navigate results easily.

#### Acceptance Criteria

1. WHEN a user starts typing THEN the system SHALL open the dropdown automatically
2. WHEN the dropdown is open and user continues typing THEN the system SHALL keep the dropdown open
3. WHEN a user clicks outside the combobox THEN the system SHALL close the dropdown
4. WHEN a user presses Escape THEN the system SHALL close the dropdown and keep the text

### Requirement 5

**User Story:** As a user, I want keyboard navigation, so that I can select results without using the mouse.

#### Acceptance Criteria

1. WHEN the dropdown is open and user presses Down arrow THEN the system SHALL highlight the next item
2. WHEN the dropdown is open and user presses Up arrow THEN the system SHALL highlight the previous item
3. WHEN an item is highlighted and user presses Enter THEN the system SHALL select that item
4. WHEN a user presses Tab THEN the system SHALL select the first matching item and move focus

### Requirement 6

**User Story:** As a user, I want a clear button, so that I can quickly clear the search and start over.

#### Acceptance Criteria

1. WHEN text is present in the search box THEN the system SHALL display a clear (X) button
2. WHEN the clear button is clicked THEN the system SHALL clear all text and show placeholder
3. WHEN the search box is empty THEN the system SHALL hide the clear button
