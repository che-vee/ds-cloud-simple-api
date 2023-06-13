from fastapi import FastAPI
from app.coffee import router as coffee_router

app = FastAPI()

app.include_router(coffee_router)