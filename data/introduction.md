# Introduction to FinApp

## 🎯 Welcome to FinApp!

FinApp is a modern financial management system for small and medium-sized businesses in Kazakhstan. We created a service that makes financial accounting simple, clear, and accessible for entrepreneurs who want to control their money without complex accounting software.

---

## 💡 What problems does FinApp solve?

### 1. **Lack of financial transparency**

❌ **Problem:** Entrepreneurs often don’t know how much their business is really earning. Money comes in and goes out, but there’s no complete picture.

✅ **FinApp solution:** A dashboard with key metrics shows the real financial state of your business in one click. You always see income, expenses, and net profit for any period.

### 2. **Complex financial accounting**

❌ **Problem:** Traditional accounting systems (1C, SAP) are too complex and require special knowledge. Small businesses need a simple tool.

✅ **FinApp solution:** An intuitive interface designed for entrepreneurs, not accountants. All operations are clear and can be easily edited directly in the table.

### 3. **Manual data entry**

❌ **Problem:** Copying transactions from bank statements by hand is slow, boring, and error-prone.

✅ **FinApp solution:** Import bank statements in Excel and PDF formats. The system automatically recognizes transactions and suggests rules for automatic categorization.

### 4. **Lack of analytics**

❌ **Problem:** Excel spreadsheets don’t provide full analytics. It’s hard to understand where money goes and which business areas are profitable.

✅ **FinApp solution:**

* Cash Flow Statement grouped by categories, business lines, and accounts
* Profit & Loss (P&L) report to understand real profitability
* Interactive charts with drill-down to each transaction

### 5. **Difficulty working in a team**

❌ **Problem:** As a business grows, you need to involve an accountant or a manager. But how do you give them access without handing over full control?

✅ **FinApp solution:** A participant management system with different access levels (Owner, Administrator, User, View only).

### 6. **Multiple accounts management**

❌ **Problem:** Businesses usually have several bank accounts, cash, and cards. It’s hard to see the full picture.

✅ **FinApp solution:** All accounts in one place. View balances, movements, and filter transactions by specific accounts.

---

## 🚀 Quick Start: Where to begin?

### Step 1: Register and create a workspace

After registration, you are automatically taken to your first workspace (organization).

**What to do:**

1. Go to the **“Organization”** section (via the left menu)
2. Fill in your business information:

   * Organization name
   * BIN (if applicable)
   * Description

> 💡 **Tip:** If you have multiple businesses, you can create a separate workspace for each.

---

### Step 2: Set up directories

Before working with transactions, configure the basic directories. This will take 5–10 minutes but will greatly simplify further work.

#### 2.1 Business accounts

Go to: **Directories → Business Accounts**

**Add all accounts your business uses:**

* Bank accounts (specify IBAN)
* Cash desks
* Corporate cards
* E-wallets

**Example:**

```
Name: Kaspi Gold settlement account
Number: KZ12345678901234567890
Type: Bank account
Currency: KZT
```

> 💡 **Important:** Even if you have only one account, make sure to add it. It’s required to link transactions.

#### 2.2 Transaction categories

Go to: **Directories → Transaction Categories**

The system already contains basic categories (marked as “system” and cannot be deleted). You can add your own specific to your business:

**Income examples:**

* Sales of goods/services
* Consulting services
* Commission income
* Interest income

**Expense examples:**

* Office rent
* Employee salaries
* Marketing and advertising
* Goods purchases
* Bank fees
* Taxes

> 💡 **Tip:** Don’t create too many detailed categories at once. Start with the main ones and add more as needed.

#### 2.3 Business lines (optional)

Go to: **Directories → Business Lines**

If you have multiple business areas (e.g., wholesale and retail, or different cities), create business lines for separate tracking.

**Examples:**

* Almaty office
* Astana office
* Online sales
* Offline store

#### 2.4 Counterparties (optional)

Go to: **Directories → Counterparties**

Add key suppliers and customers you work with frequently.

**Examples:**

* LLP “Goods Supplier” (BIN: 123456789012)
* Sole proprietor Ivanov (IIN: 987654321098)
* Kaspi Bank (for bank fees)

> 💡 **Tip:** You can add counterparties gradually as you work with transactions.

---

### Step 3: Upload data

Now the most important part — fill the system with your financial data. There are two ways:

#### Method 1: Import bank statements (Recommended) 🚀

The fastest way to upload a large volume of data.

**How to do it:**

1. **Download a statement from your bank**

   * Log in to online banking (Kaspi, Halyk, Freedom, etc.)
   * Select a period (we recommend starting with the current month)
   * Download the statement in Excel (.xlsx) or PDF format

2. **Import the statement into FinApp**

   * Go to: **Transactions → Import**
   * Click “Upload statement” or drag files into the upload area
   * Wait for the system to process the file

3. **Set up field mapping**

   * The system will show the statement content
   * Match statement columns with FinApp fields:

     * Transaction date
     * Amount
     * Description
     * Counterparty (if available)
   * Select the account the statement belongs to

4. **Import transactions**

   * Click “Import”
   * Transactions will appear in the “Transactions” tab

> 💡 **Important:** After import, transactions will have no categories. Don’t worry — we’ll categorize them in the next step!

#### Method 2: Manual transaction entry

If you have few transactions or want to add a specific one:

1. Go to: **Transactions → Transactions**
2. Click “Add transaction”
3. Fill in:

   * **Amount**
   * **Date**
   * **Group:** Income or Expense
   * **Account**
   * **Category** (optional at first)
   * **Counterparty**
   * **Description**
4. Click “Save”

---

### Step 4: Categorize transactions

After import, many transactions will be without categories. Let’s fix that!

#### 4.1 Manual categorization (to start)

1. Go to: **Transactions → Transactions**
2. In the table, find transactions
3. Click the “+” button next to “Category”
4. Select the appropriate category
5. It will be saved automatically

> 💡 **Tip:** Start with large amounts — categorize the most significant transactions first.

#### 4.2 Automation rules (to save time)

After manually categorizing several transactions, set up rules for automatic processing of future ones.

1. Go to: **Transactions → Rules**
2. Click “Add rule”
3. Configure:

   * **Target field:** Transaction category
   * **Value:** select category
   * **Conditions:**

     * Example: “Description contains ‘rent’” → category “Office rent”
     * Or: “Counterparty = ‘Supplier LLC’” → category “Goods purchase”
4. Save the rule

**Examples:**

```
Rule 1:
If description contains "Kaspi fee"
→ Set category "Bank fees"

Rule 2:
If counterparty = "Landlord Company"
→ Set category "Office rent"

Rule 3:
If description contains "salary"
→ Set category "Employee salaries"
```

> 💡 **Important:** Rules are applied automatically to newly imported transactions. You can create multiple rules and manage their priority via drag & drop.

---

### Step 5: Explore the dashboard

Now that you have data, look at the financial picture!

1. Go to: **Dashboard**
2. Select a period (current month, 3 months, year)
3. Review metrics:

   * **Income**
   * **Expenses**
   * **Balance:** difference (profit/loss)
4. Check charts:

   * Switch between “By categories” and “By business lines”
   * Analyze where money goes

> 💡 **Insight:** If the balance is negative, don’t panic. You may have imported only one month or had large one-time expenses.

---

### Step 6: Create reports

For deeper analysis, use professional reports.

#### Cash Flow Report

1. Go to: **Reports → Cash Flow**
2. Select period
3. Choose grouping (by months, weeks, etc.)
4. Switch grouping types:

   * By categories
   * By business lines
   * By accounts
   * By counterparties
5. Click table cells to drill down to specific transactions

#### Profit & Loss (P&L) Report

1. Go to: **Reports → P&L**
2. Select period
3. Review structure:

   * Revenue
   * Cost of goods sold
   * Gross profit
   * Operating expenses
   * Operating profit
   * Net profit

> 💡 **Tip:** Export reports to Excel for further analysis or investor presentations.

---

### Step 7: Invite your team (optional)

If others work with finances:

1. Go to: **Organization**
2. Click “Invite” in the “Members” section
3. Enter colleague’s email
4. Choose access level:

   * **Administrator** — everything except deleting the organization
   * **User** — work with transactions and view reports
   * **View only** — view data only
5. Send invitation

---

## 📊 Typical workflow

### Daily (5–10 minutes)

1. Check the dashboard
2. Add new transactions
3. Quick review and categorization

### Weekly (15–30 minutes)

1. Import weekly bank statements
2. Check categorization
3. Review Cash Flow report
4. Analyze major expenses

### Monthly (30–60 minutes)

1. Import monthly statements
2. Review all transactions
3. Create P&L report
4. Export for accountant/taxes
5. Analyze trends vs previous month

---

## 🎓 Useful tips

### 1. Consistency over perfection

❌ Enter everything at month-end
✅ Enter weekly or daily

### 2. Use automation rules

❌ Categorize every transaction manually
✅ Automate recurring ones

### 3. Don’t over-detail categories

❌ “Blue pens”, “Black pens”
✅ “Office supplies”

### 4. Use descriptions

Add short comments for unusual transactions.

### 5. Reconcile with the bank

Once a month, compare FinApp balances with bank balances.

### 6. Use filters and search

Search by text, dates, categories, accounts.

### 7. Export data

For accountants, taxes, investors, and deeper Excel analysis.

---

## 🔮 Roadmap

### Coming soon

* ✅ Bank API integrations (Kaspi, Halyk, Freedom)
* ✅ 1C integration
* ✅ Mobile app
* ✅ OCR for receipts
* ✅ Budgeting

### Planned

* 📊 AI-powered forecasting
* 💳 Online cash register integration
* 🤖 Smart ML categorization
* 📱 Telegram bot
* 🔔 Alerts
* 📈 Advanced analytics

> 💡 **Have an idea?** Write to us at [support@finapp.kz](mailto:support@finapp.kz) — we value your feedback!

---

## 🆘 Need help?

### FAQ

**Q: How much does FinApp cost?**
A: 30-day free trial. After that, plans start from 5,000 KZT/month.

**Q: Is my data safe?**
A: Yes! We use encryption, regular backups, and security best practices.

**Q: Can I export all data?**
A: Yes, anytime to Excel.

**Q: Can I use it for multiple companies?**
A: Yes, create a separate workspace for each.

**Q: Do I need accounting knowledge?**
A: No! FinApp is for entrepreneurs, not accountants.

### Support

* 📧 Email: [support@finapp.kz](mailto:support@finapp.kz)
* 💬 Chat: bottom-right chat icon
* 📞 Phone: +7 (xxx) xxx-xx-xx (Mon–Fri, 9:00–18:00)
* 📚 Knowledge base: help.finapp.kz

### Learning resources

* 📺 Videos: youtube.com/finappkz
* 📖 Docs: docs.finapp.kz
* 🎓 Webinars: Every Friday at 15:00

---

## 🚀 Ready to start?

Now you know how FinApp works and where to begin. Follow the “Quick Start” steps, and within an hour you’ll have a full financial system set up!

**Remember:** The main thing is to start. It doesn’t have to be perfect. Import data, categorize key transactions, review reports — and you’ll already know more about your business than before.

**Good luck managing your finances! 💰**
