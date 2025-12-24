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
