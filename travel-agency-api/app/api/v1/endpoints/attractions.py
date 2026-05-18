from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter()

MOCK_ATTRACTIONS = [
    {
        "id": 1,
        "name": "London Royal Palaces Free Walking Tour",
        "location": "London",
        "price_type": "Free",
        "rate": 0.0,
        "price": 0.0,
        "category": "Culture",
        "duration": "2 hours",
        "rating": 4.8,
        "reviews": 124,
        "description": "Walk through the royal history of London's palaces and parks."
    },
    {
        "id": 2,
        "name": "Jack the Ripper Pay-What-You-Want Tour",
        "location": "London",
        "price_type": "Pay what you want",
        "rate": 0.0,
        "price": 0.0,
        "category": "Adventure",
        "duration": "2.5 hours",
        "rating": 4.6,
        "reviews": 89,
        "description": "Explore the historic mystery in Whitechapel with a dynamic guide."
    },
    {
        "id": 3,
        "name": "London Eye Standard Ticket",
        "location": "London",
        "price_type": "Fixed",
        "rate": 45.0,
        "price": 45.0,
        "category": "Sightseeing",
        "duration": "0.5 hours",
        "rating": 4.7,
        "reviews": 4120,
        "description": "Experience breathtaking 360-degree views of London from 135 meters high."
    },
    {
        "id": 4,
        "name": "Central Park Free Guided Walk",
        "location": "New York",
        "price_type": "Free",
        "rate": 0.0,
        "price": 0.0,
        "category": "Nature",
        "duration": "1.5 hours",
        "rating": 4.9,
        "reviews": 340,
        "description": "Discover Central Park's history, design, and famous landmarks."
    }
]

@router.get("/search")
async def search_attractions(
    city: Optional[str] = Query(None, description="City or location name, e.g. London, New York"),
    dest_name: Optional[str] = Query(None, description="City or location name, e.g. London, New York"),
    price_type: Optional[str] = Query(None, description="Filter by price type, e.g. Free, Pay what you want, Fixed")
):
    search_city = city or dest_name or "london"
    
    results = [
        attraction for attraction in MOCK_ATTRACTIONS 
        if search_city.lower() in attraction["location"].lower()
    ]
    
    if price_type:
        results = [
            attraction for attraction in results 
            if price_type.lower() == attraction["price_type"].lower()
        ]
        
    return {"results": results}
