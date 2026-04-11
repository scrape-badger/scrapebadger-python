"""Google Flights client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from scrapebadger._internal.client import BaseClient


TripType = Literal["round_trip", "one_way", "multi_city"]
TravelClass = Literal["economy", "premium_economy", "business", "first"]
StopsFilter = Literal["any", "nonstop", "one_stop", "two_stops"]


class FlightsClient:
    """Client for Google Flights search.

    Supports one-way, round-trip, and multi-city itineraries with
    passenger configuration, cabin class, stops filter, and max-price.
    Returns Google's Best flights recommendations plus the full Other
    flights result set, with per-offer pricing, duration, stops,
    layovers, carbon emissions, and price insights (low / typical /
    high + typical price range) when Google shows them.

    Example:
        ```python
        flights = await client.google.flights.search(
            departure_id="JFK",
            arrival_id="LHR",
            outbound_date="2026-06-15",
            return_date="2026-06-22",
            adults=2,
        )
        for offer in flights["best_flights"]:
            print(offer["price"], offer["currency"], offer["total_duration_minutes"])
        if insights := flights.get("price_insights"):
            print("Price level:", insights["price_level"])
        ```
    """

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    async def search(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
        *,
        return_date: str | None = None,
        trip_type: TripType = "round_trip",
        adults: int = 1,
        children: int = 0,
        infants_in_seat: int = 0,
        infants_on_lap: int = 0,
        travel_class: TravelClass = "economy",
        currency: str = "USD",
        gl: str = "us",
        hl: str = "en",
        stops: StopsFilter = "any",
        max_price: int | None = None,
    ) -> dict[str, Any]:
        """Search Google Flights for available itineraries.

        Args:
            departure_id: Departure airport IATA code (e.g. "JFK") or
                location ID.
            arrival_id: Arrival airport IATA code or location ID.
            outbound_date: Outbound date in YYYY-MM-DD format.
            return_date: Return date (required for round_trip).
            trip_type: "round_trip" | "one_way" | "multi_city".
            adults: Adult passengers (1-9).
            children: Children passengers (0-8).
            infants_in_seat: Infants in seat (0-4).
            infants_on_lap: Infants on lap (0-4).
            travel_class: Cabin class.
            currency: ISO-4217 currency code (default "USD").
            gl: Country code.
            hl: Language code.
            stops: Max stops filter.
            max_price: Upper price filter.

        Returns:
            Response with `best_flights[]`, `other_flights[]`,
            `price_insights`, `airports[]`, and trip-type metadata.
        """
        params: dict[str, Any] = {
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "trip_type": trip_type,
            "adults": adults,
            "children": children,
            "infants_in_seat": infants_in_seat,
            "infants_on_lap": infants_on_lap,
            "travel_class": travel_class,
            "currency": currency,
            "gl": gl,
            "hl": hl,
            "stops": stops,
        }
        if return_date is not None:
            params["return_date"] = return_date
        if max_price is not None:
            params["max_price"] = max_price
        return await self._client.get("/v1/google/flights/search", params=params)
