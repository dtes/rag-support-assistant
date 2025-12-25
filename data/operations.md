# Functional requirements: Operations section

## 1. General purpose

This section is intended for managing the financial operations of an organization, including viewing, creating, editing transactions, importing bank statements, and managing automatic processing rules.

##2. Section Structure

The section consists of three main tabs:
- **Transactions** - View and manage financial transactions
- **Import** - download and process bank statements
- **Rules** - setting up automatic rules for processing operations

## 3. The Operations tab

### 3.1 Viewing operations

**Displaying a list of operations**
- Operations are displayed as a table with a mobile-responsive design
- Each operation shows:
- The amount with the direction icon (arrow up for income, down for expenses)
- Date and time of the operation
- Description of the operation (edited inline)
- Tags: article, direction, counterparty (edited inline)
- Organization account
- The amounts of income are highlighted in green, expenses in red
- Support for inline editing of all fields of the operation

### 3.2 Search and filtering

**Text search**
- Search for operations by description and any text content
- The search works in real time when you type
- A search field with a search icon and the ability to clear

**Filtering by date**
- Selection of preset periods via the drop-down list
- Automatic recalculation of results when the period changes
- Displaying only transactions for the selected period

**Filtering by parameters**
- Filter by groups of operations (income, expenses, etc.) - one choice
- Filter by articles of operations - Multiple selection with search
- Filter by organization's accounts - Multiple choice with search
- Counterparty filter - multiple choice with search
- Filter by directions - Multiple choice with search
- All filters can be combined
- The ability to clean each filter separately

### 3.3 Operations Management

**Creating a new operation**
- The "Add operation" button opens the modal window
- Required fields to fill in
- Validation of data before saving
- Automatic updating of the list after creation

**Inline editing**
- The operation description is edited directly in the table when the focus is lost.
- Tags (article, direction, counterparty) are edited by click
- When clicked, a drop-down list opens with a search
- Tags can be deleted by clicking on the cross
- If there is no tag, a plus button is displayed to add it.
- Changes are saved automatically

**Deleting an operation**
- Delete button in the operation line
- Confirmation request before deletion
- Automatic updating of the list after deletion

**View transactions by operation**
- Ability to open a modal window with a list of related transactions
- Go to a detailed view of the operation

### 3.4 Exporting data

**Unloading operations**
- The "Export" button in the tab header
- Export in Excel (XLSX) format
- Export takes into account all applied filters
- Automatic file download after formation
- The file name is generated automatically

### 3.5 Pagination

**Page-by-page navigation**
- The list of operations is loaded page by page for performance
- Navigation controls at the bottom of the table
- Display of the current page
- Ability to navigate to the next/previous page
- Information about the availability of the following pages

## 4. The "Import" tab

### 4.1 Uploading Files

**File upload area**
- UploadArea component with drag & drop support
- The "Upload statement" button for selecting files
- Information about supported formats: Excel, PDF
- Prompt "Select files or just drag and drop here"

**Supported formats**
- Excel (.xls, .xlsx)
- PDF
- The ability to download multiple files at the same time

**The download process**
- Select files through the dialog or drag and drop into the area
- Automatic sending to the server after selection
- Display the download progress
- Notification of download results (success/error)
- Automatic updating of the list of statements after downloading

### 4.2 Viewing uploaded statements

**Statement table**
- A list of statements in the form of a table with columns:
  - File (file type name and icon)
- File size
  - Upload date
  - Processing status
  - Actions
- Color file icons (red for PDF, green for Excel)

**Statement statuses**
- PENDING - blue tag
- In PROCESSING - yellow tag
- Ready for mapping (READY_FOR_MAPPING) - yellow tag
- MAPPED - green tag
- IMPORTED - green tag
- ERROR - red tag

**The "No data" status**
- Displayed when there are no statements
- The message "Statements not found"
- The "Download first statement" button for quick access

### 4.3 Actions with statements

**Check-out settings**
- A button with an eye icon for viewing
- The StatementModal modal window opens
- Allows you to set up mapping and import data
- After the import, the list of operations is updated

**Deleting an extract**
- The button with the basket icon
- Confirmation request with warning
- Warning about deleting related operations
- Automatic updating of the list after deletion

**Pagination**
- Page-by-page view of statements (10 per page)
- Navigation elements at the bottom of the card
- Are displayed only if the following pages are available

## 5. The "Rules" tab

### 5.1 Purpose

**Automation of operations processing**
- Rules allow you to fill in the fields of operations automatically
- Applied based on conditions
- Simplify the processing of repetitive operations
- Have priority of execution

### 5.2 Displaying Rules

**Table of rules**
- Columns of the table:
- Drag handle to change the priority
  - Target field (which field will be filled in)
- Value (what the field will be filled in with)
- Conditions (under what conditions the rule applies)
  - Actions (edit/delete)

**Drag & Drop**
- Ability to drag and drop rules to change the priority
- Visual indication when dragging
- Automatic saving of the new order

**The "No data" status**
- Displayed when there are no rules
- The message "Rules not found"
- The "Add first rule" button

### 5.3 Creating and editing rules

**Creating a rule**
- The "Add rule" button opens the modal window
- Selection of the target field (what to fill in)
- Selecting a value to fill in
- Setting up the conditions for applying the rule
- Validation before saving

**Edit the rule**
- The edit button opens a modal window with the rule data.
- Ability to change all parameters
- Saving changes updates the list

**Deleting a rule**
- Delete confirmation button
- The query "Are you sure you want to delete this rule?"
- Automatic updating of the list after deletion

### 5.4 Conditions and Values

**Target fields**
- Operation article (CategoryID)
- Direction (directionId)
- Other fields of the operation

**Types of conditions**
- Equal to (eq)
- Not equal to (ne)
- Greater than (gt), Greater than or equal to (gte)
- Less than (lt), Less than or equal to (lte)
- Contains
- Does not contain (not_contains)
- Included in (in)

**Display of conditions**
- Conditions are shown as tags
- Format: "Value Operator field"
- For example: "Description contains 'Lease'"

### 5.5 Priority of rules

**Application procedure**
- Rules are applied from top to bottom
- The first appropriate rule is followed
- Priority change via drag & drop
- Visual indication of the current priority

## 6. Integration with directories

**Use of background information**
- The system uses reference books for:
- Articles of operations (categories)
- Directions
  - Accounts of the organization
- Counterparties
- Groups of operations
- Types of activities
- When selected, up-to-date data is displayed in the filters.
- Directories are loaded during initialization

##7. User Interface

### 7.1 Navigation
- The section consists of three tabs: "Operations", "Import", "Rules"
- Switch between tabs via tabs
- Each tab saves its own state
- The active tab is highlighted in blue

### 7.2 Feedback
- Loading indicators when performing operations
- Modal windows for confirming critical actions
- Notifications of successful operations
- Detailed error messages
- Button states (loading, disabled)

### 7.3 Adaptability
- Mobile adaptation of all components
- Optimization of touch targets (minimum 44px)
- Horizontal scrolling for wide tables
- Adaptation of filters for mobile devices

### 7.4 Performance
- Page-by-page loading of data
- Debounce for real-time search
- Optimization of table updates
- Caching of reference data

##8. Validation and Constraints

**Data validation**
- Checking the correctness of transaction amounts
- Date validation (not in the future for completed operations)
- Checking whether key fields must be filled in
- Checking the formats of uploaded files

**Access rights**
- Differentiation of rights to view, create, edit and delete operations
- Access control to the extract import function
- Restrictions on data export according to user rights