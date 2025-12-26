"""
Accounting Service for managing the General Ledger.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import uuid
from decimal import Decimal
from datetime import datetime

from app.models.ledger import Account, JournalEntry, LedgerEntry
from app.schemas.ledger import JournalEntryCreate, TrialBalanceItem

class AccountingService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_account(self, company_id: uuid.UUID, code: str, name: str, account_type: str) -> Account:
        """Helper to get a specific account or create it if missing."""
        account = self.db.query(Account).filter(
            Account.company_id == company_id,
            Account.code == code
        ).first()

        if not account:
            account = Account(
                company_id=company_id,
                code=code,
                name=name,
                account_type=account_type
            )
            self.db.add(account)
            self.db.flush()
        
        return account

    def initialize_chart_of_accounts(self, company_id: uuid.UUID):
        """Initialize standard Chart of Accounts for a company."""
        defaults = [
            # Assets
            ("1000", "Cash", "Asset"),
            ("1010", "Bank - XOF", "Asset"),
            ("1200", "Accounts Receivable", "Asset"),
            # Liabilities
            ("2000", "Accounts Payable", "Liability"),
            ("2100", "Payroll Payable", "Liability"),
            ("2200", "Tax Payable", "Liability"),
            ("2300", "IFRS 17 - CSM (Liability)", "Liability"),
            ("2400", "IFRS 17 - Risk Adjustment", "Liability"),
            # Equity
            ("3000", "Retained Earnings", "Equity"),
            # Revenue
            ("4000", "Premium Income", "Revenue"),
            # Expense
            ("5000", "Salary Expense", "Expense"),
            ("5100", "Commission Expense", "Expense"),
            ("5200", "Operating Expense", "Expense")
        ]
        
        for code, name, acc_type in defaults:
            self.get_or_create_account(company_id, code, name, acc_type)
            
        self.db.commit()

    def post_journal_entry(self, company_id: uuid.UUID, data: JournalEntryCreate, creator_id: uuid.UUID) -> JournalEntry:
        """
        Post a balanced journal entry to the ledger.
        Ensures Sum(Debit) == Sum(Credit).
        """
        if not data.is_balanced():
            raise ValueError("Journal entry is not balanced. Total Debits must equal Total Credits.")

        journal_entry = JournalEntry(
            company_id=company_id,
            description=data.description,
            reference=data.reference,
            entry_date=data.entry_date,
            created_by=creator_id
        )
        self.db.add(journal_entry)
        self.db.flush()

        for entry_data in data.entries:
            ledger_entry = LedgerEntry(
                journal_entry_id=journal_entry.id,
                account_id=entry_data.account_id,
                debit=entry_data.debit,
                credit=entry_data.credit
            )
            self.db.add(ledger_entry)

        self.db.commit()
        self.db.refresh(journal_entry)
        return journal_entry

    def get_account_balance(self, account_id: uuid.UUID) -> Decimal:
        """Calculate the current balance for an account."""
        result = self.db.query(
            func.sum(LedgerEntry.debit) - func.sum(LedgerEntry.credit)
        ).filter(LedgerEntry.account_id == account_id).scalar()
        
        return Decimal(str(result or 0))

    def get_trial_balance(self, company_id: uuid.UUID) -> List[TrialBalanceItem]:
        """Generate a trial balance report for all accounts in a company."""
        accounts = self.db.query(Account).filter(Account.company_id == company_id).all()
        report = []
        
        for acc in accounts:
            totals = self.db.query(
                func.sum(LedgerEntry.debit).label('debit'),
                func.sum(LedgerEntry.credit).label('credit')
            ).filter(LedgerEntry.account_id == acc.id).first()
            
            d = Decimal(str(totals.debit or 0))
            c = Decimal(str(totals.credit or 0))
            
            report.append(TrialBalanceItem(
                account_name=acc.name,
                account_code=acc.code,
                total_debit=d,
                total_credit=c,
                balance=d - c
            ))
            
        return report

    def get_ledger_history(self, company_id: uuid.UUID, limit: int = 50) -> List[JournalEntry]:
        """Retrieve recent ledger history."""
        return self.db.query(JournalEntry).filter(
            JournalEntry.company_id == company_id
        ).order_by(JournalEntry.entry_date.desc()).limit(limit).all()

    def get_profit_loss(self, company_id: uuid.UUID, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate Profit and Loss report."""
        accounts = self.db.query(Account).filter(
            Account.company_id == company_id,
            Account.account_type.in_(["Revenue", "Expense"])
        ).all()
        
        report = {
            "revenue": [],
            "expenses": [],
            "total_revenue": Decimal("0.0"),
            "total_expenses": Decimal("0.0"),
            "net_profit": Decimal("0.0")
        }
        
        for acc in accounts:
            # Aggregate entries in the date range
            balance_query = self.db.query(
                func.sum(LedgerEntry.debit).label('debit'),
                func.sum(LedgerEntry.credit).label('credit')
            ).join(JournalEntry).filter(
                LedgerEntry.account_id == acc.id,
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date
            ).first()
            
            d = Decimal(str(balance_query.debit or 0))
            c = Decimal(str(balance_query.credit or 0))
            
            # Natural balance for P&L
            if acc.account_type == "Revenue":
                val = c - d # Credits are positive for revenue
                report["revenue"].append({"name": acc.name, "amount": val, "code": acc.code})
                report["total_revenue"] += val
            else:
                val = d - c # Debits are positive for expenses
                report["expenses"].append({"name": acc.name, "amount": val, "code": acc.code})
                report["total_expenses"] += val
                
        report["net_profit"] = report["total_revenue"] - report["total_expenses"]
        return report

    def get_balance_sheet(self, company_id: uuid.UUID, as_of_date: datetime) -> Dict[str, Any]:
        """Generate Balance Sheet as of a specific date."""
        accounts = self.db.query(Account).filter(
            Account.company_id == company_id,
            Account.account_type.in_(["Asset", "Liability", "Equity"])
        ).all()
        
        report = {
            "assets": [],
            "liabilities": [],
            "equity": [],
            "total_assets": Decimal("0.0"),
            "total_liabilities": Decimal("0.0"),
            "total_equity": Decimal("0.0")
        }
        
        for acc in accounts:
            # Aggregate all entries up to as_of_date
            balance_query = self.db.query(
                func.sum(LedgerEntry.debit).label('debit'),
                func.sum(LedgerEntry.credit).label('credit')
            ).join(JournalEntry).filter(
                LedgerEntry.account_id == acc.id,
                JournalEntry.entry_date <= as_of_date
            ).first()
            
            d = Decimal(str(balance_query.debit or 0))
            c = Decimal(str(balance_query.credit or 0))
            
            if acc.account_type == "Asset":
                val = d - c
                report["assets"].append({"name": acc.name, "amount": val, "code": acc.code})
                report["total_assets"] += val
            elif acc.account_type == "Liability":
                val = c - d
                report["liabilities"].append({"name": acc.name, "amount": val, "code": acc.code})
                report["total_liabilities"] += val
            else: # Equity
                val = c - d
                report["equity"].append({"name": acc.name, "amount": val, "code": acc.code})
                report["total_equity"] += val
                
        # Include Net Profit in Equity if not already closed out to Retained Earnings
        # In this simple model, we'll calculate YTD profit manually for the balance sheet
        # if not explicitly tracked in an account.
        
        return report
