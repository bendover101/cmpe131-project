from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.booking import User

router = APIRouter()

@router.get("/login")
def login_user(
    email: str = Query(...),
    password: str = Query(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.Email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.Password and user.Password != password:
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return {
        "user_id": user.User_ID,
        "first_name": user.First_Name,
        "last_name": user.Last_Name,
        "email": user.Email
    }
