from fastapi import APIRouter, Request

router = APIRouter()

# Catches BOTH possible UI requests
@router.get("/hostels")
@router.get("/hotels/search")
async def search_hostels(request: Request):
    return {
        "results": [
            {"hotel_name": "The Hive Kensington", "price": 120.50, "currency": "USD", "rating": 4.5},
            {"hotel_name": "Royal National Hotel", "price": 95.00, "currency": "USD", "rating": 3.8},
            {"hotel_name": "Generator London", "price": 45.00, "currency": "USD", "rating": 4.1}
        ]
    }