# Functional Requirements: "Reports" Section

## 1. General Purpose

The **Reports** section provides users with tools to analyze an organization’s financial data through two main reports:

* **Cash Flow Statement** — analysis of cash inflows and outflows
* **Profit and Loss (P&L) Report** — analysis of revenues, expenses, and overall financial performance

## 2. Section Structure

The section is доступен via the **Reports** dropdown in the sidebar and includes two subsections:

* Cash Flow Report (`/reports/cashflow`)
* Profit & Loss Report (`/reports/profit-loss`)

---

# PART 1: CASH FLOW REPORT

## 3. Overall Structure of the Cash Flow Report

### 3.1 Page Header

**Elements**

* Main title: **“Cash Flow Statement”**
* Subtitle: **“Analysis of cash inflows and outflows”**
* Styling: large font, bold weight

### 3.2 Report Control Panel

**Layout**

* Horizontal toolbar with controls
* All elements in a single row (n-flex)
* Responsive layout on mobile devices

**Control elements:**

1. **Period selector**

   * Dropdown with preset periods:

     * Current month
     * Last 3 months
     * Last 6 months
     * Last year
     * Custom period
   * Width: 200px
   * Automatically reloads data on change

2. **Custom period selector**

   * Shown only when **Custom period** is selected
   * Date picker with `daterange` type
   * Allows selecting start and end dates
   * Automatically refreshes data on change

3. **Period grouping**

   * Dropdown with options:

     * By days
     * By weeks
     * By months
     * By quarters
     * By years
   * Width: 200px
   * Defines how data is grouped into columns

4. **Growth display toggle**

   * Button with trend icon (`TrendingUpSharp`)
   * Type: `primary` when active, `default` when inactive
   * Tooltip: “Show growth”
   * Toggles percentage change between periods

5. **Export button**

   * Button with download icon (`DownloadOutline`)
   * Exports the current report view

6. **Fullscreen toggle**

   * Button with dynamic icon
   * “Expand” icon in normal mode
   * “Collapse” icon in fullscreen mode
   * Type: `primary` when active, `default` when inactive

### 3.3 Data Grouping

**Radio group for grouping type:**

* By categories (`category`) — default
* By directions (`direction`)
* By accounts (`account`)
* By counterparties (`counterparty`)
* By activity types (`activity_type`)

**Style**

* Radio buttons in a horizontal row
* Active option highlighted

---

## 4. Cash Flow Data Tables

### 4.1 By Category Table (`CashFlowByCategoryTable`)

**Shown when:** `groupBy === 'category'`

**Inputs:**

* `data` — report data
* `categories` — list of transaction categories
* `accounts` — list of accounts
* `periodGroupBy` — period grouping type
* `showGrowth` — whether to show growth
* `loading` — loading indicator

**Structure:**

* Grouped by transaction categories
* Columns by periods (depending on `periodGroupBy`)
* Totals per category
* Drill-down to transaction list

### 4.2 By Direction Table (`CashFlowByDirectionTable`)

**Shown when:** `groupBy === 'direction'`

**Inputs:**

* `data`
* `directions` — list of business directions
* `periodGroupBy`
* `showGrowth`
* `loading`

**Structure:**

* Grouped by business directions
* Period columns
* Totals per direction

### 4.3 By Account Table (`CashFlowByAccountTable`)

**Shown when:** `groupBy === 'account'`

**Inputs:**

* `data`
* `accounts` — list of accounts
* `periodGroupBy`
* `showGrowth`
* `loading`

**Structure:**

* Grouped by organization accounts
* Opening and closing balances
* Inflows and outflows by period

### 4.4 By Counterparty Table (`CashFlowByCounterpartyTable`)

**Shown when:** `groupBy === 'counterparty'`

**Inputs:**

* `data`
* `counterparties` — list of counterparties
* `periodGroupBy`
* `showGrowth`
* `loading`

**Structure:**

* Grouped by counterparties
* Transaction amounts with each counterparty by period

### 4.5 By Activity Type Table (`CashFlowByActivityTypeTable`)

**Shown when:** `groupBy === 'activity_type'`

**Inputs:**

* `data`
* `activityTypes` — list of activity types
* `categories` — list of categories
* `periodGroupBy`
* `showGrowth`
* `loading`

**Structure:**

* Grouped by activity types (operating, investing, financing)
* Breakdown by categories within each type
* Totals per activity type

---

## 5. Cash Flow Report Functionality

### 5.1 Drill-down to Transactions

**Purpose**

* Navigate from aggregated data to transaction details
* Clicking a table cell opens a detailed view

**Implementation**

* Opens `TransactionListModal`
* Shows all transactions contributing to the selected amount
* Filtered by selected period and category/direction/account/counterparty

### 5.2 Fullscreen Mode

**Activation**

* Click the fullscreen button
* Toggles `isFullScreen`

**UI Changes**

* Card gets `fullscreen-card` class
* Occupies full available screen
* Improved visibility for large tables

### 5.3 Report Export

**Export format**

* Excel (XLSX)
* Preserves the current report view
* Respects all applied filters and groupings

**Process**

* Click export button
* File generation on the server
* Automatic download

---

## 6. Cash Flow Data Loading and Display

### 6.1 Loading States

**Loading indicator (`isLoading`)**

* Shown while data is being fetched
* Passed to table components
* Blocks interaction with the table

### 6.2 Data Handling

**Data source**

* API endpoint for report data
* Request parameters:

  * Period (`selectedPeriod`, `dateRange`)
  * Grouping type (`groupBy`)
  * Period granularity (`periodGroupBy`)

**Data storage**

* `reportData` — main report data
* Reference lists (`categories`, `directions`, `accounts`, `counterparties`, `activityTypes`)
* Period metadata

---

# PART 2: PROFIT & LOSS (P&L) REPORT

## 7. Overall Structure of the P&L Report

### 7.1 Page Header

**Elements**

* Main title: **“Profit and Loss (P&L) Report”**
* Subtitle: **“Analysis of revenues, expenses, and financial performance”**

### 7.2 Control Panel

**Controls:**

1. **Period selector**

   * Current month
   * Previous month
   * Current quarter
   * Current year
   * Custom period
   * Automatically reloads data on change

2. **Custom period**

   * Two `date` fields (`dateFrom`, `dateTo`)
   * Separator “—”
   * Shown only when **Custom period** is selected

3. **Export button**

   * Download icon
   * Text: **“Export”**
   * Style: `btn btn-secondary`

---

## 8. Key P&L Indicators

### 8.1 Summary Card

**Display**

* Card titled **“Key Metrics”**
* Grid of 4 indicators

**Metrics:**

1. **Revenue**

   * Total income
   * Always positive (green)

2. **Gross Profit**

   * Revenue minus Cost of Sales
   * Dynamic color (green if ≥ 0, red if < 0)

3. **Operating Profit**

   * Gross profit minus Operating expenses
   * Dynamic color

4. **Net Profit**

   * Final financial result
   * Dynamic color

**Styling**

* `summary-label` — metric name
* `summary-amount` — metric value
* `positive` / `negative` classes for color

---

## 9. Detailed P&L Report

### 9.1 Report Structure

**Report sections (in order):**

1. **REVENUE**

   * List of revenue categories
   * Amount per category (green)
   * Subtotal: **“Total revenue”**

2. **COST OF SALES**

   * List of cost of sales categories
   * Amount per category (red)
   * Subtotal: **“Total cost of sales”**

3. **GROSS PROFIT** (highlighted)

   * Calculation: Revenue − Cost of Sales
   * Large font, highlighted background
   * Dynamic color

4. **OPERATING EXPENSES**

   * List of operating expense categories
   * Amount per category (red)
   * Subtotal: **“Total operating expenses”**

5. **OPERATING PROFIT** (highlighted)

   * Calculation: Gross profit − Operating expenses
   * Large font, highlighted background
   * Dynamic color

6. **OTHER INCOME AND EXPENSES**

   * Mixed list (income and expenses)
   * Dynamic color per line
   * Subtotal with net value

7. **NET PROFIT** (final section)

   * Final calculation
   * Maximum emphasis
   * Dynamic color

### 9.2 Report Row Display

**Row types:**

* `report-row` — regular row
* `report-row subtotal` — subtotal row
* `report-row total` — total row

**Row content:**

* `report-description` — description (category name)
* `report-amount` — amount

  * `positive` — green
  * `negative` — red

### 9.3 Highlighted Sections

**Styling classes:**

* `report-section highlight`
* Used for gross and operating profit
* Special visual emphasis

---

## 10. P&L Data Loading

### 10.1 Loading States

**Loading indicator**

* `BaseCard` with `loading-card` class
* Spinner and text **“Loading data…”**
* Shown while `isLoading === true`

### 10.2 Data Source

**Data structure:**

* `revenues[]`
* `costOfSales[]`
* `operatingExpenses[]`
* `otherIncomeExpenses[]`

**Calculated metrics:**

* `totalRevenues`
* `totalCostOfSales`
* `grossProfit`
* `totalOperatingExpenses`
* `operatingProfit`
* `totalOtherIncomeExpenses`
* `netProfit`

---

## 11. Common Functions

### 11.1 Currency Formatting

**`formatCurrency()` function**

* Locale: `ru-RU`
* Minimum fraction digits: 0
* Maximum fraction digits: 0
* Thousands separators
* Currency: ₸ (Kazakhstani tenge)

**Examples:**

* `1500000` → **“1 500 000 ₸”**
* `-250000` → **“-250 000 ₸”**

### 11.2 Report Export

**For P&L:**

* **Export** button
* Format: Excel
* Includes all report sections
* Preserves formatting (colors, totals)

---

## 12. Responsiveness

### 12.1 Desktop

**Cash Flow:**

* All filters in one row
* Full-size tables
* All period columns visible

**P&L:**

* Metrics grid 2×2
* Wide report sections
* All elements visible

### 12.2 Mobile Devices

**Cash Flow:**

* Filters wrap to multiple rows
* Horizontal table scrolling
* Simplified period display

**P&L:**

* Metrics in a single column (1×4)
* Compact report sections
* Responsive font sizes

---

## 13. Performance

**Optimizations:**

* Lazy loading of tables
* Caching of reference data
* Conditional component rendering (`v-if`)
* Debouncing on filter changes
* Virtualization for large tables

---

## 14. Error Handling

**On load error:**

* Error message displayed
* Retry option
* Logging to console

**When no data is available:**

* Empty table with message
* Suggestion to change the period
* Link to create transactions

---
