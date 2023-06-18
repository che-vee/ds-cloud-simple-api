from typing import List
from itertools import cycle
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

APP_URLS = [
    "http://localhost:8081",
    "http://localhost:8082",
    "http://localhost:8083",
]

app_urls_cycle = cycle(APP_URLS)

def check_health_stat(url: str):
    try:
        response = requests.get(f"{url}/health")
        if response.status_code == 200:
            logging.info(f"Health check passed for app instance: {url}")
            return True
    except requests.RequestException as e:
        logging.warning(f"Health check failed for app instance: {url}. Error: {str(e)}")
    return False

def get_next_app_url():
    for _ in range(len(APP_URLS)):
        next_app_url = next(app_urls_cycle)
        if check_health_stat(next_app_url):
            return next_app_url
        
    logging.error("No healthy apps available.")
    raise HTTPException(status_code=503, detail="No healthy apps available.")

def redirect_request(request: Request):
    try:
        request_path = request.url.path
        next_app_url = get_next_app_url()
        redirect_url = f"{next_app_url}{request_path}"

        logging.info(f"Redirecting request to: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=307)
    except Exception as e:
        logging.error(f"Error during request redirection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")