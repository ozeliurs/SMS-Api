import time
import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException, Security, Depends, BackgroundTasks
from pydantic import BaseModel
from sms_sender import SMSSender
from config import BASE_URL, PASSWORD, API_KEY
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()

# Initialize the SMS sender once
sms_sender = SMSSender(BASE_URL, PASSWORD)

# Store for background tasks
task_store: Dict[str, dict] = {}

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key_header

class SMSRequest(BaseModel):
    phone_number: str
    message: str

def send_sms_task(job_id: str, phone_number: str, message: str):
    start_time = time.time()
    task_store[job_id]['status'] = 'processing'

    result = sms_sender.send_sms(phone_number, message)
    result['elapsed_time'] = time.time() - start_time

    task_store[job_id]['status'] = 'completed'
    task_store[job_id]['result'] = result

@app.post("/send-sms")
async def send_sms(sms_request: SMSRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    job_id = str(uuid.uuid4())
    task_store[job_id] = {'status': 'pending'}

    background_tasks.add_task(send_sms_task, job_id, sms_request.phone_number, sms_request.message)
    return {"status": "accepted", "job_id": job_id}

@app.get("/job/{job_id}")
async def get_job_status(job_id: str, api_key: str = Depends(get_api_key)):
    if job_id not in task_store:
        raise HTTPException(status_code=404, detail="Job not found")
    return task_store[job_id]

@app.on_event("shutdown")
def shutdown_event():
    # Clean up the browser when the application shuts down
    if hasattr(sms_sender, 'driver'):
        sms_sender.driver.quit()
