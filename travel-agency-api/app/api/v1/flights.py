import os
from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.core.rapidapi_client import get_rapidapi_client, RapidApiError
from app.services.rapidapi_service import RapidApiService

router = APIRouter()

def extract_flight_list(data: dict) -> List[dict]:
    if not isinstance(data, dict):
        return []
    res_data = data.get("data", {})
    if not isinstance(res_data, dict):
        return []
    return res_data.get("flightOffers", res_data.get("flights", []))

def normalize_flight(item: dict, adults: int = 1) -> dict:
    if "segments" in item and "priceBreakdown" in item:
        segments = item.get("segments", [])
        first_seg = segments[0] if segments else {}
        legs = first_seg.get("legs", []) if isinstance(first_seg, dict) else []
        first_leg = legs[0] if legs else {}
        
        carrier_data = first_leg.get("carriersData", [{}])[0] if isinstance(first_leg, dict) else {}
        airline_name = carrier_data.get("name", "United Airlines")
        airline_code = carrier_data.get("code", "UA")
        
        flight_num = first_leg.get("flightInfo", {}).get("flightNumber", "100")
        full_flight_number = f"{airline_code} {flight_num}"
        
        dep_airport = first_leg.get("departureAirport", {})
        origin_code = dep_airport.get("code", "SFO")
        
        arr_airport = first_leg.get("arrivalAirport", {})
        destination_code = arr_airport.get("code", "JFK")
        
        dep_time_raw = first_leg.get("departureTime", "")
        dep_time = dep_time_raw.split("T")[1][:5] if "T" in dep_time_raw else dep_time_raw
        
        arr_time_raw = first_leg.get("arrivalTime", "")
        arr_time = arr_time_raw.split("T")[1][:5] if "T" in arr_time_raw else arr_time_raw
        
        total_time_sec = first_leg.get("totalTime", 0)
        if total_time_sec:
            h = total_time_sec // 3600
            m = (total_time_sec % 3600) // 60
            duration = f"{h}h {m}m"
        else:
            duration = "5h 30m"
            
        stops = len(legs) - 1 if legs else 0
        
        price_bd = item.get("priceBreakdown", {})
        total_obj = price_bd.get("total", {})
        total_units = total_obj.get("units", 0)
        total_nanos = total_obj.get("nanos", 0)
        total_price = round(float(total_units) + float(total_nanos) * 1e-9, 2)
        
        if not total_price:
            total_rounded = price_bd.get("totalRounded", {})
            total_price = float(total_rounded.get("units", 0))
            
        price_per_person = round(total_price / max(1, adults), 2)
        cabin_info = first_leg.get("cabinClass", "ECONOMY").capitalize()
        
        return {
            "id": str(item.get("token") or item.get("flightKey") or full_flight_number),
            "airline": airline_name,
            "airlineCode": airline_code,
            "flightNumber": full_flight_number,
            "aircraft": first_leg.get("flightInfo", {}).get("planeType", "Boeing 737") or "Boeing 737",
            "origin": origin_code,
            "destination": destination_code,
            "departureTime": dep_time or "N/A",
            "arrivalTime": arr_time or "N/A",
            "duration": duration,
            "stops": max(0, int(stops)),
            "class": cabin_info,
            "totalPrice": total_price,
            "pricePerPerson": price_per_person,
            "seatsAvailable": None,
            "_raw_departure_date": dep_time_raw,
            "_raw_arrival_date": arr_time_raw,
        }

    bounds = item.get("bounds", [])
    first_seg = {}
    last_seg = {}
    stops = 0

    if bounds and isinstance(bounds, list):
        bound = bounds[0]
        segments = bound.get("segments", [])
        if segments and isinstance(segments, list):
            first_seg = segments[0]
            last_seg = segments[-1]
            stops = len(segments) - 1

    carrier = first_seg.get("carrier", {})
    airline_name = carrier.get("name", item.get("airline", "United Airlines"))
    airline_code = carrier.get("code", item.get("airlineCode", "UA"))

    f_num = first_seg.get("flightNumber", item.get("flightNumber", "100"))
    if str(f_num).upper().startswith(str(airline_code).upper()):
        full_flight_number = f_num
    else:
        full_flight_number = f"{airline_code} {f_num}"

    dep_airport = first_seg.get("departureAirport", {})
    origin_code = dep_airport.get("code", item.get("origin", "SFO"))

    arr_airport = last_seg.get("arrivalAirport", {})
    destination_code = arr_airport.get("code", item.get("destination", "LAX"))

    dep_time_raw = first_seg.get("departureTime", "")
    dep_time = dep_time_raw.split("T")[1][:5] if "T" in dep_time_raw else dep_time_raw

    arr_time_raw = last_seg.get("arrivalTime", "")
    arr_time = arr_time_raw.split("T")[1][:5] if "T" in arr_time_raw else arr_time_raw

    duration = item.get("duration", "3h 30m")

    price_detail = item.get("priceDetail", {})
    total_price_obj = price_detail.get("total", {})
    raw_price = (
        total_price_obj.get("amount") or
        item.get("price") or
        item.get("totalPrice") or
        0
    )
    total_price = round(float(raw_price or 0), 2)
    adults_count = max(1, int(adults))
    price_per_person = round(total_price / adults_count, 2) if total_price else 0

    cabin_info = item.get("cabinClassText", item.get("cabinClass", "Economy"))

    return {
        "id": str(item.get("token") or item.get("id") or item.get("offerId") or full_flight_number),
        "airline": airline_name,
        "airlineCode": airline_code,
        "flightNumber": full_flight_number,
        "aircraft": first_seg.get("aircraft", {}).get("type", "") if isinstance(first_seg.get("aircraft"), dict) else "",
        "origin": origin_code,
        "destination": destination_code,
        "departureTime": dep_time or "N/A",
        "arrivalTime": arr_time or "N/A",
        "duration": duration,
        "stops": max(0, int(stops)),
        "class": cabin_info,
        "totalPrice": total_price,
        "pricePerPerson": price_per_person,
        "seatsAvailable": item.get("seatsLeft", item.get("seatsAvailable", None)),
        "_raw_departure_date": first_seg.get("departureTime", ""),
        "_raw_arrival_date": last_seg.get("arrivalTime", ""),
    }

@router.get("/flights")
@router.get("/flights/search")
async def search_flights(
    origin: str = Query(..., description="Airport name such as JFK, SFO, etc"),
    destination: str = Query(..., description="Airport name such as LHR, DXB, etc"),
    departure_date: str = Query(..., description="Format: YYYY-MM-DD"),
    adults: int = Query(1, description="Number of adult passengers"),
):
    try:
        service = RapidApiService(get_rapidapi_client())
        raw_data = service.search_flights(
            depart_date=departure_date,
            from_name=origin,
            to_name=destination,
            adults=adults,
            locale="en-gb",
            page_number=0,
            currency="USD",
            order_by="BEST",
            flight_type="ONEWAY",
            cabin_class="ECONOMY",
        )
        flights = extract_flight_list(raw_data)
        normalized = [normalize_flight(f, adults=adults) for f in flights]
        return {"results": normalized}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch live flights: {str(e)}")