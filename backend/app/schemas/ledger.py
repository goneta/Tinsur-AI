"""
Pydantic schemas for accounting ledger.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from decimal import Decimal

# --- Account Schemas ---

class AccountBase(BaseModel):
    code: str
    name: str
    account_type: str
    description: Optional[str] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Ledger Entry Schemas ---

class LedgerEntryBase(BaseModel):
    account_id: uuid.UUID
    debit: Decimal = Decimal('0')
    credit: Decimal = Decimal('0')

class LedgerEntryCreate(LedgerEntryBase):
    pass

class LedgerEntryResponse(LedgerEntryBase):
    id: uuid.UUID
    journal_entry_id: uuid.UUID
    account_name: Optional[str] = None # Added for convenience in UI
    account_code: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# --- Journal Entry Schemas ---

class JournalEntryBase(BaseModel):
    entry_date: datetime = Field(default_factory=datetime.utcnow)
    description: str
    reference: Optional[str] = None

class JournalEntryCreate(JournalEntryBase):
    entries: List[LedgerEntryCreate]

    def is_balanced(self) -> bool:
        total_debit = sum(e.debit for e in self.entries)
        total_credit = sum(e.credit for e in self.entries)
        return total_debit == total_credit

class JournalEntryResponse(JournalEntryBase):
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    entries: List[LedgerEntryResponse]
    model_config = ConfigDict(from_attributes=True)

# --- Financial Report Schemas ---

class TrialBalanceItem(BaseModel):
    account_name: str
    account_code: str
    total_debit: Decimal
    total_credit: Decimal
    balance: Decimal

class FinancialReportItem(BaseModel):
    name: str
    code: str
    amount: Decimal

class ProfitLossResponse(BaseModel):
    revenue: List[FinancialReportItem]
    expenses: List[FinancialReportItem]
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal

class BalanceSheetResponse(BaseModel):
    assets: List[FinancialReportItem]
    liabilities: List[FinancialReportItem]
    equity: List[FinancialReportItem]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
