from fastapi import FastAPI
from typing import Dict
import boto3
import os
import threading
import time

def send_message(msg: Dict[str, str]):
    sqs = boto3.client(
        "sqs",
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    sqs.send_message(QueueUrl=os.getenv("QUEUE_URL"), MessageBody=str(msg))

def consume_messages():
    sqs = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

    while True:
        response = sqs.receive_message(
            QueueUrl=os.getenv("QUEUE_URL"),
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5,
    )
        messages = response.get("Messages")
        
        if messages:
            for msg in messages:
                print(f"Message processed: {msg['Body']}")

                receipt_handle = msg["ReceiptHandle"]
                sqs.delete_message(
                    QueueUrl=os.getenv("QUEUE_URL"), ReceiptHandle=receipt_handle
                )
        else:
            time.sleep(3)

consumer_thread = threading.Thread(target=consume_messages, daemon=True)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    consumer_thread.start()
