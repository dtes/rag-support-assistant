# Functional requirements: The "Reference Books" section

## 1. General purpose

The Directories section provides users with the ability to manage reference information used in financial transactions and reports. It includes the management of accounts, transaction items, destinations, and counterparties.

##2. Section Structure

The section is accessible via the "Directories" drop-down menu in the sidebar with four subsections.:
- **Business Accounts** (/references/accounts)
- **Articles of operations** (/references/categories)
- **Directions** (/references/directions)
- **Counterparties** (/references/counterparts)

---

# PART 1: BUSINESS ACCOUNTS

## 3. General structure

### 3.1 Page Title

**Elements**
- Heading: "Business Accounts"
- The "Add account" button with a plus sign
- Button type: primary (blue)

**Location**
- Headline on the left
- The button on the right
- Vertical alignment in the center

### 3.2 Invoice table

**Component**
- n-data-table from Naive UI
- With borders (bordered: true)
- Row key: account ID

**Table columns:**

1. **Name**
   - Key: name
- Style: bold (FontWeight: 500)
- Basic account information

2. **Account number**
   - Key: num
- The account number is displayed
   - If missing: "—"
- For example: IBAN, card number

3. **Account type**
- Key: type
   - Displays the name of the account type
   - It is obtained from the accountTypes directory
   - Examples: Checking account, Cash register, Card

4. **Currency**
- Key: currency
   - Displays the currency code
- Examples: KZT, USD, EUR

5. **Actions**
- Width: 120px
   - Two buttons:
- Edit (pencil icon)
- Delete (trash icon)
   - Buttons of the size small, quaternary, round

##4. Account Management

### 4.1 Creating an account

**Initiation**
- Click on the "Add account" button
- The AccountModal modal window opens
- Mode: create

**Required fields:**
- Account name
- Account type (selected from the directory)
- Currency

**Optional fields:**
- Account number
- Description
- Initial balance

**After creation:**
- The modal window is closing
- The list of accounts is updated
- A new account appears in the table

### 4.2 Account Editing

**Initiation**
- Click on the edit button in the invoice line
- The AccountModal modal window opens
- Mode: update
- The fields are filled with current data

**Features:**
- Changing all account fields
- Data validation
- Saving changes

**After editing:**
- The modal window is closing
- The list of accounts is updated
- The changes are reflected in the table

### 4.3 Deleting an account

**Initiation**
- Click on the delete button in the invoice line
- popconfirm appears with confirmation
- Text: "Delete account \"{account name}\"?"

**Confirmation:**
- The "Yes" button - performs the deletion
- The "No" button cancels the operation

**After removal:**
- The account is deleted from the system
- The list is being updated
- The score disappears from the table

**Restrictions:**
- You cannot delete an account if there are related transactions.
- An error message is displayed

##5. Uploading data

### 5.1 Reference Books

**Downloadable reference books:**
- accountTypes - account types
- currencies - currencies

**Usage:**
- For display in the table
- For selection when creating/editing

### 5.2 Load indication

**Spinner**
- The n-spin component
- Shown while loading === true
- Covers the entire table

---

# PART 2: ARTICLES OF OPERATIONS

## 6. General structure

### 6.1 Page Title

**Elements**
- Headline: "Articles of operations"
- The "Add article" button with a plus sign
- Button type: primary

### 6.2 Grouping by operation type

**Display**
- Articles are grouped by operation groups
- Each group has a heading:
- "Income"
- "Expenses"
- "Transfers"
- etc.

**Structure:**
- groupedCategories - calculated property
- Groups categories by the group field
- Each group contains an array of articles

### 6.3 Tables of articles

**For each group:**
- Separate n-data-table
- Group header above the table
- With borders (bordered: true)

**Table columns:**

1. **Name**
   - Key: name
- Style: bold (FontWeight: 500)
is the title of the article.

2. **Description**
   - Key: description
   - If missing: "—"
- Explanation of the article

3. **Type of activity**
- Key: type
   - Displayed as an n-tag
- Type: info, size: small
- Examples: Operational, Investment, Financial

4. **Actions**
- Width: 120px
   - Edit and delete buttons
   - Disabled buttons for system articles (isSystem: true)

##7. Article Management

### 7.1 Creating an Article

**Initiation**
- Click on the "Add Article"
button - The CategoryModal modal window opens
- Mode: create

**Required fields:**
- The title of the article
- Group of operations (income/expenses/etc.)
- Type of activity

**Optional fields:**
- Description

**After creation:**
- The modal window is closing
- The list of articles is updated
- A new article appears in the corresponding group

### 7.2 Editing an article

**Initiation**
- Click on the edit button
- The CategoryModal modal window opens
- Mode: update
- The fields are filled with current data

**Restrictions:**
- System articles cannot be edited (disabled button)

**After editing:**
- The list is being updated
- The changes are reflected in the table

### 7.3 Deleting an article

**Initiation**
- Click on the delete button
- Popconfirm: "Delete the article \"{title}\"?"

**Restrictions:**
- Cannot delete system articles (disabled button)
- Cannot delete articles with operations

**After removal:**
- The article is being deleted
- The list is being updated

##8. Uploading article data

### 8.1 Reference Books

**Downloadable data:**
- transactionGroups - groups of operations
- activityTypes - types of activities
- categories - the articles themselves

**Download sequence:**
1. Loading activities
2. Loading groups of operations
3. Uploading articles

### 8.2 Processing system articles

**System articles:**
- isSystem field: true
- You can't edit it
- Cannot be deleted
- Disabled action buttons

---

# PART 3: DIRECTIONS

## 9. General structure

### 9.1 Page Title

**Elements**
- Heading: "Directions"
- The "Add direction" button with a plus sign
- Button type: primary

### 9.2 Direction table

**Component**
- n-data-table
- With frames
- Row key: id

**Table columns:**

1. **Name**
   - Key: name
- Style: bold
   - Name of the business line

2. **Description**
   - Key: description
   - If missing: "—"
- Explanation of the direction

3. **Actions**
   - Width: 120px
   - Edit and delete buttons
   - Size: small, quaternary

## 10. Direction management

### 10.1 Creating a Direction

**Initiation**
- Click on the "Add direction" button
- The DirectionModal modal window opens
- Mode: create

**Fields:**
- Name (required)
- Description (optional)

**After creation:**
- The list is being updated
- New direction in the table

### 10.2 Editing the direction

**Initiation**
- Click on the edit button
- DirectionModal opens
- Mode: update

**After editing:**
- Changes are saved
- The table is being updated

### 10.3 Removing a direction

**Initiation**
- Click on the delete button
- Popconfirm with confirmation

**Restrictions:**
- You can't delete a referral with operations

**After removal:**
- The direction is being removed
- The list is being updated

---

# PART 4: COUNTERPARTIES

## 11. General structure

### 11.1 Page Title

**Elements**
- Heading: "Counterparties"
- "Add counterparty" button with a plus sign
- Button type: primary

### 11.2 Counterparty Table

**Component**
- n-data-table
- With frames
- Row key: id

**Table columns:**

1. **Name**
   - Key: name
   - Style: bold
   - Name of the organization/sole proprietor/individual

2. **BIN/IIN**
   - Key: bin
- If missing: "—"
- Identification number

3. **Type**
   - Key: type
   - Tag (n-tag)
- Values: Organization, sole proprietor, Individual

4. **Contact information**
- Phone, email
   - If missing: "—"

5. **Actions**
- Width: 120px
   - Edit and delete buttons

## 12. Managing counterparties

### 12.1 Creating a Counterparty

**Initiation**
- Click on the "Add counterparty" button
- The Counterpart modal window opens
- Mode: create

**Required fields:**
- Name

**Optional fields:**
- BIN/IIN
- Type of counterparty
- Phone number
- Email
- Address
- Description

**After creation:**
- The list is being updated
- New counterparty in the table

### 12.2 Editing the Counterparty

**Initiation**
- Click on the edit button
- The counterparymodal opens
- Mode: update
- The fields are filled with data

**After editing:**
- Changes are saved
- The table is being updated

### 12.3 Removing a counterparty

**Initiation**
- Click on the delete button
- Popconfirm: "Delete counterparty \"{name}\"?"

**Restrictions:**
- You cannot delete a counterparty with transactions

**After removal:**
- The counterparty is being deleted
- The list is being updated

---

# COMMON FUNCTIONS

## 13. Modal windows

### 13.1 Structure of modal windows

**Common elements:**
- Title (creation/editing)
- A form with fields
- "Save" and "Cancel" buttons
- Download indication when saving

**Modes:**
- create - create a new record
- update - edit an existing one

### 13.2 Validation

**Checks:**
- Required fields must be filled in
- Correctness of the data format (email, phone, BIN/IIN)
- Uniqueness (where required)

**Error display:**
- Highlighting incorrect fields in red
- Text error messages
- Lock the "Save" button in case of errors

### 13.3 Saving data

**The process:**
1. Form validation
2. Sending data to the server
3. Response processing
4. Closing the modal window
5. Updating the list

**In case of an error:**
- The modal window remains open
- An error message is displayed
- The user can correct the data

##14. Error Handling

###14.1 Download Errors

**If there is a data upload error:**
- Error message ($message.error)
- Error text from the server response
- The possibility of a second attempt

###14.2 Saving Errors

**If there is a creation/editing error:**
