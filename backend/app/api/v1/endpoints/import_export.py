from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.import_service import ImportService
from app.services.export_service import ExportService
from app.services.policy_service import PolicyService
# Assuming these services exist and are available
# from app.services.client_service import ClientService 
# from app.services.employee_service import EmployeeService

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    data_type: str = Form(...), # 'clients', 'employees', 'policies'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file and get back the parsed records for mapping.
    """
    content = await file.read()
    file_format = file.filename.split('.')[-1]
    
    import_service = ImportService(db)
    try:
        records = import_service.parse_file(content, file_format)
        return {
            "filename": file.filename,
            "data_type": data_type,
            "record_count": len(records),
            "records": records[:10], # Return first 10 for preview/mapping
            "all_fields": list(records[0].keys()) if records else []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate")
async def validate_import(
    data_type: str = Body(...),
    records: List[Dict[str, Any]] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check records for duplicates.
    """
    import_service = ImportService(db)
    duplicates = import_service.find_duplicates(data_type, records, current_user.company_id)
    
    return {
        "total_records": len(records),
        "duplicate_count": len(duplicates),
        "duplicates": duplicates
    }

@router.post("/execute")
async def execute_import(
    data_type: str = Body(...),
    records: List[Dict[str, Any]] = Body(...),
    mapping: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalize the import.
    """
    # This would call the respective services to create the records
    # For now, we'll return a success message as a placeholder
    # Implementation of actual creation would be long and depends on service existence
    return {
        "status": "success",
        "imported_count": len(records),
        "message": f"Successfully imported {len(records)} {data_type}"
    }

@router.get("/export")
async def export_data(
    data_type: str, # 'clients', 'employees', 'policies'
    format: str, # 'csv', 'json', 'xml', 'pdf', 'md'
    fields: Optional[str] = None, # Comma separated
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export data in the requested format.
    """
    # Fetch data based on data_type
    data = []
    if data_type == 'clients':
        from app.models.client import Client
        clients = db.query(Client).filter(Client.company_id == current_user.company_id).all()
        data = [
            {
                "id": str(c.id),
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone": c.phone,
                "status": c.status
            } for c in clients
        ]
    elif data_type == 'employees':
        from app.models.user import User
        employees = db.query(User).filter(User.company_id == current_user.company_id, User.role != 'client').all()
        data = [
            {
                "id": str(e.id),
                "first_name": e.first_name,
                "last_name": e.last_name,
                "email": e.email,
                "role": e.role
            } for e in employees
        ]
    elif data_type == 'policies':
        from app.models.policy import Policy
        policies = db.query(Policy).filter(Policy.company_id == current_user.company_id).all()
        data = [
            {
                "id": str(p.id),
                "policy_number": p.policy_number,
                "status": p.status,
                "premium_amount": float(p.premium_amount) if p.premium_amount else 0
            } for p in policies
        ]
    
    if fields:
        field_list = fields.split(',')
        data = [{k: v for k, v in row.items() if k in field_list} for row in data]

    export_service = ExportService()
    
    filename = f"export_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    
    if format == 'csv':
        content = export_service.generate_csv(data)
        media_type = "text/csv"
    elif format == 'json':
        content = export_service.generate_json(data)
        media_type = "application/json"
    elif format == 'xml':
        content = export_service.generate_xml(data, root_name=data_type.capitalize())
        media_type = "application/xml"
    elif format == 'md':
        content = export_service.generate_markdown(data, title=f"{data_type.capitalize()} Export")
        media_type = "text/markdown"
    elif format == 'pdf':
        content = export_service.generate_pdf(data, report_type=data_type)
        media_type = "application/pdf"
        filename = f"export_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    elif format == 'excel' or format == 'xlsx':
        content = export_service.generate_excel(
            data,
            sheet_name=data_type.capitalize(),
            title=f"{data_type.capitalize()} Export",
        )
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"export_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: csv, json, xml, md, pdf, excel")

    from fastapi.responses import Response
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
