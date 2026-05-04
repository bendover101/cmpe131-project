from fastapi import APIRouter, Request

router = APIRouter(prefix="", tags=["booking"])

@router.post("")
@router.post("/")
async def create_booking(request: Request):
    return {"message": "Booking successfully saved!", "status": "success"}

@router.get("/by-agent-user")
async def get_user_bookings(user_id: int = 1, agency_id: str = "agenta"):
    return [
        {
            "id": 101,
            "booking_type": "Hotel",
            "provider": "The Hive Kensington",
            "details": "3 Nights - Standard Room",
            "total_price": 361.50,
            "currency": "USD",
            "status": "CONFIRMED",
            "booking_date": "2026-05-01"
        },
        {
            "id": 102,
            "booking_type": "Flight",
            "provider": "United Airlines",
            "details": "SFO to CDG - Economy",
            "total_price": 450.50,
            "currency": "USD",
            "status": "CONFIRMED",
            "booking_date": "2026-05-01"
        }
    ]
