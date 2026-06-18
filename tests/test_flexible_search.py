from datetime import date

import pytest
from pydantic import ValidationError

from app.models import FareResult
from app.main import app
from app.routes.search import flexible_search
from app.schemas import FlexibleSearchRequest, FlexibleSearchResponse
from app.services.flexible_search_service import (
    DateCandidate,
    FlexibleSearchError,
    generate_date_candidates,
    search_flexible,
)


def make_request(**overrides) -> FlexibleSearchRequest:
    data = {
        "origin": "CNF",
        "destination": "MAO",
        "trip_type": "round_trip",
        "departure_start": "2026-07-01",
        "departure_end": "2026-07-03",
        "return_start": "2026-08-01",
        "return_end": "2026-08-03",
        "adults": 1,
        "currency": "BRL",
        "min_trip_days": 5,
        "max_trip_days": 40,
        "max_candidates": 30,
    }
    data.update(overrides)
    return FlexibleSearchRequest(**data)


def make_fare(total_price: float, **overrides) -> FareResult:
    data = {
        "id": None,
        "monitor_id": 0,
        "source": "amadeus",
        "airline": "LA",
        "total_price": total_price,
        "currency": "BRL",
        "stops": 1,
        "duration": "PT6H40M",
        "departure_at": None,
        "return_at": None,
        "raw_json": "{}",
    }
    data.update(overrides)
    return FareResult(**data)


def test_generate_candidates_with_explicit_windows() -> None:
    candidates = generate_date_candidates(make_request(max_candidates=4))

    assert candidates == [
        DateCandidate(date(2026, 7, 1), date(2026, 8, 1)),
        DateCandidate(date(2026, 7, 1), date(2026, 8, 2)),
        DateCandidate(date(2026, 7, 1), date(2026, 8, 3)),
        DateCandidate(date(2026, 7, 2), date(2026, 8, 1)),
    ]


def test_generate_candidates_with_partial_window_and_duration() -> None:
    request = FlexibleSearchRequest(
        origin="CNF",
        destination="MAO",
        trip_type="round_trip",
        departure_start="2026-07-20",
        return_end="2026-08-04",
        adults=1,
        currency="BRL",
        min_trip_days=10,
        max_trip_days=12,
        max_candidates=30,
    )

    candidates = generate_date_candidates(request)

    assert candidates == [
        DateCandidate(date(2026, 7, 20), date(2026, 7, 30)),
        DateCandidate(date(2026, 7, 20), date(2026, 7, 31)),
        DateCandidate(date(2026, 7, 20), date(2026, 8, 1)),
        DateCandidate(date(2026, 7, 21), date(2026, 7, 31)),
        DateCandidate(date(2026, 7, 21), date(2026, 8, 1)),
        DateCandidate(date(2026, 7, 21), date(2026, 8, 2)),
        DateCandidate(date(2026, 7, 22), date(2026, 8, 1)),
        DateCandidate(date(2026, 7, 22), date(2026, 8, 2)),
        DateCandidate(date(2026, 7, 22), date(2026, 8, 3)),
        DateCandidate(date(2026, 7, 23), date(2026, 8, 2)),
        DateCandidate(date(2026, 7, 23), date(2026, 8, 3)),
        DateCandidate(date(2026, 7, 23), date(2026, 8, 4)),
        DateCandidate(date(2026, 7, 24), date(2026, 8, 3)),
        DateCandidate(date(2026, 7, 24), date(2026, 8, 4)),
        DateCandidate(date(2026, 7, 25), date(2026, 8, 4)),
    ]


def test_reject_invalid_origin() -> None:
    with pytest.raises(ValidationError):
        make_request(origin="BH")


def test_reject_invalid_destination() -> None:
    with pytest.raises(ValidationError):
        make_request(destination="MANAUS")


def test_reject_max_trip_days_lower_than_min_trip_days() -> None:
    with pytest.raises(ValidationError):
        make_request(min_trip_days=10, max_trip_days=9)


def test_reject_missing_date_data() -> None:
    with pytest.raises(ValidationError):
        FlexibleSearchRequest(
            origin="CNF",
            destination="MAO",
            trip_type="round_trip",
            departure_start="2026-07-20",
            return_end="2026-08-04",
        )


def test_respect_max_candidates() -> None:
    candidates = generate_date_candidates(make_request(max_candidates=2))

    assert len(candidates) == 2


def test_raise_when_no_valid_candidates() -> None:
    request = make_request(
        departure_start="2026-07-01",
        departure_end="2026-07-01",
        return_start="2026-07-01",
        return_end="2026-07-01",
        min_trip_days=None,
        max_trip_days=None,
    )

    with pytest.raises(FlexibleSearchError):
        generate_date_candidates(request)


def test_select_cheapest_offer_without_calling_real_api() -> None:
    calls = []

    def fake_search(origin, destination, departure_date, return_date, adults, currency):
        calls.append((origin, destination, departure_date, return_date, adults, currency))
        if departure_date == "2026-07-01":
            return [make_fare(1200, airline="G3")]
        return [make_fare(990, airline="LA", stops=0)]

    response = search_flexible(
        make_request(
            departure_start="2026-07-01",
            departure_end="2026-07-02",
            return_start="2026-08-01",
            return_end="2026-08-01",
        ),
        fake_search,
    )

    assert len(calls) == 2
    assert response.cheapest_offer is not None
    assert response.cheapest_offer.departure_date == date(2026, 7, 2)
    assert response.cheapest_offer.return_date == date(2026, 8, 1)
    assert response.cheapest_offer.total_price == 990
    assert response.cheapest_offer.airline == "LA"
    assert response.searched_candidates == 2


def test_flexible_search_endpoint_exists(monkeypatch) -> None:
    def fake_search(_request):
        return FlexibleSearchResponse(
            **{
            "origin": "CNF",
            "destination": "MAO",
            "cheapest_offer": {
                "departure_date": "2026-07-23",
                "return_date": "2026-08-03",
                "airline": "LA",
                "total_price": 1120.45,
                "currency": "BRL",
                "stops": 1,
                "duration": "PT6H40M",
                "source": "amadeus",
            },
            "searched_candidates": 15,
            "message": "Menor tarifa encontrada dentro das combinacoes consultadas. Verifique a oferta antes de comprar.",
            }
        )

    monkeypatch.setattr("app.routes.search.search_flexible", fake_search)
    route_paths = set(app.openapi()["paths"])
    request = FlexibleSearchRequest(
        origin="CNF",
        destination="MAO",
        trip_type="round_trip",
        departure_start="2026-07-20",
        return_end="2026-08-04",
        adults=1,
        currency="BRL",
        min_trip_days=10,
        max_trip_days=12,
        max_candidates=30,
    )

    response = flexible_search(request)

    assert "/search/flexible" in route_paths
    assert response.cheapest_offer is not None
    assert response.cheapest_offer.total_price == 1120.45
