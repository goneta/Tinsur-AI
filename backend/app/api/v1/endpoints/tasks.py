"""
Task endpoints for internal workflow.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_agent
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Create a task."""
    payload.company_id = current_user.company_id
    payload.created_by = current_user.id

    task = Task(
        company_id=payload.company_id,
        assigned_to=payload.assigned_to,
        created_by=payload.created_by,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=payload.status,
        due_date=payload.due_date,
        related_resource=payload.related_resource,
        related_resource_id=payload.related_resource_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List tasks for the current company."""
    query = db.query(Task).filter(Task.company_id == current_user.company_id)
    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db),
):
    """Update a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or task.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task
