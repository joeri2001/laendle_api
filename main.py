from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import schedule
import time
from threading import Thread
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
PLACE_ID = os.getenv('PLACE_ID')
GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

cache = {
    "data": None,
    "expiry": datetime.min
}

def fetch_place_details():
    params = {
        'place_id': PLACE_ID,
        'fields': 'name,rating,reviews',
        'language': 'de',
        'key': GOOGLE_MAPS_API_KEY
    }

    async def fetch():
        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_MAPS_API_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                cache["data"] = data
                cache["expiry"] = datetime.now() + timedelta(hours=24)
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch place details")

    import asyncio
    asyncio.run(fetch())

def schedule_jobs():
    schedule.every(24).hours.do(fetch_place_details)
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = Thread(target=schedule_jobs, daemon=True)
scheduler_thread.start()

@app.get("/laendle")
async def get_place_details():
    if cache["data"] is None or datetime.now() > cache["expiry"]:
        fetch_place_details()
    
    if cache["data"]:
        return cache["data"]
    else:
        raise HTTPException(status_code=500, detail="No data available, please try again later.")
