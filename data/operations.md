# Functional Requirements: "Operations" Section

## 1. General Purpose

This section is intended for managing the organization’s financial operations, including viewing, creating, and editing operations, importing bank statements, and managing automatic processing rules.

## 2. Section Structure

The section consists of three main tabs:

* **Operations** — view and manage financial operations
* **Import** — upload and process bank statements
* **Rules** — configure automatic rules for processing operations

## 3. "Operations" Tab

### 3.1 Viewing Operations

**Operations list display**

* Operations are displayed in a table with a mobile-responsive design
* Each operation shows:

  * Amount with a direction icon (up arrow for income, down arrow for expenses)
  * Operation date and time
  * Operation description (inline editable)
  * Tags: category, direction, counterparty (inline editable)
  * Organization account
* Income amounts are highlighted in green, expenses in red
* Inline editing of all operation fields is supported

### 3.2 Search and Filtering

**Text search**

* Search operations by description and any textual content
* Search works in real time while typing
* Search field with a search icon and clear option

**Date filtering**

* Select predefined periods from a dropdown
* Automatic recalculation when the period changes
* Only operations within the selected period are displayed

**Parameter filtering**

* Filter by operation groups (income, expenses, etc.) — single select
* Filter by categories — multi-select with search
* Filter by organization accounts — multi-select with search
* Filter by counterparties — multi-select with search
* Filter by directions — multi-select with search
* All filters can be combined
* Ability to clear each filter separately

### 3.3 Operations Management

**Creating a new operation**

* “Add Operation” button opens a modal window
* Required fields must be filled in
* Data validation before saving
* Automatic refresh of the list after creation

**Inline editing**

* Operation description is edited directly in the table on blur
* Tags (category, direction, counterparty) are edited on click
* Clicking opens a searchable dropdown
* Tags can be removed by clicking the cross icon
* If a tag is missing, a plus button is shown to add it
* Changes are saved automatically

**Deleting an operation**

* Delete button in the operation row
* Confirmation prompt before deletion
* Automatic refresh of the list after deletion

**Viewing transactions for an operation**

* Ability to open a modal window with a list of related transactions
* Navigation to detailed operation view

### 3.4 Data Export

**Export operations**

* “Export” button in the tab header
* Export to Excel (XLSX) format
* Export respects all applied filters
* Automatic file download after generation
* File name is generated automatically

### 3.5 Pagination

**Page navigation**

* Operations list is loaded page by page for performance
* Navigation controls at the bottom of the table
* Current page indicator
* Ability to go to next/previous page
* Information about availability of next pages

## 4. "Import" Tab

### 4.1 File Upload

**File upload area**

* UploadArea component with drag & drop support
* “Upload Statement” button to select files
* Information about supported formats: Excel, PDF
* Hint: “Choose files or simply drag them here”

**Supported formats**

* Excel (.xls, .xlsx)
* PDF
* Ability to upload multiple files at once

**Upload process**

* Select files via dialog or drag into the area
* Automatic upload to the server after selection
* Display of upload progress
* Notification of upload results (success/error)
* Automatic refresh of the statements list after upload

### 4.2 Viewing Uploaded Statements

**Statements table**

* List of statements displayed as a table with columns:

  * File (name and file type icon)
  * File size
  * Upload date
  * Processing status
  * Actions
* File icons are colored (red for PDF, green for Excel)

**Statement statuses**

* Pending (PENDING) — blue tag
* Processing (PROCESSING) — yellow tag
* Ready for mapping (READY_FOR_MAPPING) — yellow tag
* Mapped (MAPPED) — green tag
* Imported (IMPORTED) — green tag
* Error (ERROR) — red tag

**“No data” state**

* Displayed when there are no statements
* Message: “No statements found”
* “Upload your first statement” button for quick access

### 4.3 Statement Actions

**Configure statement**

* Button with an eye icon to view
* Opens the StatementModal
* Allows mapping configuration and data import
* After import, the operations list is refreshed

**Delete statement**

* Button with a trash icon
* Confirmation prompt with warning
* Warning about deleting related operations
* Automatic refresh of the list after deletion

**Pagination**

* Page-by-page viewing of statements (10 per page)
* Navigation controls at the bottom of the card
* Displayed only when there are next pages

## 5. "Rules" Tab

### 5.1 Purpose

**Automation of operation processing**

* Rules allow automatic filling of operation fields
* Applied based on conditions
* Simplify handling of recurring operations
* Have an execution priority

### 5.2 Displaying Rules

**Rules table**

* Table columns:

  * Drag handle to change priority
  * Target field (which field will be filled)
  * Value (what the field will be filled with)
  * Conditions (when the rule applies)
  * Actions (edit/delete)

**Drag & Drop**

* Ability to drag rules to change priority
* Visual indication during dragging
* Automatic saving of the new order

**“No data” state**

* Displayed when there are no rules
* Message: “No rules found”
* “Add your first rule” button

### 5.3 Creating and Editing Rules

**Create rule**

* “Add Rule” button opens a modal window
* Select target field
* Select value to fill
* Configure rule conditions
* Validation before saving

**Edit rule**

* Edit button opens a modal with rule data
* Ability to change all parameters
* Saving updates the list

**Delete rule**

* Delete button with confirmation
* Prompt: “Are you sure you want to delete this rule?”
* Automatic refresh of the list after deletion

### 5.4 Conditions and Values

**Target fields**

* Operation category (categoryId)
* Direction (directionId)
* Other operation fields

**Condition types**

* Equals (eq)
* Not equals (ne)
* Greater than (gt), Greater than or equals (gte)
* Less than (lt), Less than or equals (lte)
* Contains (contains)
* Does not contain (not_contains)
* In (in)

**Condition display**

* Conditions are shown as tags
* Format: “Field operator Value”
* Example: “Description contains ‘Rent’”

### 5.5 Rule Priority

**Order of application**

* Rules are applied from top to bottom
* The first matching rule is executed
* Priority can be changed via drag & drop
* Visual indication of the current priority

## 6. Integration with Reference Data

**Using reference data**

* The system uses reference data for:

  * Operation categories
  * Directions
  * Organization accounts
  * Counterparties
  * Operation groups
  * Activity types
* актуальные данные отображаются при выборе в фильтрах
* Reference data is loaded during initialization

## 7. User Interface

### 7.1 Navigation

* The section consists of three tabs: “Operations”, “Import”, “Rules”
* Switching between tabs via tab controls
* Each tab сохраняет свое состояние
* The active tab is highlighted in blue

### 7.2 Feedback

* Loading indicators during operations
* Modal dialogs to confirm critical actions
* Notifications for successful operations
* Detailed error messages
* Button states (loading, disabled)

### 7.3 Responsiveness

* Mobile adaptation of all components
* Touch target optimization (minimum 44px)
* Horizontal scrolling for wide tables
* Adaptive filters for mobile devices

### 7.4 Performance

* Page-by-page data loading
* Debounce for real-time search
* Optimized table updates
* Caching of reference data

## 8. Validation and Restrictions

**Data validation**

* Validation of operation amounts
* Date validation (not in the future for completed operations)
* Validation of required key fields
* Validation of uploaded file formats

**Access control**

* Role-based access for viewing, creating, editing, and deleting operations
* Access control for bank statement import functionality
* Restrictions on data export according to user permissions
