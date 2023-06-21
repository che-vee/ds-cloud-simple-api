from fastapi import FastAPI
from app.coffee import router as coffee_router
from app.models import User
from app.database import SessionLocal, Base, engine
from sqlalchemy.orm import Session

app = FastAPI()

app.include_router(coffee_router)

def create_tables():
    Base.metadata.create_all(bind=engine)

def seed_data():
    session = SessionLocal()

    users = [
        {"username": "user1", "favourite_coffee": "espresso"},
        {"username": "user2", "favourite_coffee": "latte"},
        {"username": "user3", "favourite_coffee": "cappuccino"},
        {"username": "user4", "favourite_coffee": "cappuccino"},
        {"username": "user5", "favourite_coffee": "latte"},
        {"username": "user6", "favourite_coffee": "espresso"},
        {"username": "user7", "favourite_coffee": "americano"}
    ]

    for user in users:
        existing_user = session.query(User).filter(User.username == user["username"]).first()
        if not existing_user:
            user_obj = User(username=user["username"], favourite_coffee=user["favourite_coffee"])
            session.add(user_obj)

    session.commit()
    session.close()

@app.on_event("startup")
async def startup_event():
    create_tables()
    seed_data()