from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
import app.models

from app.api.v1.router import api_router
from app.models import booking

app = FastAPI(title="Travel Agency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Travel Agency API!",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

Base.metadata.create_all(bind=engine)
