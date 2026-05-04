from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/attractions")
@router.get("/attractions/search")
async def search_attractions(request: Request):
    return {
        "results": [
            {"name": "Eiffel Tower Guided Tour", "price": 45.00, "currency": "USD", "rating": 4.8},
            {"name": "Louvre Museum Entry", "price": 20.00, "currency": "USD", "rating": 4.9},
            {"name": "Seine River Cruise", "price": 15.00, "currency": "USD", "rating": 4.6}
        ]
    }