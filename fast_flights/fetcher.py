from datetime import datetime as Datetime, timedelta, date as Date
from typing import overload

from primp import Client

from .integrations.base import Integration
from .parser import MetaList, parse
from .querying import Query, FlightQuery, create_query, Passengers, DEFAULT_PASSENGERS
from .types import SeatType, TripType

URL = "https://www.google.com/travel/flights"


@overload
def get_flights(q: str, /, *, proxy: str | None = None) -> MetaList:
    """Get flights using a str query.

    Examples:
    - *Flights from TPE to MYJ on 2025-12-22 one way economy class*
    """


@overload
def get_flights(q: Query, /, *, proxy: str | None = None) -> MetaList:
    """Get flights using a structured query.

    Example:
    ```python
    get_flights(
        query(
            flights=[
                FlightQuery(
                    date="2025-12-22",
                    from_airport="TPE",
                    to_airport="MYJ",
                )
            ],
            seat="economy",
            trip="one-way",
            passengers=Passengers(adults=1),
            language="en-US",
            currency="",
        )
    )
    ```
    """


def get_flights(
    q: Query | str,
    /,
    *,
    proxy: str | None = None,
    integration: Integration | None = None,
) -> MetaList:
    """Get flights.

    Args:
        q: The query.
        proxy (str, optional): Proxy.
    """
    html = fetch_flights_html(q, proxy=proxy, integration=integration)
    return parse(html)


def fetch_flights_html(
    q: Query | str,
    /,
    *,
    proxy: str | None = None,
    integration: Integration | None = None,
) -> str:
    """Fetch flights and get the **HTML**.

    Args:
        q: The query.
        proxy (str, optional): Proxy.
    """
    if integration is None:
        client = Client(
            impersonate="chrome_145",
            impersonate_os="macos",
            referer=True,
            proxy=proxy,
            cookie_store=True,
        )

        if isinstance(q, Query):
            params = q.params()

        else:
            params = {"q": q}

        res = client.get(URL, params=params)
        return res.text

    else:
        return integration.fetch_html(q)


def get_flights_by_period(
    from_airport: str,
    to_airport: str,
    date_from: str | Datetime,
    date_to: str | Datetime,
    *,
    seat: SeatType = "economy",
    trip: TripType = "one-way",
    passengers: Passengers = DEFAULT_PASSENGERS,
    language: str = "",
    currency: str = "",
    max_stops: int | None = None,
    proxy: str | None = None,
) -> dict[str, MetaList]:
    """Get flights for a date range.

    Args:
        from_airport: Departure airport code (IATA).
        to_airport: Arrival airport code (IATA).
        date_from: Start date (YYYY-MM-DD or datetime object).
        date_to: End date (YYYY-MM-DD or datetime object, inclusive).
        seat: Seat type.
        trip: Trip type.
        passengers: Passenger configuration.
        language: Language code.
        currency: Currency code.
        max_stops: Maximum number of stops.
        proxy: Proxy URL.

    Returns:
        dict mapping date strings (YYYY-MM-DD) to flight results.
    """
    start = _parse_date(date_from)
    end = _parse_date(date_to)

    results: dict[str, MetaList] = {}
    current = start

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        query = create_query(
            flights=[
                FlightQuery(
                    date=date_str,
                    from_airport=from_airport,
                    to_airport=to_airport,
                    max_stops=max_stops,
                )
            ],
            seat=seat,
            trip=trip,
            passengers=passengers,
            language=language,
            currency=currency,
        )

        results[date_str] = get_flights(query, proxy=proxy)
        current += timedelta(days=1)

    return results


def get_flights_round_trip(
    from_airport: str,
    to_airport: str,
    date_from: str | Datetime,
    date_to: str | Datetime,
    *,
    seat: SeatType = "economy",
    passengers: Passengers = DEFAULT_PASSENGERS,
    language: str = "",
    currency: str = "",
    max_stops: int | None = None,
    proxy: str | None = None,
) -> MetaList:
    """Get round-trip flights.

    Args:
        from_airport: Departure airport code (IATA).
        to_airport: Arrival airport code (IATA).
        date_from: Outbound date (YYYY-MM-DD or datetime object).
        date_to: Return date (YYYY-MM-DD or datetime object).
        seat: Seat type.
        passengers: Passenger configuration.
        language: Language code.
        currency: Currency code.
        max_stops: Maximum number of stops.
        proxy: Proxy URL.

    Returns:
        List of round-trip flight options.
    """
    date_from_str = _format_date(date_from)
    date_to_str = _format_date(date_to)

    query = create_query(
        flights=[
            FlightQuery(
                date=date_from_str,
                from_airport=from_airport,
                to_airport=to_airport,
                max_stops=max_stops,
            ),
            FlightQuery(
                date=date_to_str,
                from_airport=to_airport,
                to_airport=from_airport,
                max_stops=max_stops,
            ),
        ],
        seat=seat,
        trip="round-trip",
        passengers=passengers,
        language=language,
        currency=currency,
    )

    return get_flights(query, proxy=proxy)


def _parse_date(d: str | Datetime | Date) -> Date:
    """Convert str or Datetime to date object."""
    if isinstance(d, str):
        return Datetime.strptime(d, "%Y-%m-%d").date()
    elif isinstance(d, Datetime):
        return d.date()
    return d


def _format_date(d: str | Datetime | Date) -> str:
    """Convert str or Datetime to YYYY-MM-DD string."""
    if isinstance(d, str):
        return d
    elif isinstance(d, Datetime):
        return d.strftime("%Y-%m-%d")
    return d.strftime("%Y-%m-%d")
