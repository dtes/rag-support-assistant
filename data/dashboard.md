# Functional Requirements: "Dashboard" Section

## 1. General Purpose

The dashboard provides the user with a visual overview of the business’s financial health, showing key metrics and analytics for the selected period.

## 2. Core Components

### 2.1 Header and Filters

**Page header**

* Displays the title “Dashboard” in the application header
* Subtitle “Business Overview” on the page itself

**Period filter**

* Dropdown selector to choose the analysis period:

  * Current month
  * 3 months
  * Year
* Automatically reloads data when the period changes
* Selector width: 200px

### 2.2 “No Data” State

**Display when there are no operations**

* Shown when there are no financial operations for the selected period
* Card with centered content:

  * Icon 📊
  * Title “No data for the selected period”
  * Explanatory text with recommendations
  * Two action buttons:

    * “📥 Import data” — navigate to /operations?tab=import
    * “➕ Add operation” — navigate to /operations

**Display condition**

* Shown when income = 0 AND expenses = 0

## 3. Metrics (KPIs)

### 3.1 Metrics Grid

**Layout**

* Responsive grid of three cards
* On desktop: 3 columns in a row
* On mobile: 1 column
* Minimum card width: 280px
* Gap between cards: var(--space-6)

### 3.2 “Income” Card

**Content**

* Title: “Income”
* Period: selected period text (e.g., “For the current month”)
* Value: total income in green
* Format: number with thousand separators + “ ₸”

**Styling**

* Green value color (success class)
* Large font size (var(--font-size-3xl))
* Bold font weight (var(--font-weight-bold))

### 3.3 “Expenses” Card

**Content**

* Title: “Expenses”
* Period: selected period text
* Value: absolute total expenses in red
* Format: number with thousand separators + “ ₸”

**Styling**

* Red value color (danger class)
* Large font size
* Bold font weight

### 3.4 “Balance” Card

**Content**

* Title: “Balance”
* Period: selected period text
* Value: difference between income and expenses
* Format: number with thousand separators + “ ₸”

**Calculation**

* Balance = Income − |Expenses|

**Dynamic styling**

* Green if balance > 0
* Red if balance < 0
* Neutral color if balance = 0

## 4. Analytical Charts

### 4.1 Charts Section

**Header**

* Section title: “Analytics”
* Font size: var(--font-size-xl)
* Bottom margin: var(--space-6)

**Chart type switcher**

* ButtonGroup component with two options:

  * “Categories” — group by categories
  * “Directions” — group by directions
* Switching updates data on both charts

### 4.2 Charts Grid

**Layout**

* Responsive grid of two charts
* On desktop: 2 columns in a row
* On mobile: 1 column
* Minimum chart width: 400px
* Gap between charts: var(--space-6)

### 4.3 Income Chart

**Display**

* Pie chart (PieChart)
* Size: 250px
* Displayed only if there is data (incomeChartData.length > 0)

**Chart title**

* Grouped by categories: “Income by Categories”
* Grouped by directions: “Income by Directions”

**Data**

* Source when grouped by categories: stats.incomeByCategory
* Source when grouped by directions: stats.incomeByDirection
* Data format: array of objects { label: string, value: number }

### 4.4 Expenses Chart

**Display**

* Pie chart (PieChart)
* Size: 250px
* Displayed only if there is data (outcomeChartData.length > 0)

**Chart title**

* Grouped by categories: “Expenses by Categories”
* Grouped by directions: “Expenses by Directions”

**Data**

* Source when grouped by categories: stats.outcomeByCategory
* Source when grouped by directions: stats.outcomeByDirection
* Data format: array of objects { label: string, value: number }

## 5. Data Interaction

### 5.1 Data Loading

**Initialization**

* Load statistics when the component is mounted
* API endpoint: statistics.getStats({ period: selectedPeriod })
* Show a loading indicator while fetching data

**Data refresh**

* Automatically reload data when the period changes
* When switching chart type, only recalculate displayed data (no API call)

### 5.2 Error Handling

**On loading error**

* Error is logged to the console
* Data is not displayed
* “No Data” state is shown

## 6. Data Formatting

### 6.1 Amount Formatting

**Number format**

* Locale: ru-RU
* Minimum fraction digits: 0
* Maximum fraction digits: 0
* Thousand separators
* Currency: ₸ (tenge)

**Examples**

* 1000000 → “1 000 000 ₸”
* 1234.56 → “1 235 ₸”

### 6.2 Period Text

**Formatting**

* current_month → “For the current month”
* 3_months → “For 3 months”
* year → “For the year”
* Default → “For the period”

## 7. Responsiveness

### 7.1 Desktop (> 768px)

**Metrics**

* 3 cards in a row
* Full-size values

**Charts**

* 2 charts in a row
* Full size (250px)

### 7.2 Tablet (480px – 768px)

**Metrics**

* 1 full-width card
* Adaptive spacing

**Charts**

* 1 full-width chart

### 7.3 Mobile (< 480px)

**General**

* Reduced spacing (var(--space-3))
* Smaller font sizes

**Metrics**

* Values: var(--font-size-xl) instead of var(--font-size-3xl)
* Compact cards

**Charts**

* Full-width cards
* Adaptive chart size

### 7.4 Action Navigation

**Buttons in “No Data” state**

* Minimum height: 44px (touch target)
* Full-width on mobile
* Centered text
* Increased font size (var(--font-size-base))

## 8. Performance

**Optimizations**

* Load data once on mount
* Switch chart type without API requests
* Computed properties for derived data
* Conditional rendering (v-if) to hide empty charts

## 9. Component States

### 9.1 Loading State

**While loading data**

* Variable loading = true
* Can be used to show skeletons or spinners

### 9.2 Error State

**On loading error**

* Error in console
* “No Data” state is shown
* User can try importing or adding operations

### 9.3 Success State

**When data is available**

* All metrics are displayed
* Charts with data are shown
* Interactive elements are available
