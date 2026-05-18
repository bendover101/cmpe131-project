from functools import lru_cache
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import get_settings


class RapidApiError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class RapidApiClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search_hotels(
        self,
        page_number: int,
        dest_type: str,
        dest_name: str,
        units: str,
        children_number: int,
        locale: str,
        include_adjacency: bool,
        filter_by_currency: str,
        order_by: str,
        checkin_date: str,
        checkout_date: str,
        room_number: int,
        adults_number: int,
        categories_filter_ids: str | None = None,
        children_ages: str | None = None,
    ):
        dest_id = self._resolve_city_dest_id(dest_name=dest_name)

        querystring = {
            "page_number": str(page_number + 1),
            "dest_id": dest_id,
            "search_type": dest_type.upper(),
            "units": units,
            "languagecode": locale,
            "currency_code": filter_by_currency,
            "arrival_date": checkin_date,
            "departure_date": checkout_date,
            "room_qty": str(room_number),
            "adults": str(adults_number),
            "sort_by": order_by,
        }

        if children_number is not None and children_number >= 1:
            if children_ages:
                querystring["children_age"] = children_ages.replace(" ", "")

        return self._get(
            host="booking-com15.p.rapidapi.com",
            path="api/v1/hotels/searchHotels",
            params=querystring,
        )

    def _resolve_city_dest_id(self, dest_name: str) -> str:
        response = self._get(
            host="booking-com15.p.rapidapi.com",
            path="api/v1/hotels/searchDestination",
            params={"query": dest_name},
        )

        data = response.get("data", [])
        if not data:
            raise RapidApiError(
                404,
                f"No destination found for '{dest_name}'.",
            )

        # Try to find a city first
        for item in data:
            if item.get("search_type") == "city" and item.get("dest_id"):
                return str(item["dest_id"])

        # Fallback to the first item with a dest_id
        for item in data:
            if item.get("dest_id"):
                return str(item["dest_id"])

        raise RapidApiError(
            404,
            f"No destination id found for '{dest_name}'.",
        )

    def search_rental_cars(
        self,
        pick_up_date: str,
        drop_off_date: str,
        pick_up_time: str,
        drop_off_time: str,
    ):
        querystring = {
            "pick_up_latitude": "40.6397018432617",
            "pick_up_longitude": "-73.7791976928711",
            "drop_off_latitude": "40.6397018432617",
            "drop_off_longitude": "-73.7791976928711",
            "pick_up_date": pick_up_date,
            "drop_off_date": drop_off_date,
            "pick_up_time": pick_up_time,
            "drop_off_time": drop_off_time,
            "driver_age": "30",
            "currency_code": "USD",
            "location": "US",
        }
        return self._get(
            host="booking-com15.p.rapidapi.com",
            path="api/v1/cars/searchCarRentals",
            params=querystring,
        )

    def _resolve_flight_dest_id(self, dest_name: str) -> str:
        response = self._get(
            host="booking-com15.p.rapidapi.com",
            path="api/v1/flights/searchDestination",
            params={"query": dest_name},
        )

        data = response.get("data", [])
        if not data:
            raise RapidApiError(
                404,
                f"No flight destination found for '{dest_name}'.",
            )

        # Try to find an airport first
        for item in data:
            if item.get("type") == "AIRPORT" and item.get("id"):
                return str(item["id"])

        # Fallback to the first item with an id
        for item in data:
            if item.get("id"):
                return str(item["id"])

        raise RapidApiError(
            404,
            f"No flight destination id found for '{dest_name}'.",
        )

    def search_flights(
        self,
        depart_date: str,
        from_name: str,
        to_name: str,
        adults: int,
        locale: str = "en-gb",
        page_number: int = 0,
        currency: str = "AED",
        order_by: str = "BEST",
        flight_type: str = "ONEWAY",
        cabin_class: str = "ECONOMY",
        children_ages: str | None = None,
        return_date: str | None = None,
    ):
        from_id = self._resolve_flight_dest_id(from_name)
        to_id = self._resolve_flight_dest_id(to_name)

        querystring = {
            "departDate": depart_date,
            "fromId": from_id,
            "toId": to_id,
            "adults": str(adults),
            "pageNo": str(page_number + 1), # pageNo is 1-indexed in booking-com15
            "currency_code": currency,
            "sort": order_by,
            "cabinClass": cabin_class,
        }

        if children_ages:
            querystring["children"] = children_ages.replace(" ", "")

        if return_date:
            querystring["returnDate"] = return_date

        return self._get(
            host="booking-com15.p.rapidapi.com",
            path="api/v1/flights/searchFlights",
            params=querystring,
        )

    def _get(self, host: str, path: str, params: dict[str, str]):
        request = Request(
            f"https://{host}/{path}?{urlencode(params)}",
            headers={
                "x-rapidapi-host": host,
                "x-rapidapi-key": self.api_key,
                "Content-Type": "application/json",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RapidApiError(error.code, detail or str(error)) from error
        except URLError as error:
            raise RapidApiError(500, "Failed to connect to RapidAPI.") from error


@lru_cache(maxsize=1)
def get_rapidapi_client() -> RapidApiClient:
    settings = get_settings()
    if not settings.rapidapi_key:
        raise RapidApiError(500, "RAPIDAPI_KEY is not configured.")

    return RapidApiClient(api_key=settings.rapidapi_key)