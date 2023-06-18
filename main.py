from fastapi import FastAPI, Request, status
from app.coffee import router as coffee_router
from load_balancer import redirect_request
from typing import Callable


app = FastAPI()
@app.middleware("http")
async def load_balance_middleware(request: Request, call_next: Callable):
    response = await call_next(request)
    if response.status_code == 200:
        return response
    else:
        return redirect_request(request)
       
app.include_router(coffee_router)