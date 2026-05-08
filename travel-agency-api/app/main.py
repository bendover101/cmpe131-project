from fastapi import FastAPI
from app.core.database import engine, Base
from app.core.database import Base  
import app.models

from app.api.v1.router import api_router
from app.models import booking

app = FastAPI(title="Travel Agency API")
app.include_router(api_router, prefix="/api/v1")
Base.metadata.create_all(bind=engine)
