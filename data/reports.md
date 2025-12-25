# Functional requirements: Reports section

## 1. General purpose

The Reports section provides users with tools to analyze an organization's financial data through two main reports.:
- **Cash Flow Statement (DDS)** - analysis of cash receipts and expenditures
- **Income Statement (OPI)** - analysis of income, expenses and financial performance

##2. Section Structure

The section is accessible via the "Reports" drop-down menu in the sidebar with two subsections.:
- DDS report (/reports/cashflow)
- OPiU report (/reports/profit-loss)

---

# PART 1: CASH FLOW STATEMENT (DDS)

## 3. General structure of the DDS report

### 3.1 Page Title

**Elements**
- Main title: "Cash Flow Statement"
- Subtitle: "Cash flow and expenditure analysis"
- Stylization: large font, bold

### 3.2 Report Control Panel

**Location**
- Horizontal panel with controls
- All elements in one row (n-flex)
- Adaptive location on mobile devices

**Control Panel elements:**

1. **Period selector**
   - A drop-down list with preset periods:
     - For the current month
     - For 3 months
     - For half a year
     - For the year
     - For any period
- Width: 200px
   - When selected, the data is automatically loaded

2. **Arbitrary period selection**
- Appears only when selecting "For any period"
- The date picker component with the "daterange" type
- Allows you to select the start and end date
   - When the data is changed, it is automatically updated

3. **Grouping by period**
- Drop-down list with options:
     - By day
     - By week
     - By month
     - By block
     - By year
   - Width: 200px
   - Defines how the data will be grouped in columns

4. **Increment display switch**
- Trend icon button (TrendingUpSharp)
- Type: primary when active, default when inactive
   - Hint: "Show increment"
- Switches the percentage change display between periods

5. **Export button**
- Download icon button (DownloadOutline)
   - Exports the current report

6. **Switch to full-screen mode**
   - A button with a dynamic icon
- The "expand" icon in the normal mode
   - Collapse icon in fullscreen mode
- Type: primary when active, default when inactive

### 3.3 Grouping data

**Radio group for selecting the grouping type:**
- By articles (category) - by default
- By directions (direction)
- By accounts (account)
- By counterparty
- By type of activity (activity_type)

**Style**
- Radio buttons in a horizontal row
- The active option is highlighted in color

## 4. DDS Data Tables

### 4.1 Table by articles (CashFlowByCategoryTable)

**Displayed when:** groupBy === 'category'

**Input parameters:**
- data - report data
- categories - list of operation items
- accounts - list of accounts
- periodGroupBy - type of grouping by period
- showGrowth - whether to show an increase
- loading - loading indicator

**Structure:**
- Grouping by items of operations
- Columns with periods (depend on periodGroupBy)
- Totals by items
- The ability to drill-down to the list of transactions

### 4.2 Referral Table (CashFlowByDirectionTable)

**Displayed when:** groupBy === 'direction'

**Input parameters:**
- data - report data
- directions - list of directions
- periodGroupBy - type of grouping by period
- showGrowth - whether to show an increase
- loading - loading indicator

**Structure:**
- Grouping by business lines
- Columns with periods
- Totals by destination

### 4.3 Account Table (CashFlowByAccountTable)

**Displayed when:** groupBy === 'account'

**Input parameters:**
- data - report data
- accounts - list of accounts
- periodGroupBy - type of grouping by period
- showGrowth - whether to show an increase
- loading - loading indicator

**Structure:**
- Grouping by organization accounts
- Balances at the beginning and end of the period
- Income and expenses by period

### 4.4 Counterparty Table (CashFlowByCounterpartyTable)

**Displayed when:** groupBy === 'counterparty'

**Input parameters:**
- data - report data
- counterparties - list of counterparties
- periodGroupBy - type of grouping by period
- showGrowth - whether to show an increase
- loading - loading indicator

**Structure:**
- Grouping by counterparties
- Amounts of transactions with each counterparty by period

### 4.5 Table by type of activity (CashFlowByActivityTypeTable)

**Displayed when:** groupBy === 'activity_type'

**Input parameters:**
- data - report data
- activityTypes - list of activities
- categories - list of articles
- periodGroupBy - type of grouping by period
- showGrowth - whether to show an increase
- loading - loading indicator

**Structure:**
- Grouping by type of activity (operational, investment, financial)
- Details by articles within each type
- Results by type of activity

## 5. Functionality of the DDS report

### 5.1 Drill-down to transactions

**Purpose**
- Ability to switch from aggregated data to a list of operations
- Clicking on a table cell opens a detailed view

**Implementation**
- The TransactionListModal modal window opens
- All transactions that make up a given amount are shown
- Filtering by selected period, article/direction/account/counterparty

### 5.2 Full-screen mode

**Activation**
- Click on the fullscreen mode button
- The isf fullscreen variable is toggled

**Changes to the UI**
- The card gets the 'fullscreen-card' class
- Takes up the entire available screen
- Improved visibility for large tables

### 5.3 Exporting the report

**Export format**
- Excel (XLSX)
- Saves the current report view
- Takes into account all applied filters and dimensions

**The process**
- Click on the export button
- File generation on the server
- Automatic download

## 6. Loading and displaying DDS data

### 6.1 Download Status

**Loading indicator (isLoading)**
- Displayed during data acquisition
- Passed to the components of the tables
- Blocks interaction with the table

### 6.2 Data processing

**Data source**
- endpoint API for uploading report data
- Query parameters:
- Period (selectedPeriod, dateRange)
- Type of grouping (groupBy)
- Frequency (periodGroupBy)

**Data storage**
- ReportData - the main data of the report
- Directories (categories, directions, accounts, partnerships, activityTypes)
- Metadata of periods

---

# PART 2: INCOME STATEMENT (OPI)

## 7. The general structure of the OPI report

### 7.1 Page Title

**Elements**
- Main heading: "Income Statement (OPI)"
- Subtitle: "Analysis of income, expenses and financial performance"

### 7.2 Control Panel

**Controls:**

1. **Period selector**
- Current month
   - Last month
   - Current quarter
   - The current year
is an arbitrary period
   - When the data is changed, it is automatically reloaded

2. **Any period**
   - Two date fields (DateFrom, DateTo)
- Separator "—"
- Appears only when "Any period" is selected

3. **Export button**
- Download icon
   - Text "Export"
- Style: btn btn-secondary

## 8. Key indicators of OPI

### 8.1 Key Indicators Card

**Display**
- A card with the heading "Key indicators"
- A grid of 4 indicators

**Indicators:**

1. **Revenue**
   - Total amount of income
   - Always a positive value (green)

2. **Gross profit**
   - Revenue minus Cost
   - Dynamic color (green if >= 0, red if < 0)

3. **Operating Profit**
- Gross profit minus Operating Expenses
- Dynamic color

4. **Net profit**
- The final financial result
   - Dynamic color

**Stylization**
- summary-label - the name of the indicator
- summary-amount - indicator value
- Positive/negative classes for color selection

## 9. Detailed OPiU Report

### 9.1 Report Structure

**Report sections (sequentially):**

1. **INCOME**
   - List of income items
   - The amount for each item (green)
   - The "Total income" subtotal

2. **COST**
- List of cost items
   - The amount for each item (red)
- The "Total cost" subtotal

3. **GROSS PROFIT** (highlighted section)
- Calculation: Income - Cost
   - Large font, background highlighting
- Dynamic color

4. **OPERATING EXPENSES**
   - List of operating expenses
   - The amount for each item (red)
- The "Total operating expenses" subtotal

5. **OPERATING PROFIT** (highlighted section)
- Calculation: Gross profit - Operating expenses
- Large font, background highlighting
   - Dynamic color

6. **OTHER INCOME AND EXPENSES**
   - Mixed list (income and expenses)
   - Dynamic color for each position
   - A subtotal with the total value

7. **NET PROFIT** (final section)
- Final calculation
- Maximum allocation
   - Dynamic color

### 9.2 Displaying report lines

**Row structure:**
- report-row - regular row
- report-row subtotal - row of the subtotal
- report-row total - total row

**Line content:**
- report-description - description (title of the article)
- report-amount - amount
  - positive - green color
  - negative - red color

### 9.3 Highlighted sections

**Styling classes:**
- report-section highlight - highlighted section
- Used for gross and operating profit
- Special visual design

## 10. Uploading OPI data

### 10.1 Download Status

**Loading indicator**
- BaseCard with the loading-card class
- The spinner and the text "Loading data..."
are displayed while isLoading === true

###10.2 Data Source

**Data structure:**
- revenues[] - revenue
- costOfSales[] - cost price
- operatingExpenses[] - operating expenses
- otherIncomeExpenses[] - other income/expenses

**Calculated indicators:**
- totalRevenues - amount of income
