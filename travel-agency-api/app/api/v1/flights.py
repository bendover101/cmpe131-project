import os
from fastapi import APIRouter, HTTPException
from amadeus import Client

from app.services.travel_service import TravelService

router = APIRouter()

amadeus_client = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID", ""),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET", "")
)
travel_service = TravelService(amadeus_client)

@router.get("/flights")
@router.get("/flights/search")
async def search_flights(origin: str, destination: str, departure_date: str):
    """Fetches live flight data from the Amadeus API."""
    try:
        flight_data = travel_service.search_flights(
            origin=origin, 
            destination=destination, 
            date=departure_date
        )
        
        return {"results": flight_data}
        
    except Exception as e:
        print(f"Amadeus API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch live flights from Amadeus")