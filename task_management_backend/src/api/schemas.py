"""Pydantic schemas for API."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import datetime

# User schemas

# PUBLIC_INTERFACE
class UserBase(BaseModel):
    email: EmailStr

# PUBLIC_INTERFACE
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

# PUBLIC_INTERFACE
class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

# Task schemas

# PUBLIC_INTERFACE
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

# PUBLIC_INTERFACE
class TaskCreate(TaskBase):
    pass

# PUBLIC_INTERFACE
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# PUBLIC_INTERFACE
class TaskRead(TaskBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
