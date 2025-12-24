"""
Pydantic schemas for accounting ledger.
"""
from pydantic import BaseModel, Field
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

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

# --- Financial Report Schemas ---

class TrialBalanceItem(BaseModel):
    account_name: str
    account_code: str
    total_debit: Decimal
    total_credit: Decimal
    balance: Decimal
