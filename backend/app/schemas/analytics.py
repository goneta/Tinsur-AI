"""
Analytics and Reporting Schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
import uuid
from decimal import Decimal

# --- Filter Schemas ---

class AnalyticsFilter(BaseModel):
    """
    Unified filter for analytics queries.
    """
    # Time Filters
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    period_type: str = "custom" # 'day', 'week', 'month', 'year', 'custom'
    
    # Scope Filters
    scope: str = "company" # 'me', 'team', 'company', 'client'
    
    # Entity Filters
    company_id: uuid.UUID
    employee_id: Optional[uuid.UUID] = None # For 'me' or specific employee selection
    client_id: Optional[uuid.UUID] = None # For specific client history
    pos_location_id: Optional[uuid.UUID] = None # Location filter

# --- Metric Models ---

class MetricValue(BaseModel):
    label: str
    value: Union[Decimal, int, float]
    previous_value: Optional[Union[Decimal, int, float]] = None
    change_percentage: Optional[float] = None
    trend: Optional[str] = None # 'up', 'down', 'stable'

class TimeSeriesPoint(BaseModel):
    date: date
    value: Union[Decimal, int, float]
    category: Optional[str] = None # For multi-line charts (e.g., breakdown by product)

# --- Dashboard Response ---

class FinancialMetrics(BaseModel):
    total_revenue: MetricValue
    total_expenses: MetricValue
    net_profit: MetricValue
    accounts_receivable: MetricValue
    expense_breakdown: List[Dict[str, Any]] # e.g., [{"name": "Salaries", "value": 5000}]

class OperationalMetrics(BaseModel):
    total_policies: MetricValue
    new_policies: MetricValue
    active_policies: MetricValue
    claims_ratio: MetricValue # Claims Amount / Premium Income in %
    policy_growth_chart: List[TimeSeriesPoint]

class PerformanceMetrics(BaseModel):
    top_agents: List[Dict[str, Any]] # [{"name": "Agent A", "sales": 10000}]
    sales_by_pos: List[Dict[str, Any]]
    
class AnalyticsDashboardResponse(BaseModel):
    period_label: str # e.g., "Last 30 Days"
    financials: FinancialMetrics
    operations: OperationalMetrics
    performance: PerformanceMetrics
