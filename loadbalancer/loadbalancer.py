from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from itertools import cycle

import logging
import requests
import time
import boto3
import os
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

APP_URLS = []

healthy_apps = []
app_urls_cycle = cycle(healthy_apps)

def get_healthy_apps():
    global healthy_apps, app_urls_cycle

    for app_url in APP_URLS:
        try:
            response = requests.get(f"{app_url}/health")
            if response.status_code == 200:
                logging.info(f"Health check passed for app instance: {app_url}")
                if app_url not in healthy_apps:
                    healthy_apps.append(app_url)
            else:
                if app_url in healthy_apps:
                    healthy_apps.remove(app_url) 
        except requests.RequestException as e:
            logging.warning(f"Health check failed for app instance: {app_url}. Error: {str(e)}")

    app_urls_cycle = cycle(healthy_apps)

        
def redirect_request(request: Request):
    if not healthy_apps:
        logging.error("No healthy apps available.")
        raise HTTPException(status_code=503, detail="No healthy apps available.")
    next_app_url = next(app_urls_cycle)
    try:
        request_path = request.url.path
        updated_url_for_docker_compose = next_app_url.replace("host.docker.internal", "localhost")
        redirect_url = f"{updated_url_for_docker_compose}{request_path}"

        logging.info(f"Redirecting request to: {redirect_url}")
        return RedirectResponse(url=redirect_url, status_code=307)
    except Exception as e:
        logging.error(f"Error during request redirection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    s3 = boto3.resource('s3', 
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    bucket_name = 'hosturls'
    object_key = 'hosts.json'

    try:
        obj = s3.Object(bucket_name, object_key)
        hosts_data = obj.get()['Body'].read().decode('utf-8')
        hosts_config = json.loads(hosts_data)
        
        APP_URLS.extend(hosts_config['urls'])

        get_healthy_apps()
        
        logging.info("Load balancer initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to fetch hosts configuration from S3: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.middleware("http")
async def load_balancer_middleware(request: Request, call_next):
    return redirect_request(request)

