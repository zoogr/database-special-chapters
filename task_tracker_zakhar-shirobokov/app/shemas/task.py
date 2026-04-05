from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models.task import TaskStatus

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NEW
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    assignee: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None