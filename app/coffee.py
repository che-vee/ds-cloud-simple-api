from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from .auth import authenticate
import json

router = APIRouter()

DB_FILE = "./database.json"

def read_data():
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    return data

def write_data(data: dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

@router.get("/v1/coffee/favourite", dependencies=[Depends(authenticate)])
def get_favourite_coffee(user: str = Depends(authenticate)):
    data = read_data()

    if not data["users"].get(user) or not data["users"][user].get("favourite_coffee"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No favourite cofee yet.")

    return {"data": {"favourite_coffee": data["users"][user]["favourite_coffee"]}}

@router.get("/v1/admin/coffee/favourite/leaderboard", dependencies=[Depends(authenticate)])
def get_leaderboard():
    data = read_data()
    top_three = sorted(data["top_three"], key=data["top_three"].get, reverse=True)[:3]
    return {"data": {"top_three": top_three}}

@router.post("/v1/coffee/favourite", status_code=status.HTTP_201_CREATED, dependencies=[Depends(authenticate)])
def set_favourite_coffee(body: Dict[str, str], user: str = Depends(authenticate)):
    data = read_data()

    favourite_coffee = body.get("favourite_coffee")
    if not favourite_coffee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Favourite coffee not provided.")

    data["users"][user]["favourite_coffee"] = favourite_coffee

    name = favourite_coffee
    current_count = data["top_three"].get(name, 0)
    data["top_three"][name] = current_count + 1

    write_data(data)

    top_three = sorted(data["top_three"], key=data["top_three"].get, reverse=True)[:3]

    return {"data": {"favourite_coffee": data["users"][user]["favourite_coffee"], "top_three": top_three}}
