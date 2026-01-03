# Functional Requirements: “Reference Data” Section

## 1. General Purpose

The **“Reference Data”** section allows users to manage reference information used in financial operations and reports. It includes management of business accounts, transaction categories, directions, and counterparties.

## 2. Section Structure

The section is доступен via a dropdown menu **“Reference Data”** in the sidebar and contains four subsections:

* **Business Accounts** (/references/accounts)
* **Transaction Categories** (/references/categories)
* **Directions** (/references/directions)
* **Counterparties** (/references/counterparties)

---

# PART 1: BUSINESS ACCOUNTS

## 3. General Structure

### 3.1 Page Header

**Elements**

* Title: “Business Accounts”
* “Add Account” button with plus icon
* Button type: primary (blue)

**Layout**

* Title on the left
* Button on the right
* Vertically center-aligned

### 3.2 Accounts Table

**Component**

* `n-data-table` from Naive UI
* Bordered: true
* Row key: account id

**Table Columns:**

1. **Name**

   * Key: `name`
   * Style: semi-bold (fontWeight: 500)
   * Main account information

2. **Account Number**

   * Key: `num`
   * Displays the account number
   * If missing: “—”
   * e.g., IBAN, card number

3. **Account Type**

   * Key: `type`
   * Displays the account type name
   * Taken from the `accountTypes` reference
   * Examples: Checking account, Cash, Card

4. **Currency**

   * Key: `currency`
   * Displays the currency code
   * Examples: KZT, USD, EUR

5. **Actions**

   * Width: 120px
   * Two buttons:

     * Edit (pencil icon)
     * Delete (trash icon)
   * Size: small, quaternary, round

## 4. Account Management

### 4.1 Create Account

**Initiation**

* Click the “Add Account” button
* Opens `AccountModal`
* Mode: `create`

**Required fields:**

* Account name
* Account type (from reference list)
* Currency

**Optional fields:**

* Account number
* Description
* Opening balance

**After creation:**

* Modal closes
* Account list refreshes
* New account appears in the table

### 4.2 Edit Account

**Initiation**

* Click Edit in the account row
* Opens `AccountModal`
* Mode: `update`
* Fields prefilled

**Capabilities:**

* Edit all account fields
* Data validation
* Save changes

**After editing:**

* Modal closes
* List refreshes
* Changes appear in the table

### 4.3 Delete Account

**Initiation**

* Click Delete in the account row
* A popconfirm appears
* Text: *“Delete account ‘{account name}’?”*

**Confirmation:**

* “Yes” — perform deletion
* “No” — cancel

**After deletion:**

* Account is removed from the system
* List refreshes
* Account disappears from the table

**Restrictions:**

* An account cannot be deleted if it has related transactions
* An error message is shown

## 5. Data Loading

### 5.1 Reference Lists

**Loaded references:**

* `accountTypes` — account types
* `currencies` — currencies

**Usage:**

* For table display
* For selection in create/edit forms

### 5.2 Loading Indicator

**Spinner**

* `n-spin` component
* Shown while `loading === true`
* Covers the entire table

---

# PART 2: TRANSACTION CATEGORIES

## 6. General Structure

### 6.1 Page Header

**Elements**

* Title: “Transaction Categories”
* “Add Category” button with plus icon
* Button type: primary

### 6.2 Grouping by Transaction Types

**Display**

* Categories are grouped by transaction groups
* Each group has a header:

  * “Income”
  * “Expenses”
  * “Transfers”
  * etc.

**Structure:**

* `groupedCategories` — computed property
* Groups `categories` by the `group` field
* Each group contains an array of categories

### 6.3 Category Tables

**For each group:**

* Separate `n-data-table`
* Group header above the table
* Bordered: true

**Table Columns:**

1. **Name**

   * Key: `name`
   * Style: semi-bold
   * Category name

2. **Description**

   * Key: `description`
   * If missing: “—”
   * Category description

3. **Activity Type**

   * Key: `type`
   * Displayed as a tag (`n-tag`)
   * Type: info, size: small
   * Examples: Operating, Investing, Financing

4. **Actions**

   * Width: 120px
   * Edit and Delete buttons
   * Disabled for system categories (`isSystem: true`)

## 7. Category Management

### 7.1 Create Category

**Initiation**

* Click “Add Category”
* Opens `CategoryModal`
* Mode: `create`

**Required fields:**

* Category name
* Transaction group (income/expenses/etc.)
* Activity type

**Optional fields:**

* Description

**After creation:**

* Modal closes
* Category list refreshes
* New category appears in the corresponding group

### 7.2 Edit Category

**Initiation**

* Click Edit
* Opens `CategoryModal`
* Mode: `update`
* Fields prefilled

**Restrictions:**

* System categories cannot be edited (button disabled)

**After editing:**

* List refreshes
* Changes appear in the table

### 7.3 Delete Category

**Initiation**

* Click Delete
* Popconfirm: *“Delete category ‘{name}’?”*

**Restrictions:**

* System categories cannot be deleted (button disabled)
* Categories with transactions cannot be deleted

**After deletion:**

* Category is removed
* List refreshes

## 8. Loading Category Data

### 8.1 References

**Loaded data:**

* `transactionGroups` — transaction groups
* `activityTypes` — activity types
* `categories` — categories

**Loading sequence:**

1. Load activity types
2. Load transaction groups
3. Load categories

### 8.2 System Categories Handling

**System categories:**

* Field `isSystem: true`
* Cannot be edited
* Cannot be deleted
* Action buttons disabled

---

# PART 3: DIRECTIONS

## 9. General Structure

### 9.1 Page Header

**Elements**

* Title: “Directions”
* “Add Direction” button with plus icon
* Button type: primary

### 9.2 Directions Table

**Component**

* `n-data-table`
* Bordered
* Row key: `id`

**Table Columns:**

1. **Name**

   * Key: `name`
   * Style: semi-bold
   * Business direction name

2. **Description**

   * Key: `description`
   * If missing: “—”
   * Direction description

3. **Actions**

   * Width: 120px
   * Edit and Delete buttons
   * Size: small, quaternary

## 10. Direction Management

### 10.1 Create Direction

**Initiation**

* Click “Add Direction”
* Opens `DirectionModal`
* Mode: `create`

**Fields:**

* Name (required)
* Description (optional)

**After creation:**

* List refreshes
* New direction appears in the table

### 10.2 Edit Direction

**Initiation**

* Click Edit
* Opens `DirectionModal`
* Mode: `update`

**After editing:**

* Changes are saved
* Table refreshes

### 10.3 Delete Direction

**Initiation**

* Click Delete
* Popconfirm for confirmation

**Restrictions:**

* Directions with transactions cannot be deleted

**After deletion:**

* Direction is removed
* List refreshes

---

# PART 4: COUNTERPARTIES

## 11. General Structure

### 11.1 Page Header

**Elements**

* Title: “Counterparties”
* “Add Counterparty” button with plus icon
* Button type: primary

### 11.2 Counterparties Table

**Component**

* `n-data-table`
* Bordered
* Row key: `id`

**Table Columns:**

1. **Name**

   * Key: `name`
   * Style: semi-bold
   * Organization / sole proprietor / individual name

2. **BIN/IIN**

   * Key: `bin`
   * If missing: “—”
   * Identification number

3. **Type**

   * Key: `type`
   * Tag (`n-tag`)
   * Values: Organization, Sole Proprietor, Individual

4. **Contact Information**

   * Phone, email
   * If missing: “—”

5. **Actions**

   * Width: 120px
   * Edit and Delete buttons

## 12. Counterparty Management

### 12.1 Create Counterparty

**Initiation**

* Click “Add Counterparty”
* Opens `CounterpartyModal`
* Mode: `create`

**Required fields:**

* Name

**Optional fields:**

* BIN/IIN
* Counterparty type
* Phone
* Email
* Address
* Description

**After creation:**

* List refreshes
* New counterparty appears in the table

### 12.2 Edit Counterparty

**Initiation**

* Click Edit
* Opens `CounterpartyModal`
* Mode: `update`
* Fields prefilled

**After editing:**

* Changes are saved
* Table refreshes

### 12.3 Delete Counterparty

**Initiation**

* Click Delete
* Popconfirm: *“Delete counterparty ‘{name}’?”*

**Restrictions:**

* Counterparties with transactions cannot be deleted

**After deletion:**

* Counterparty is removed
* List refreshes

---

# COMMON FEATURES

## 13. Modals

### 13.1 Modal Structure

**Common elements:**

* Title (create/edit)
* Form with fields
* “Save” and “Cancel” buttons
* Loading indicator while saving

**Modes:**

* `create` — create new record
* `update` — edit existing record

### 13.2 Validation

**Checks:**

* Required fields must be filled
* Correct data formats (email, phone, BIN/IIN)
* Uniqueness where required

**Error display:**

* Highlight invalid fields in red
* Text error messages
* Disable “Save” button when errors exist

### 13.3 Saving Data

**Process:**

1. Validate form
2. Send data to the server
3. Handle response
4. Close modal
5. Refresh list

**On error:**

* Modal remains open
* Error message is shown
* User can correct data

## 14. Error Handling

### 14.1 Load Errors

**When loading fails:**

* Error message (`$message.error`)
* Error text from server response
* Ability to retry

### 14.2 Save Errors

**When create/edit fails:**

* Error message in modal
* Error details
* Modal remains open

### 14.3 Delete Errors

**When delete fails:**

* Error message
* Reason (e.g., related transactions exist)
* Record remains in the list

## 15. Loading Indicators

### 15.1 List Loading

**`n-spin` component:**

* Covers the entire table
* Shown when `loading === true`
* Blocks interaction

### 15.2 Saving Loading

**In modals:**

* “Save” button shows loading state
* Text changes to “Saving…”
* Button becomes disabled

## 16. Responsiveness

### 16.1 Desktop

**Tables:**

* All columns visible
* Convenient action buttons
* Full-size modals

### 16.2 Tablet and Mobile

**Tables:**

* Horizontal scroll for wide tables
* Adaptive button sizes (min 44px)
* Column optimization (hide less important ones)

**Modals:**

* Full-screen on mobile
* Adaptive form field sizes
* Vertical button layout

## 17. Performance

**Optimizations:**

* Lazy loading of reference data
* Caching loaded data
* Optimized rendering of large lists
* Debounce on search (if applicable)

## 18. Access Control

**Permissions:**

* View reference data
* Create records
* Edit records
* Delete records

**UI behavior:**

* Hide buttons when no permission
* Disabled state for unavailable actions
* Messages about insufficient permissions
