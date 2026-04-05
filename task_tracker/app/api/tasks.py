from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskFilter
from app.services.task_service import TaskService
from app.services.analytics import AnalyticsService
from app.api.auth import get_current_user
from app.models.task import User
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = TaskService(db)
    return service.create_task(task)

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = None,
    assignee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = TaskService(db)
    filters = TaskFilter(
        status=status,
        assignee_id=assignee_id
    )
    return service.get_tasks(filters)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = TaskService(db)
    updated_task = service.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = TaskService(db)
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")

@router.get("/analytics/statistics")
def get_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AnalyticsService(db)
    return service.get_statistics()

@router.get("/analytics/chart")
def get_status_chart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AnalyticsService(db)
    chart_path = service.create_status_chart()
    
    with open(chart_path, "rb") as image_file:
        return StreamingResponse(
            io.BytesIO(image_file.read()),
            media_type="image/png"
        )

@router.get("/analytics/export")
def export_to_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AnalyticsService(db)
    df = service.get_dataframe()
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return StreamingResponse(
        iter([csv_buffer.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"}
    )