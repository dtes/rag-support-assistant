# Functional requirements: Dashboard section

## 1. General purpose

The dashboard provides the user with a visual overview of the financial condition of the business with key metrics and analytics for the selected period.

## 2. Main components

### 2.1 Header and Filters

**Page title**
- The name "Dashboard" is displayed in the header of the application
- The subtitle "Business Overview" on the page itself

**Period filter**
- A drop-down list for selecting the analysis period:
- Current month
- 3 months
- Year
- Automatic data reset when the period changes
- Selector width: 200px

### 2.2 The "No data" status

**Display in the absence of operations**
- It is shown when there are no financial transactions for the selected period.
- A card with centered content:
  - Icon 📊
- Heading "No data for the selected period"
- Explanatory text with recommendations
- Two action buttons:
- "📥 Import data" - switch to /operations?tab=import
    - "➕ Add operation" - switch to /operations

**Display condition**
- It is shown when income = 0 and expenses = 0

## 3. Metrics (KPIs)

### 3.1 Metric Grid

**Location**
- Adaptive grid of three cards
- On the desktop: 3 columns in a row
- On mobile devices: 1 speaker
- Minimum card width: 280px
- Indentation between cards: var(--space-6)

### 3.2 Income Card

**Content**
- Heading: "Income"
- Period: the text of the selected period (for example, "For the current month")
- Value: the amount of income in green
- Format: a number separated by thousands + " ₸"

**Stylization**
- The green color value (success class)
- Large font size (var(--font-size-3xl))
- Bold (var(--font-weight-bold))

### 3.3 Expense Card

**Content**
- Heading: "Expenses"
- Period: the text of the selected period
- Value: the absolute amount of expenses in red
- Format: a number separated by thousands + " ₸"

**Stylization**
- Red color value (danger class)
- Large font size
- Bold lettering

### 3.4 The "Balance" card

**Content**
- Heading: "Balance"
- Period: the text of the selected period
- Value: the difference between income and expenses
- Format: a number separated by thousands + " ₸"

**Calculation**
- Balance = Income - |Expenses|

**Dynamic styling**
- Green color if the balance is > 0
- Red color if the balance is < 0
- Neutral color if balance = 0

## 4. Analytical charts

### 4.1 Diagram Section

**Headline**
- Section name: "Analytics"
- Font size: var(--font-size-xl)
- Bottom margin: var(--space-6)

**Chart type switch**
- ButtonGroup component with two options:
- "Articles" - grouping by category
- "Directions" - grouping by directions
- Switching updates the data on both charts

### 4.2 Chart Grid

**Location**
- Adaptive grid of two diagrams
- On the desktop: 2 columns in a row
- On mobile devices: 1 speaker
- Minimum chart width: 400px
- Indentation between diagrams: var(--space-6)

### 4.3 Revenue Chart

**Display**
- Pie Chart (PieChart)
- Size: 250px
- Shown only if there is data (incomeChartData.length > 0)

**Chart title**
- When grouped by category: "Income by category"
- When grouped by directions: "Income by destination"

**Data**
- Source when grouped by category: stats.incomeByCategory
- Source when grouped by destination: stats.incomeByDirection
- Data format: array of objects {label: string, value: number}

### 4.4 Expense Chart

**Display**
- Pie Chart (PieChart)
- Size: 250px
- Shown only if there is data (outcomeChartData.length > 0)

**Chart title**
- When grouped by category: "Expenses by category"
- When grouped by directions: "Expenses by destination"

**Data**
- Source when grouped by category: stats.outcomeByCategory
- Source when grouped by destination: stats.outcomeByDirection
- Data format: array of objects {label: string, value: number}

## 5. Interaction with data

### 5.1 Loading data

**Initialization**
- Loading statistics when mounting a component
- API endpoint: statistics.getStats({period: selectedPeriod})
- Loading indicator during data acquisition

**Data update**
- When the period changes, the data is automatically reloaded
- When switching the chart type, only the displayed data is recalculated (without an API request)

### 5.2 Error Handling

**If there is a download error**
- The error is logged to the console
- Data is not displayed
- The "No data" status is displayed

##6. Formatting data

### 6.1 Formatting amounts

**Numeric format**
- Locale: ru-RU
- Minimum fractional characters: 0
- Maximum fractional characters: 0
- Thousand separators
- Currency: ₸ (tenge)

**Examples**
- 1000000 → "1 000 000 ₸"
- 1234.56 → "1 235 ₸"

### 6.2 Period text

**Formatting**
- current_month → "For the current month"
- 3_months → "For 3 months"
- year → "For the year"
- By default → "For the period"

##7. Adaptability

### 7.1 Desktop (> 768px)

**Metrics**
- 3 cards in a row
- Full-size values

**Charts**
- 2 charts in a row
- Full size (250px)

###7.2 Tablet (480px - 768px)

**Metrics**
- 1 full-width card
- Adaptive margins

**Charts**
- 1 full-width chart

### 7.3 Mobile (< 480px)

**General**
- Reduced margins (var(--space-3))
- Reduced font sizes

**Metrics**
- Values: var(--font-size-xl) instead of var(--font-size-3xl)
- Compact cards

**Charts**
- Full-width cards
- Adaptive chart size

### 7.4 Navigation through actions

**Buttons in the "No data" state**
- Minimum height: 44px (touch target)
- Full-width on mobile devices
- Centered text
- Increased font size (var(--font-size-base))

## 8. Efficiency

**Optimizations**
- Loading data once during mounting
- Switching the chart type without API requests
- Calculated properties for derived data
- Conditional rendering (v-if) to hide empty diagrams

## 9. Component States

### 9.1 Load indication

**During data download**
- Variable loading = true
- Can be used to display skeletons or spinners

### 9.2 Error Status

**If there is a download error**
- Error in the console
- The "No data" status is displayed
- The user can try to import or add operations

### 9.3 Successful status

**If data is available**
- All metrics are displayed
- Charts with data are shown
- Interactive elements are available for interaction