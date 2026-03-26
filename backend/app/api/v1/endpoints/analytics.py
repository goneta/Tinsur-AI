"""
Analytics API endpoints.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
import io

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsFilter, AnalyticsDashboardResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.post("/dashboard", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    filter_params: AnalyticsFilter,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve aggregated analytics for the dashboard.
    """
    # Enforce company scope
    if filter_params.company_id != current_user.company_id:
        if current_user.role != 'super_admin':
             raise HTTPException(status_code=403, detail="Not authorized to access this company's data")
    
    # Check permissions (either admin/manager role or specific permission)
    if current_user.role not in ['super_admin', 'company_admin', 'manager']:
        # Could also use new require_permission("view_analytics") here if fully migrating
        # For now, fix the immediate 403 by allowing manager
        raise HTTPException(status_code=403, detail="Insufficient role for analytics")
    
    service = AnalyticsService(db)
    return service.get_dashboard_metrics(filter_params)

from fastapi.responses import StreamingResponse
from app.services.export_service import ExportService
import io

@router.post("/export")
def export_analytics_report(
    filter_params: AnalyticsFilter,
    format: str = Query("csv", pattern="^(csv|pdf)$"),
    report_type: str = Query("financial_close", pattern="^(financial_close|claims_summary|policies_summary)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export analytics report.
    """
    service = AnalyticsService(db)
    export_service = ExportService()
    
    # 1. Fetch Data based on report type
    data = []
    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d')}"
    
    if report_type == "financial_close":
        # Re-use metrics logic or fetch detailed ledger
        # For CSV export, raw rows are better than aggregated metrics
        # Let's simple fetch ledger entries for the period
        from app.models.ledger import JournalEntry, LedgerEntry, Account
        
        start = filter_params.start_date or date.today().replace(day=1)
        end = filter_params.end_date or date.today()
        
        entries = db.query(JournalEntry).filter(
            JournalEntry.company_id == current_user.company_id,
            JournalEntry.entry_date >= start,
            JournalEntry.entry_date <= end
        ).all()
        
        # Flatten for CSV
        for je in entries:
            for le in je.entries:
                data.append({
                    "Date": je.entry_date,
                    "Reference": je.reference,
                    "Description": je.description,
                    "Account": le.account.name,
                    "Debit": le.debit,
                    "Credit": le.credit
                })
        filename = f"financial_close_{start}_{end}"
        
    elif report_type == "policies_summary":
        pass # To implement
        
    # 2. Generate File
    if format == "csv":
        csv_content = export_service.generate_csv(data)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
        )
        
    raise HTTPException(status_code=400, detail="Format not supported")
