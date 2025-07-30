"""Routes for CRUD operations on tasks."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api import models, schemas, auth, database

from typing import List, Optional

router = APIRouter(prefix="/tasks", tags=["tasks"])

# PUBLIC_INTERFACE
@router.post("/", response_model=schemas.TaskRead, summary="Create a task")
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new task for the authenticated user."""
    async with db.begin():
        task_obj = models.Task(
            title=task.title,
            description=task.description,
            owner_id=current_user.id
        )
        db.add(task_obj)
        await db.flush()
        await db.refresh(task_obj)
        return task_obj

# PUBLIC_INTERFACE
@router.get("/", response_model=List[schemas.TaskRead], summary="List tasks", description="Get list of the current user's tasks. Optionally filter by completion status.")
async def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """List the current user's tasks, with optional filtering."""
    stmt = select(models.Task).where(models.Task.owner_id == current_user.id)
    if completed is not None:
        stmt = stmt.where(models.Task.completed == completed)
    results = await db.execute(stmt)
    tasks = results.scalars().all()
    return tasks

# PUBLIC_INTERFACE
@router.get("/{task_id}", response_model=schemas.TaskRead, summary="Get a task by ID")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get a task by ID."""
    result = await db.execute(
        select(models.Task).where(models.Task.id == task_id, models.Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# PUBLIC_INTERFACE
@router.patch("/{task_id}", response_model=schemas.TaskRead, summary="Update a task")
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update a task."""
    q = await db.execute(
        select(models.Task).where(models.Task.id == task_id, models.Task.owner_id == current_user.id)
    )
    task = q.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task

# PUBLIC_INTERFACE
@router.delete("/{task_id}", response_model=dict, summary="Delete a task")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a task."""
    q = await db.execute(
        select(models.Task).where(models.Task.id == task_id, models.Task.owner_id == current_user.id)
    )
    task = q.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return {"ok": True}
