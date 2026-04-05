from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tasks_router, auth_router
from app.database import Base, engine

app = FastAPI(
    title="Task Tracker API",
    description="API для управления задачами",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Task Tracker API", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}