import asyncio
import os
import sys

# Add the app directory to the path so we can import the client
sys.path.insert(0, os.path.abspath('travel-agency-api'))

from app.core.rapidapi_client import RapidApiClient

async def main():
    client = RapidApiClient(api_key=os.getenv("RAPIDAPI_KEY", "4421695e4emshdbbd1ffa0344322p19d73djsn4990b49848a4"))
    try:
        # First test a normal 3-day stay
        print("Testing 66 day stay in New York...")
        res = client.search_hotels(
            page_number=1,
            dest_type="city",
            dest_name="New York",
            units="metric",
            children_number=0,
            locale="en-gb",
            include_adjacency=True,
            filter_by_currency="USD",
            order_by="popularity",
            checkin_date="2026-06-01",
            checkout_date="2026-08-06",
            room_number=1,
            adults_number=1
        )
        print("RAW RESPONSE:")
        import json
        print(json.dumps(res, indent=2))
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
