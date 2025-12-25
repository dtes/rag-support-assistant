# FinApp Functional Requirements

This documentation contains a detailed description of the functional requirements for all sections of the FinApp application.

## Documentation structure

### 1. [Operations](./operations.md )
**Description:** Managing financial transactions, importing bank statements, and setting up automatic processing rules.

**Main functions:**
- View, create, and edit operations
- Inline-editing of operation fields
- Search and filtering by multiple parameters
- Import of bank statements (Excel, PDF)
- Management of automatic processing rules with Drag & Drop priorities
- Export operations to Excel

**Key Features:**
- 3 tabs: Operations, Import, Rules
- Page-by-page loading of data
- Mobile adaptation with inline editing

---

### 2. [Dashboard](./dashboard.md )
**Description:** Visual overview of the financial condition of the business with key metrics and analytics.

**Main components:**
- Filter the period (current month, 3 months, year)
- KPI metrics: Income, Expenses, Balance
- Pie charts of income and expenses
- Switching the grouping (by articles / by directions)

**Key Features:**
- "No data" status with calls to action
- Dynamic formatting of amounts
- Adaptive grid of metrics and charts

---

### 3. [Reports](./reports.md )
**Description:** Two main financial statements - DDS and OPI.

#### DDS (Cash Flow) Report
- Grouping: by articles, directions, accounts, counterparties, types of activity
- Periodicity: by day, week, month, quarter, year
- Drill-down to transactions
- Full-screen mode
- Increase display

#### OPiU (Profit and Loss) Report
- Key indicators: Revenue, Gross profit, Operating profit, Net profit
- Detailed structure: Income, Cost, Operating expenses, Other income/expenses
- Dynamic color selection

**General functions:**
- Period selection
- Export to Excel
- Formatting the currency

---

### 4. [Reference Books](./references.md )
**Description:** Application reference information management.

**Sections:**

#### Business Accounts
- Name, account number, account type, currency
- CRUD operations
- Validation upon deletion (verification of related operations)

#### Articles of operations
- Grouping by transaction type (income, expenses, transfers)
- Name, description, type of activity
- System articles (cannot be edited/deleted)

#### Directions
- Business lines
- Name, description
- CRUD operations

#### Counterparties
- Name, BIN/IIN, type, contact information
- CRUD operations
- Protection against deletion in the presence of operations

**General functions:**
- Modal windows for creating/editing
- Data validation
- Confirmation of deletion (Popconfirm)
- Loading indication

---

### 5. [Organization](./workspace.md )
**Description:** Workspace and participant management.

#### Workspace Information
- Name, Description, BIN
- Date of creation
- Viewing/editing mode
- Validation of changes

#### Participant management
- A list of participants with avatars and initials
- Access Levels: Owner, Administrator, User, View Only
- Positions
- Inviting new participants
- Changing roles
- Removal of participants

**Access rights:**
- canEditWorkspace - edit information
- canInviteMembers - invite participants
- canManageMembers - member management

**Restrictions:**
- You can't delete the owner
- You can't delete yourself
- You cannot delete a single administrator

---

### 6. [Profile](./profile.md )
**Description:** Personal data management and account security.

#### Personal information
- An avatar with initials
- First name, last name, email, phone number
- Viewing/editing mode
- Validation of fields (required fields, email/phone format)
- Undo changes with recovery from backup

#### Security

**Two-factor authentication (2FA):**
- Status indicator (enabled/disabled)
- On/off button
- Setup via authenticator app
- Code requirement when disabling

**Password change:**
- ChangePasswordModal modal window
- Fields: current password, new password, confirmation
- Password complexity validation:
- Minimum 8 characters
  - Uppercase and lowercase letters
  - Numbers
  - Special characters
- Possible exit from all sessions

---

## General principles

### Adaptability
All sections are adapted for:
- **Desktop** (> 768px): full functionality, multi-column grids
- **Tablet** (480px - 768px): adaptive grids, optimized elements
- **Mobile** (< 480px): single-column layouts, enlarged buttons (minimum 44px), full-screen modal windows

### Error handling
- Modal windows with detailed error descriptions
- Validation on the client before sending to the server
- Possibility to try again in case of errors
- Saving the entered data in case of errors

### Loading indication
- Spinners when loading data (n-spin)
- Loading the state of the buttons when performing operations
- Blocking interaction during loading

### Data validation
- Checking required fields
- Validation of formats (email, phone, BIN/IIN)
- Check for uniqueness (where required)
- Highlighting errors in red
- Text error messages

### Confirmation of actions
- Popconfirm for deleting records
- Modal windows for critical operations
- Warnings about the consequences of actions
- The ability to cancel operations

### Performance
- Page-by-page loading of data
- Caching of directories
- Lazy loading of components
- Debounce for real-time search
- Optimization of rendering of large lists

### Formatting
- **Numbers:** thousand separators, ru-RU locale
- **Currency:** format "1,000,000 ₸"
- **Dates:** DD.MM.YYYY or localized format
- **Percentages:** indicating the ± sign for changes

### Access rights
- Differentiation of rights at the UI level
- Hiding/deactivating unavailable functions
- Checking rights before critical operations
- Notifications of insufficient rights

---

## UI Technology Stack

- **Framework:** Vue 3 (Composition API / Options API)
- **UI library:** Naive UI (n-card, n-button, n-input, n-table, n-select, etc.)
- **Icons:** Vicons (ionicons5)
- **Date formatting:** embedded JavaScript methods
- **Validation of forms:** Built-in Naive UI validation
- **Modal windows:** custom modal system
- **Styles:** SCSS with CSS variables

---

## Navigation

All sections are accessible via the side menu (AppSidebar):
- Dashboard
- Operations
- Reports ▸
- DDS Report
- OPiU Report
- Reference books ▸
- Business accounts
  - Articles of operations
- Directions
  - Counterparties
- Organization
- Profile (via UserAccountDropdown in the header)

---

## Additional information

For more detailed information on each section, please refer to the relevant documentation files.

**Date of last update:** December 22, 2024