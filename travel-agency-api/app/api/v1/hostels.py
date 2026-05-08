import os
from fastapi import APIRouter, HTTPException

from app.core.rapidapi_client import RapidApiClient
from app.services.rapidapi_service import RapidApiService

router = APIRouter()

rapidapi_client = RapidApiClient(
    api_key=os.getenv("RAPIDAPI_KEY", ""),
    api_host=os.getenv("RAPIDAPI_HOST", "booking-com15.p.rapidapi.com")
)
rapidapi_service = RapidApiService(rapidapi_client)

@router.get("/hostels")
@router.get("/hotels/search")
async def search_hostels(destination: str, checkin: str, checkout: str):
    """Fetches live hotel data from RapidAPI."""
    try:
        hotel_data = rapidapi_service.search_hotels(
            dest_name=destination,
            checkin_date=checkin,
            checkout_date=checkout,
            page_number=0,
            dest_type="city",
            country_name="", 
            units="metric",
            children_number=0,
            locale="en-gb",
            include_adjacency=True,
            filter_by_currency="USD",
            order_by="popularity",
            room_number=1,
            adults_number=1
        )
        
        
        extracted_hotels = hotel_data.get("data", {}).get("hotels", []) if isinstance(hotel_data, dict) else []
        
        return {"results": extracted_hotels}
        
    except Exception as e:
        print(f"RapidAPI Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch live hotels from RapidAPI")