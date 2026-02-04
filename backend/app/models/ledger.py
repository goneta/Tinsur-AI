"""
General Ledger models for double-entry accounting.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.time import utcnow

from app.core.database import Base

class Account(Base):
    """
    Chart of Accounts.
    Following standard accounting types: Asset, Liability, Equity, Revenue, Expense.
    """
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    code = Column(String(20), nullable=False) # e.g., '1010' for Cash
    name = Column(String(100), nullable=False) # e.g., 'Cash at Bank'
    account_type = Column(String(50), nullable=False) # Asset, Liability, Equity, Revenue, Expense
    
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    company = relationship("Company")
    ledger_entries = relationship("LedgerEntry", back_populates="account")

    def __repr__(self):
        return f"<Account {self.code}: {self.name}>"

class JournalEntry(Base):
    """
    Represents a financial transaction header.
    A single JournalEntry must have at least two LedgerEntry (one debit, one credit) that balance to zero.
    """
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    entry_date = Column(DateTime, default=utcnow)
    description = Column(String(500))
    reference = Column(String(100)) # e.g., Invoice # or Payroll ID
    
    # Audit trail
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    company = relationship("Company")
    entries = relationship("LedgerEntry", back_populates="journal_entry", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<JournalEntry {self.id}: {self.description}>"

class LedgerEntry(Base):
    """
    Line items for a Journal Entry.
    Amount: Positive for Debit, Negative for Credit (standard internal representation).
    Alternatively: Separate debit/credit columns. We'll use debit/credit columns for clarity.
    """
    __tablename__ = "ledger_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    debit = Column(Numeric(15, 2), default=0)
    credit = Column(Numeric(15, 2), default=0)
    
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="entries")
    account = relationship("Account", back_populates="ledger_entries")

    def __repr__(self):
        return f"<LedgerEntry {self.account_id}: D={self.debit} C={self.credit}>"
