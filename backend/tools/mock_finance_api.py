"""
Mock Finance API - simulates financial service endpoints
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import random


class MockFinanceAPI:
    """Mock API for financial operations"""

    def __init__(self, user_id: str):
        """Initialize with user context"""
        self.user_id = user_id

        # Mock data for demo
        self._accounts = [
            {"id": "acc_001", "name": "Основной счет", "currency": "KZT", "balance": Decimal("1250000.50")},
            {"id": "acc_002", "name": "Резервный счет", "currency": "USD", "balance": Decimal("5000.00")},
            {"id": "acc_003", "name": "Операционный счет", "currency": "KZT", "balance": Decimal("850000.00")},
        ]

        self._expense_categories = [
            {"id": "cat_001", "name": "Аренда", "type": "expense"},
            {"id": "cat_002", "name": "Зарплата", "type": "expense"},
            {"id": "cat_003", "name": "Маркетинг", "type": "expense"},
            {"id": "cat_004", "name": "Продажи услуг", "type": "income"},
            {"id": "cat_005", "name": "Подписки", "type": "income"},
        ]

        self._counterparties = [
            {"id": "cp_001", "name": "ТОО СтройСервис", "type": "supplier"},
            {"id": "cp_002", "name": "ИП Иванов А.А.", "type": "contractor"},
            {"id": "cp_003", "name": "ТОО ТехноКом", "type": "client"},
        ]

    def get_transactions(
        self,
        period: str = "month",
        transaction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get transactions for specified period

        Args:
            period: "week", "month", "quarter", "year"
            transaction_type: "income", "expense", or None for all
        """
        # Generate mock transactions
        periods = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }
        days = periods.get(period, 30)

        transactions = []
        for i in range(random.randint(5, 15)):
            date = datetime.now() - timedelta(days=random.randint(0, days))
            trans_type = transaction_type or random.choice(["income", "expense"])
            amount = Decimal(str(random.randint(10000, 500000)))

            transaction = {
                "id": f"trans_{i:03d}",
                "date": date.strftime("%Y-%m-%d"),
                "type": trans_type,
                "amount": float(amount),
                "category": random.choice(self._expense_categories)["name"],
                "account": random.choice(self._accounts)["name"],
                "description": f"Операция {i+1}"
            }
            transactions.append(transaction)

        # Calculate summary
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")

        return {
            "user_id": self.user_id,
            "period": period,
            "transaction_count": len(transactions),
            "total_income": total_income,
            "total_expense": total_expense,
            "net_cash_flow": total_income - total_expense,
            "transactions": transactions
        }

    def get_cash_flow_report(self, period: str = "month") -> Dict[str, Any]:
        """
        Get cash flow statement (ДДС)

        Args:
            period: "month", "quarter", "year"
        """
        transactions = self.get_transactions(period)

        return {
            "user_id": self.user_id,
            "report_type": "cash_flow",
            "period": period,
            "opening_balance": 2000000.00,
            "cash_inflows": transactions["total_income"],
            "cash_outflows": transactions["total_expense"],
            "net_cash_flow": transactions["net_cash_flow"],
            "closing_balance": 2000000.00 + transactions["net_cash_flow"],
            "generated_at": datetime.now().isoformat()
        }

    def get_account_balance(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account balance(s)

        Args:
            account_id: specific account ID or None for all accounts
        """
        if account_id:
            account = next((a for a in self._accounts if a["id"] == account_id), None)
            if not account:
                return {"error": f"Account {account_id} not found"}

            return {
                "user_id": self.user_id,
                "account": {
                    **account,
                    "balance": float(account["balance"])
                }
            }

        # Return all accounts
        return {
            "user_id": self.user_id,
            "accounts": [
                {**a, "balance": float(a["balance"])}
                for a in self._accounts
            ],
            "total_balance_kzt": sum(
                float(a["balance"]) if a["currency"] == "KZT" else float(a["balance"]) * 470
                for a in self._accounts
            )
        }

    def get_profit_loss_report(self, period: str = "month") -> Dict[str, Any]:
        """
        Get profit & loss statement (ОПиУ)

        Args:
            period: "month", "quarter", "year"
        """
        transactions = self.get_transactions(period)

        revenue = transactions["total_income"]
        expenses = transactions["total_expense"]
        gross_profit = revenue - expenses
        operating_expenses = expenses * 0.7  # Mock
        net_profit = gross_profit - operating_expenses

        return {
            "user_id": self.user_id,
            "report_type": "profit_loss",
            "period": period,
            "revenue": revenue,
            "cost_of_goods_sold": expenses * 0.3,
            "gross_profit": gross_profit,
            "operating_expenses": operating_expenses,
            "net_profit": net_profit,
            "profit_margin": (net_profit / revenue * 100) if revenue > 0 else 0,
            "generated_at": datetime.now().isoformat()
        }

    def get_expense_categories(self) -> Dict[str, Any]:
        """Get expense/income categories dictionary"""
        return {
            "user_id": self.user_id,
            "categories": self._expense_categories
        }

    def get_counterparties(self) -> Dict[str, Any]:
        """Get counterparties dictionary"""
        return {
            "user_id": self.user_id,
            "counterparties": self._counterparties
        }


# Convenience functions with user context
def create_finance_api(user_id: str) -> MockFinanceAPI:
    """Create finance API instance with user context"""
    return MockFinanceAPI(user_id)
