"""Routes for user registration and authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.api import models, schemas, auth, database

router = APIRouter(prefix="/auth", tags=["auth"])

# PUBLIC_INTERFACE
@router.post("/register", response_model=schemas.UserRead, summary="Register new user", description="Create a new user account")
async def register(user_create: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    """Register a new user."""
    async with db.begin():
        q = await db.execute(models.User.__table__.select().where(models.User.email == user_create.email))
        user = q.first()
        if user is not None:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = auth.get_password_hash(user_create.password)
        user_obj = models.User(email=user_create.email, hashed_password=hashed_password)
        db.add(user_obj)
        await db.flush()  # So we can retrieve the ID
        await db.refresh(user_obj)
        return user_obj

# PUBLIC_INTERFACE
@router.post("/token", summary="Login and receive JWT token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_db)):
    """Get JWT token by email and password."""
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# PUBLIC_INTERFACE
@router.get("/me", response_model=schemas.UserRead, summary="Get current user")
async def get_current_user(current_user: models.User = Depends(auth.get_current_user)):
    """Return info for the currently logged-in user."""
    return current_user
