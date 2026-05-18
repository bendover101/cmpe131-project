from fastapi import APIRouter
from app.api.v1.endpoints import travel, booking, rapidapi, attractions, users
from app.api.v1 import hostels, flights 

api_router = APIRouter()

api_router.include_router(travel.router, prefix="/travel", tags=["travel"])
api_router.include_router(booking.router, prefix="/bookings", tags=["booking"])
api_router.include_router(rapidapi.router, prefix="/rapidapi", tags=["rapidapi"])
api_router.include_router(attractions.router, prefix="/attractions", tags=["attractions"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(hostels.router, tags=["search"])
api_router.include_router(flights.router, tags=["search"])