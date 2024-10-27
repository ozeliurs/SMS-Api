import time

from fastapi import FastAPI, HTTPException, Security, Depends, BackgroundTasks
from pydantic import BaseModel
from sms_sender import SMSSender
from config import BASE_URL, PASSWORD, API_KEY
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()

# Initialize the SMS sender once
sms_sender = SMSSender(BASE_URL, PASSWORD)

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key_header

class SMSRequest(BaseModel):
    phone_number: str
    message: str

def send_sms_task(phone_number: str, message: str) -> dict:
    start_time = time.time()
    result = sms_sender.send_sms(phone_number, message)
    result['elapsed_time'] = time.time() - start_time
    return result

@app.post("/send-sms")
async def send_sms(sms_request: SMSRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    background_tasks.add_task(send_sms_task, sms_request.phone_number, sms_request.message)
    return {"status": "accepted", "message": "SMS sending task has been queued"}

@app.on_event("shutdown")
def shutdown_event():
    # Clean up the browser when the application shuts down
    if hasattr(sms_sender, 'driver'):
        sms_sender.driver.quit()
