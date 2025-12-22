"""
LangChain tool definitions for finance API
"""
from typing import Optional, List
from langchain.tools import tool
from tools.mock_finance_api import MockFinanceAPI


# Global API instance - will be set with user context
_finance_api: Optional[MockFinanceAPI] = None


def set_user_context(user_id: str):
    """Set user context for all tools"""
    global _finance_api
    _finance_api = MockFinanceAPI(user_id)


@tool
def get_transactions(period: str = "month", transaction_type: Optional[str] = None) -> dict:
    """
    Get financial transactions for a specified period.

    Args:
        period: Time period - "week", "month", "quarter", or "year"
        transaction_type: Type of transactions - "income", "expense", or None for all

    Returns:
        Dictionary with transactions and summary
    """
    if not _finance_api:
        return {"error": "User context not set"}

    return _finance_api.get_transactions(period, transaction_type)


@tool
def get_cash_flow_report(period: str = "month") -> dict:
    """
    Get cash flow statement (ДДС - Движение Денежных Средств).

    Args:
        period: Time period - "month", "quarter", or "year"

    Returns:
        Cash flow report with inflows, outflows, and balances
    """
    if not _finance_api:
        return {"error": "User context not set"}

    return _finance_api.get_cash_flow_report(period)


@tool
def get_account_balance(account_id: Optional[str] = None) -> dict:
    """
    Get account balance(s).

    Args:
        account_id: Specific account ID (e.g., "acc_001") or None for all accounts

    Returns:
        Account balance information
    """
    if not _finance_api:
        return {"error": "User context not set"}

    return _finance_api.get_account_balance(account_id)


@tool
def get_profit_loss_report(period: str = "month") -> dict:
    """
    Get profit and loss statement (ОПиУ - Отчет о Прибылях и Убытках).

    Args:
        period: Time period - "month", "quarter", or "year"

    Returns:
        P&L report with revenue, expenses, and profit metrics
    """
    if not _finance_api:
        return {"error": "User context not set"}

    return _finance_api.get_profit_loss_report(period)


@tool
def get_expense_categories() -> dict:
    """
    Get list of expense and income categories.

    Returns:
        Dictionary of available categories
    """
    if not _finance_api:
        return {"error": "User context not set"}

    return _finance_api.get_expense_categories()


@tool
def get_counterparties() -> dict:
    """
    Get list of counterparties (suppliers, contractors, clients).

    Returns:
        Dictionary of counterparties
    """
    if not _finance_api:
        return {"error": "User context not set"}

    return _finance_api.get_counterparties()


# List of all available tools
FINANCE_TOOLS = [
    get_transactions,
    get_cash_flow_report,
    get_account_balance,
    get_profit_loss_report,
    get_expense_categories,
    get_counterparties,
]
