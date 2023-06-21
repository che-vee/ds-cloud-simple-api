from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from .auth import authenticate
from .models import User
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from .database import SessionLocal

router = APIRouter()

def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_user_favourite_coffee(username: str, session: Session):
    return session.query(User).filter(User.username == username).first()

def get_favourite_coffees_count(session: Session):
    result = (
        session.query(User.favourite_coffee, func.count(User.favourite_coffee))
        .group_by(User.favourite_coffee)
        .order_by(func.count(User.favourite_coffee).desc())
        .limit(3)
        .all()
    )
    return [coffee for coffee, _ in result]

@router.get("/health")
def health_check():
    return {"status": "OK"}

@router.get("/v1/coffee/favourite", dependencies=[Depends(authenticate)])
def get_favourite_coffee(user: str = Depends(authenticate), session: Session = Depends(get_db_session)):
    result = get_user_favourite_coffee(user, session)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No favorite coffee yet.")
    return {"data": {"favourite_coffee": result.favourite_coffee}}

@router.get("/v1/admin/coffee/favourite/leaderboard", dependencies=[Depends(authenticate)])
def get_leaderboard(session: Session = Depends(get_db_session)):
    top_three = get_favourite_coffees_count(session)
    return {"data": {"top_three": top_three}}

@router.post("/v1/coffee/favourite", status_code=status.HTTP_201_CREATED, dependencies=[Depends(authenticate)])
def set_favourite_coffee(body: Dict[str, str], user: str = Depends(authenticate), session: Session = Depends(get_db_session)):
    favourite_coffee = body.get("favourite_coffee")
    if not favourite_coffee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Favourite coffee not provided.")

    user_data = get_user_favourite_coffee(user, session)
    if user_data:
        user_data.favourite_coffee = favourite_coffee
    else:
        new_user = User(username=user, favourite_coffee=favourite_coffee)
        session.add(new_user)

    session.commit()

    top_three = get_favourite_coffees_count(session)
    return {"data": {"favourite_coffee": favourite_coffee, "top_three": top_three}}
