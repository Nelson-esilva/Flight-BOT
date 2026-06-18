from urllib.parse import parse_qs, urlparse

import pytest

from app.models import Monitor
from app.services.amadeus_client import (
    AmadeusAuthenticationError,
    AmadeusClient,
    AmadeusConfigurationError,
    AmadeusRateLimitError,
    AmadeusUnavailableError,
)


def make_monitor(**overrides) -> Monitor:
    data = {
        "id": 7,
        "origin": "MAO",
        "destination": "GRU",
        "departure_date": "2026-07-10",
        "return_date": "2026-07-20",
        "trip_type": "round_trip",
        "max_price": 1200.0,
        "currency": "BRL",
        "adults": 1,
        "max_stops": 1,
        "status": "active",
    }
    data.update(overrides)
    return Monitor(**data)


def test_search_flight_offers_uses_expected_query_and_normalizes_response() -> None:
    calls = []

    def transport(method, url, headers, body, timeout):
        calls.append((method, url, headers, body, timeout))
        if url.endswith("/v1/security/oauth2/token"):
            return 200, {"access_token": "token"}

        return 200, {
            "data": [
                {
                    "source": "GDS",
                    "validatingAirlineCodes": ["LA"],
                    "itineraries": [
                        {
                            "duration": "PT4H",
                            "segments": [
                                {
                                    "carrierCode": "LA",
                                    "departure": {"at": "2026-07-10T10:00:00"},
                                },
                                {
                                    "carrierCode": "LA",
                                    "departure": {"at": "2026-07-10T12:00:00"},
                                },
                            ],
                        },
                        {
                            "duration": "PT4H",
                            "segments": [
                                {
                                    "carrierCode": "LA",
                                    "departure": {"at": "2026-07-20T10:00:00"},
                                }
                            ],
                        },
                    ],
                    "price": {"currency": "BRL", "total": "999.90"},
                }
            ]
        }

    client = AmadeusClient(
        api_key="key",
        api_secret="secret",
        base_url="https://test.api.amadeus.com",
        transport=transport,
    )

    offers = client.search_flight_offers(make_monitor(), max_results=5)

    assert len(offers) == 1
    assert offers[0].source == "amadeus"
    assert offers[0].airline == "LA"
    assert offers[0].total_price == 999.90
    assert offers[0].currency == "BRL"
    assert offers[0].stops == 1
    assert offers[0].duration == "PT4H"
    assert offers[0].departure_at == "2026-07-10T10:00:00"
    assert offers[0].return_at == "2026-07-20T10:00:00"
    assert offers[0].raw_json is not None

    search_url = calls[1][1]
    query = parse_qs(urlparse(search_url).query)
    assert query["originLocationCode"] == ["MAO"]
    assert query["destinationLocationCode"] == ["GRU"]
    assert query["departureDate"] == ["2026-07-10"]
    assert query["returnDate"] == ["2026-07-20"]
    assert query["adults"] == ["1"]
    assert query["currencyCode"] == ["BRL"]
    assert query["maxPrice"] == ["1200"]
    assert query["max"] == ["5"]


def test_missing_credentials_raise_configuration_error() -> None:
    client = AmadeusClient(api_key="", api_secret="", transport=lambda *args: (200, {}))

    with pytest.raises(AmadeusConfigurationError):
        client.search_flight_offers(make_monitor())


def test_unauthorized_response_raises_authentication_error() -> None:
    client = AmadeusClient(
        api_key="key",
        api_secret="secret",
        transport=lambda *args: (401, {}),
    )

    with pytest.raises(AmadeusAuthenticationError):
        client.search_flight_offers(make_monitor())


def test_rate_limit_response_raises_rate_limit_error() -> None:
    def transport(method, url, headers, body, timeout):
        if url.endswith("/v1/security/oauth2/token"):
            return 200, {"access_token": "token"}
        return 429, {}

    client = AmadeusClient(api_key="key", api_secret="secret", transport=transport)

    with pytest.raises(AmadeusRateLimitError):
        client.search_flight_offers(make_monitor())


def test_unavailable_response_raises_unavailable_error() -> None:
    client = AmadeusClient(
        api_key="key",
        api_secret="secret",
        transport=lambda *args: (503, {}),
    )

    with pytest.raises(AmadeusUnavailableError):
        client.search_flight_offers(make_monitor())
