from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Configure CORS
# origins = [
#     "https://laendle.joeribrinks.nl",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

# Define your Google Maps API key and endpoint
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
PLACE_ID = os.getenv('PLACE_ID')
GOOGLE_MAPS_API_URL = f'https://maps.googleapis.com/maps/api/place/details/json'

@app.get("/laendle")
async def get_place_details():
    params = {
        'place_id': PLACE_ID,
        'fields': 'name,rating,reviews',
        'language': 'de',
        'key': GOOGLE_MAPS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(GOOGLE_MAPS_API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch place details")