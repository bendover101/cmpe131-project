from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/flights")
@router.get("/flights/search")
async def search_flights(request: Request):
    return {
        "results": [
            {
                "airline": "United Airlines", "airline_code": "United Airlines", 
                "price": 450.50, "total_price": 450.50, "Rate": 450.50,
                "currency": "USD", "departure_time": "2026-06-01T08:00:00"
            },
            {
                "airline": "American Airlines", "airline_code": "American Airlines", 
                "price": 320.00, "total_price": 320.00, "Rate": 320.00,
                "currency": "USD", "departure_time": "2026-06-01T10:30:00"
            },
            {
                "airline": "Delta Air Lines", "airline_code": "Delta Air Lines", 
                "price": 510.75, "total_price": 510.75, "Rate": 510.75,
                "currency": "USD", "departure_time": "2026-06-01T14:15:00"
            },
            {
                "airline": "Southwest", "airline_code": "Southwest", 
                "price": 289.99, "total_price": 289.99, "Rate": 289.99,
                "currency": "USD", "departure_time": "2026-06-01T18:45:00"
            }
        ]
    }