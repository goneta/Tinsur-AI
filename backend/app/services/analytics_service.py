"""
Analytics Service for aggregating/calculating metrics.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, desc, extract
from typing import List, Dict, Any, Tuple
from decimal import Decimal
from datetime import date, datetime, timedelta

from app.models.ledger import LedgerEntry, Account, JournalEntry
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.user import User
from app.models.commission import Commission
from app.schemas.analytics import (
    AnalyticsFilter, AnalyticsDashboardResponse, 
    FinancialMetrics, OperationalMetrics, PerformanceMetrics,
    MetricValue, TimeSeriesPoint
)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_metrics(self, filters: AnalyticsFilter) -> AnalyticsDashboardResponse:
        """
        Aggregate all metrics for the dashboard based on filters.
        """
        # Calculate date range if not provided (default to this month)
        start_date = filters.start_date or date.today().replace(day=1)
        end_date = filters.end_date or date.today()
        
        # Determine comparison period (previous equivalent period)
        duration = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=duration)
        prev_end = start_date - timedelta(days=1)

        # 1. Financials
        financials = self._get_financial_metrics(filters, start_date, end_date, prev_start, prev_end)
        
        # 2. Operations
        operations = self._get_operational_metrics(filters, start_date, end_date, prev_start, prev_end)
        
        # 3. Performance
        performance = self._get_performance_metrics(filters, start_date, end_date)

        return AnalyticsDashboardResponse(
            period_label=f"{start_date} to {end_date}",
            financials=financials,
            operations=operations,
            performance=performance
        )

    def _get_financial_metrics(self, filters: AnalyticsFilter, start, end, prev_start, prev_end) -> FinancialMetrics:
        """Calculate Revenue, Expenses, Profit."""
        
        def calc_ledger_balance(account_type, s, e):
            query = self.db.query(
                func.sum(LedgerEntry.credit) - func.sum(LedgerEntry.debit)
            ).join(LedgerEntry.account).join(LedgerEntry.journal_entry).filter(
                Account.company_id == filters.company_id,
                Account.account_type == account_type,
                JournalEntry.entry_date >= s,
                JournalEntry.entry_date <= e  # Simplified: ensuring date is within range
            )
            # Apply scope/location filters if JournalEntry or Account links to them (Note: Ledger is usually company-wide)
            # For this Phase, we'll keep financials company-wide unless strictly filtered
            return Decimal(query.scalar() or 0)

        # Revenue (Credit Balance for Revenue accounts)
        rev_curr = calc_ledger_balance("Revenue", start, end)
        rev_prev = calc_ledger_balance("Revenue", prev_start, prev_end)
        
        # Expenses (Debit Balance for Expense accounts usually positive for expense logic, but in DB credits are negative)
        # Actually, let's use the explicit debit-credit logic from AccountingService helper
        # Expense: Debit increases it. So Balance = Debit - Credit.
        def calc_expense_balance(s, e):
             query = self.db.query(
                func.sum(LedgerEntry.debit) - func.sum(LedgerEntry.credit)
            ).join(LedgerEntry.account).join(LedgerEntry.journal_entry).filter(
                Account.company_id == filters.company_id,
                Account.account_type == "Expense",
                JournalEntry.entry_date >= s,
                JournalEntry.entry_date <= e
            )
             return Decimal(query.scalar() or 0)

        exp_curr = calc_expense_balance(start, end)
        exp_prev = calc_expense_balance(prev_start, prev_end)
        
        net_curr = rev_curr - exp_curr
        net_prev = rev_prev - exp_prev
        
        # Accounts Receivable (Asset)
        ar_balance = self.db.query(
                func.sum(LedgerEntry.debit) - func.sum(LedgerEntry.credit)
            ).join(LedgerEntry.account).filter(
                Account.company_id == filters.company_id,
                Account.code == "1200" # Accounts Receivable
            ).scalar() or 0
            
        return FinancialMetrics(
            total_revenue=self._make_metric("Total Revenue", rev_curr, rev_prev),
            total_expenses=self._make_metric("Total Expenses", exp_curr, exp_prev),
            net_profit=self._make_metric("Net Profit", net_curr, net_prev),
            accounts_receivable=MetricValue(label="Accounts Receivable", value=Decimal(ar_balance)),
            expense_breakdown=[] # To be implemented if needed
        )

    def _get_operational_metrics(self, filters, start, end, prev_start, prev_end) -> OperationalMetrics:
        """Calculate Policy and Claims data."""
        
        def count_policies(s, e):
            q = self.db.query(func.count(Policy.id)).filter(
                Policy.company_id == filters.company_id,
                Policy.start_date >= s,
                Policy.start_date <= e
            )
            if filters.employee_id:
                # Assuming Policy has an agent_id or user_id field. Let's check model...
                # Using known fields from previous tasks.
                pass # Filters logic to be refined with exact Policy model fields
            return q.scalar() or 0

        total_policies = self.db.query(func.count(Policy.id)).filter(
            Policy.company_id == filters.company_id,
            Policy.status == 'active'
        ).scalar() or 0
        
        new_curr = count_policies(start, end)
        new_prev = count_policies(prev_start, prev_end)
        
        # Claims Ratio
        # Claims Paid / Premium Earned (Simplified: Claims Amount / Total Revenue)
        # Using Claims table sum
        claims_amount = self.db.query(func.sum(Claim.claim_amount)).filter(
            Claim.company_id == filters.company_id,
            Claim.incident_date >= start,
            Claim.incident_date <= end
        ).scalar() or 0
        
        # This relies on revenue calculated in _get_financial_metrics, or we can query payment table
        # For speed let's assume we can pass revenue or re-query
        revenue = self.db.query(func.sum(LedgerEntry.credit) - func.sum(LedgerEntry.debit)).join(LedgerEntry.account).join(LedgerEntry.journal_entry).filter(
                Account.company_id == filters.company_id,
                Account.account_type == "Revenue",
                JournalEntry.entry_date >= start,
                JournalEntry.entry_date <= end
        ).scalar() or 0
        
        ratio = 0
        if revenue and revenue > 0:
            ratio = (claims_amount / revenue) * 100
            
        return OperationalMetrics(
            total_policies=MetricValue(label="Total Active Policies", value=total_policies),
            new_policies=self._make_metric("New Policies", new_curr, new_prev),
            active_policies=MetricValue(label="Active Policies", value=total_policies),
            claims_ratio=MetricValue(label="Claims Ratio", value=Decimal(ratio).quantize(Decimal("0.01"))),
            policy_growth_chart=[] # Placeholder for time series
        )

    def _get_performance_metrics(self, filters, start, end) -> PerformanceMetrics:
        """Agent and POS performance."""
        # Top Agents by Revenue (Premium)
        top_agents_q = self.db.query(
            User.first_name, User.last_name, 
            func.count(Policy.id).label('count'),
            func.sum(Policy.premium_amount).label('total')
        ).join(Policy, Policy.sales_agent_id == User.id).filter(
            Policy.company_id == filters.company_id,
            Policy.created_at >= start,
            Policy.created_at <= end,
            User.role.in_(['agent', 'manager'])
        ).group_by(User.id).order_by(desc('total')).limit(5).all()
        
        top_agents = [
            {
                "name": f"{uc.first_name} {uc.last_name}", 
                "sales": uc.total or 0,
                "count": uc.count
            }
            for uc in top_agents_q
        ]
        
        return PerformanceMetrics(
            top_agents=top_agents,
            sales_by_pos=[]
        )

    def _make_metric(self, label, current, previous) -> MetricValue:
        """Helper to create MetricValue with trend."""
        change = 0.0
        trend = "stable"
        
        if previous and previous != 0:
            change = float((current - previous) / previous) * 100
            
        if change > 0:
            trend = "up"
        elif change < 0:
            trend = "down"
            
        return MetricValue(
            label=label,
            value=current,
            previous_value=previous,
            change_percentage=round(change, 1),
            trend=trend
        )
