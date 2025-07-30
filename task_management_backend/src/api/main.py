from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes_auth import router as auth_router
from src.api.routes_tasks import router as tasks_router

app = FastAPI(
    title="Task Management Backend",
    description="Handles business logic and exposes RESTful APIs for user authentication and task management.",
    version="0.1.0",
    openapi_tags=[
        {"name": "auth", "description": "User registration, authentication & current user info"},
        {"name": "tasks", "description": "CRUD operations for tasks"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/", tags=["health"])
def health_check():
    """Check API health."""
    return {"message": "Healthy"}
