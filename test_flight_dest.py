import os
import sys
import httpx
import asyncio

async def test():
    key = os.getenv("RAPIDAPI_KEY", "4421695e4emshdbbd1ffa0344322p19d73djsn4990b49848a4")
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    async with httpx.AsyncClient() as client:
        print("Testing flight destination SFO...")
        url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchDestination"
        resp = await client.get(url, headers=headers, params={"query": "SFO"})
        print(resp.status_code)
        print(resp.text[:500])
        
        print("\nTesting flight destination London...")
        resp = await client.get(url, headers=headers, params={"query": "London"})
        print(resp.status_code)
        print(resp.text[:500])

if __name__ == "__main__":
    asyncio.run(test())
