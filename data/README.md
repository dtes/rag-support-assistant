# FinApp Documentation

Welcome to the documentation for the **FinApp** financial management system!

## 📚 Documentation Structure

### 🎯 [Introduction to FinApp](./introduction.md)

**Start here if you’re a new user!**

This document includes:

* What FinApp is for and what problems it solves
* A step-by-step **Quick Start** guide (from registration to your first reports)
* Setting up directories and uploading data
* A typical workflow (daily/weekly/monthly)
* Useful tips for effective work
* Development roadmap and upcoming integrations (1C, banks, mobile app)
* FAQ and support

**Recommended for:**

* New users who have just signed up
* Entrepreneurs who want to understand how the system can help their business
* Anyone who wants to get started quickly without diving into all the details

---

### 📋 [Functional Requirements](./functional-reqs/)

Detailed technical documentation for all sections of the application.

#### Section navigation:

**📊 [Dashboard](./functional-reqs/dashboard.md)**

* KPI metrics (Income, Expenses, Balance)
* Analytical charts
* Period filtering
* Responsive UI

**💰 [Transactions](./functional-reqs/operations.md)**

* Financial transaction management
* Inline editing
* Bank statement import
* Automation rules
* Data export

**📈 [Reports](./functional-reqs/reports.md)**

* Cash Flow Statement
* Profit & Loss (P&L) report
* Grouping and drill-down
* Export to Excel

**📖 [References](./functional-reqs/references.md)**

* Business accounts
* Transaction categories
* Business lines
* Counterparties

**🏢 [Workspace](./functional-reqs/workspace.md)**

* Workspace information
* Member management
* Access rights
* User invitations

**👤 [Profile](./functional-reqs/profile.md)**

* Personal information
* Security (2FA, password change)
* Data validation

**Recommended for:**

* Developers working on the project
* Product managers
* QA engineers
* Analysts

---

## 🗺️ Documentation Usage Map

### For users

```
New user
    ↓
📖 Read introduction.md
    ↓
Understand how the system works
    ↓
Follow the Quick Start
    ↓
Upload data and start working
    ↓
Dive into specific sections when needed
```

### For developers

```
New task
    ↓
📋 Check functional-reqs/README.md
    ↓
Find the required section (e.g., operations.md)
    ↓
Study requirements and UI components
    ↓
Implement the functionality
```

### For product managers

```
Feature planning
    ↓
📋 Review existing requirements
    ↓
📖 Check alignment with the user journey (introduction.md)
    ↓
Extend/update requirements
    ↓
Align with the team
```

---

## 📝 Quick Links

### For new users

* [What is FinApp and why do I need it?](./introduction.md#-what-problems-does-finapp-solve)
* [Quick Start: Where to begin?](./introduction.md#-quick-start-where-to-begin)
* [How to upload data?](./introduction.md#step-3-upload-data)
* [Typical workflow](./introduction.md#-typical-workflow)
* [FAQ](./introduction.md#-need-help)

### For developers

* [Overview of all sections](./functional-reqs/README.md)
* [General UI principles](./functional-reqs/README.md#general-principles)
* [Technology stack](./functional-reqs/README.md#ui-technology-stack)

### For the team

* [Roadmap](./introduction.md#-roadmap)
* [Integrations (1C, banks)](./introduction.md#coming-soon)

---

## 🎯 Core FinApp Concepts

### Workspace

An isolated area for managing one business. A user can have multiple workspaces for different companies.

### Transaction

Any movement of money: income, expense, or transfer between accounts. A transaction is linked to an account and may have a category, counterparty, and business line.

### References

Data sets used to categorize and filter transactions:

* **Accounts** — bank accounts, cash, cards
* **Categories** — income and expense categories
* **Business lines** — business areas or offices
* **Counterparties** — customers and suppliers

### Rules

Automatic rules for categorizing imported transactions based on conditions (e.g., if the description contains “rent”, then category is “Office rent”).

### Members

Users who have access to a workspace with different permission levels (Owner, Administrator, User, View only).

---

## 🔄 Documentation Update Process

### When to update

1. **When functionality changes** — update the relevant section in `functional-reqs`
2. **When adding a new feature** — describe it in `functional-reqs` and mention it in `introduction.md`
3. **When UI/UX changes** — update screenshots and descriptions in `functional-reqs`
4. **When common questions arise** — add them to the FAQ in `introduction.md`

### How to update

1. Find the relevant file in `docs/`
2. Make your changes
3. Update the “Last updated” date at the bottom of the file
4. Update related sections if needed
5. Make sure all links work

---

## 📞 Contacts

### For users

* **Email:** [support@finapp.kz](mailto:support@finapp.kz)
* **Phone:** +7 (xxx) xxx-xx-xx
* **Chat:** In the bottom-right corner of the app

### For the team

* **Slack:** #finapp-docs
* **Email:** [team@finapp.kz](mailto:team@finapp.kz)
