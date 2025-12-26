"""
Regulatory models for IFRS 17 and Solvency II.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, JSON, Date
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, JSON, Date
from sqlalchemy.orm import relationship
import uuid
from app.core.guid import GUID
from datetime import datetime

from app.core.database import Base

class IFRS17Group(Base):
    """
    Groups insurance contracts as required by IFRS 17.
    Tracks Contract Service Margin (CSM) and Unearned Profit.
    """
    __tablename__ = "ifrs17_groups"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False) # e.g., "Motor 2025 Q1 - Onerous"
    
    # Financials
    initial_csm = Column(Numeric(15, 2), default=0) # Unearned profit at start
    remaining_csm = Column(Numeric(15, 2), default=0) # Current balance of unearned profit
    risk_adjustment = Column(Numeric(15, 2), default=0) 
    
    # Metadata
    cohort_year = Column(String(4))
    portfolio = Column(String(100)) # e.g., "Motor", "Health"
    profitability_category = Column(String(50)) # "onerous", "no_significant_possibility_onerous", "other"
    
    status = Column(String(50), default='active')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RegulatoryMetricSnapshot(Base):
    """
    Periodic snapshots of regulatory health metrics.
    Essential for Solvency II reporting.
    """
    __tablename__ = "regulatory_metrics"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    snapshot_date = Column(Date, default=datetime.utcnow().date)
    
    # Solvency II Metrics
    eligible_own_funds = Column(Numeric(15, 2), nullable=False) # Capital available
    scr_amount = Column(Numeric(15, 2), nullable=False) # Solvency Capital Requirement
    solvency_ratio = Column(Numeric(10, 4), nullable=False) # Own Funds / SCR
    
    # Breakdowns
    market_risk_scr = Column(Numeric(15, 2), default=0)
    underwriting_risk_scr = Column(Numeric(15, 2), default=0)
    operational_risk_scr = Column(Numeric(15, 2), default=0)
    
    details = Column(JSON, default={}) # Detailed breakdown of calculations
    
    created_at = Column(DateTime, default=datetime.utcnow)
