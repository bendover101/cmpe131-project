from app.core.database import SessionLocal, Base, engine
from app.models.booking import User
import app.models

def seed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if user 0 exists
    user0 = db.query(User).filter(User.User_ID == 0).first()
    if not user0:
        print("Creating User 0...")
        u0 = User(User_ID=0, First_Name="Test", Last_Name="User Zero", Email="user0@example.com", Password="password")
        db.add(u0)
    else:
        user0.Password = "password"
        
    user1 = db.query(User).filter(User.User_ID == 1).first()
    if not user1:
        print("Creating User 1...")
        u1 = User(User_ID=1, First_Name="Test", Last_Name="User One", Email="user1@example.com", Password="password")
        db.add(u1)
    else:
        user1.Password = "password"
        
    db.commit()
    db.close()
    print("Database seeded with test users!")

if __name__ == "__main__":
    seed_users()
