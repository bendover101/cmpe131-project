from fastapi import APIRouter, HTTPException, Query
import httpx
import os
from datetime import datetime

router = APIRouter()

@router.get("/hostels")
async def search_hostels(
    destination: str = Query(..., description="City or location name, e.g. London, New York"),
    checkin: str = Query(..., description="Format: YYYY-MM-DD"),
    checkout: str = Query(..., description="Format: YYYY-MM-DD"),
    agency_id: str = Query(..., description="Agency ID")
):
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    if not rapidapi_key:
        raise HTTPException(status_code=500, detail="API Key missing")

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    async with httpx.AsyncClient() as client:
        try:
           
            loc_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
            loc_response = await client.get(loc_url, headers=headers, params={"query": destination})
            loc_response.raise_for_status()
            loc_data = loc_response.json()

           
            dest_id = None
            for item in loc_data.get("data", []):
                if item.get("dest_type") == "city":
                    dest_id = item.get("dest_id")
                    break
            
            if not dest_id:
                return {"error": "Could not find a valid destination ID for that city."}

            hotel_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
            
            
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
            total_nights = (checkout_date - checkin_date).days

            hotel_query = {
                "dest_id": dest_id,
                "search_type": "city",
                "arrival_date": checkin,
                "departure_date": checkout,
                "sort_by": "PRICE" 
            }

            hotel_response = await client.get(hotel_url, headers=headers, params=hotel_query)
            hotel_response.raise_for_status()
            raw_hotel_data = hotel_response.json()

            processed_hotels = []
            
   
            properties = raw_hotel_data.get("data", {}).get("hotels", []) 
            
            for prop in properties:
                hotel_name = prop.get("property", {}).get("name", "")
                if "Student" in hotel_name and agency_id != "StudentTrips":
                    continue
                total_price = prop.get("property", {}).get("priceBreakdown", {}).get("grossPrice", {}).get("value", 0)
                
                processed_hotels.append({
                    "hotel_name": hotel_name,
                    "total_stay_price": round(total_price, 2),
                    "price_per_night": round(total_price / total_nights, 2) if total_nights > 0 else total_price,
                    "currency": "USD"
                })

            return {
                "agency": agency_id,
                "nights": total_nights,
                "results": processed_hotels
            }

        except httpx.HTTPStatusError as e:
            return {"error": f"API Error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            return {"error": "An unexpected error occurred processing the data."}