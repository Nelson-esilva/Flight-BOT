from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta

from app.models import FareResult
from app.schemas import FlexibleOfferResponse, FlexibleSearchRequest, FlexibleSearchResponse
from app.services.amadeus_client import search_round_trip_offers


FareSearch = Callable[[str, str, str, str, int, str], list[FareResult]]


@dataclass(frozen=True, slots=True)
class DateCandidate:
    departure_date: date
    return_date: date


class FlexibleSearchError(ValueError):
    pass


def generate_date_candidates(request: FlexibleSearchRequest) -> list[DateCandidate]:
    departure_end = request.departure_end
    return_start = request.return_start

    if departure_end is None:
        if request.min_trip_days is None:
            raise FlexibleSearchError("min_trip_days is required to infer departure_end")
        departure_end = request.return_end - timedelta(days=request.min_trip_days)

    if return_start is None:
        if request.min_trip_days is None:
            raise FlexibleSearchError("min_trip_days is required to infer return_start")
        return_start = request.departure_start + timedelta(days=request.min_trip_days)

    candidates: list[DateCandidate] = []
    departure_date = request.departure_start

    while departure_date <= departure_end:
        return_date = return_start
        while return_date <= request.return_end:
            trip_days = (return_date - departure_date).days
            if _is_valid_candidate(trip_days, request):
                candidates.append(DateCandidate(departure_date, return_date))
                if len(candidates) >= request.max_candidates:
                    return candidates
            return_date += timedelta(days=1)
        departure_date += timedelta(days=1)

    if not candidates:
        raise FlexibleSearchError("No valid date combinations were generated")

    return candidates


def search_flexible(
    request: FlexibleSearchRequest,
    fare_search: FareSearch = search_round_trip_offers,
) -> FlexibleSearchResponse:
    candidates = generate_date_candidates(request)
    cheapest_offer: FareResult | None = None
    cheapest_candidate: DateCandidate | None = None

    for candidate in candidates:
        offers = fare_search(
            request.origin,
            request.destination,
            candidate.departure_date.isoformat(),
            candidate.return_date.isoformat(),
            request.adults,
            request.currency,
        )
        for offer in offers:
            if cheapest_offer is None or offer.total_price < cheapest_offer.total_price:
                cheapest_offer = offer
                cheapest_candidate = candidate

    return FlexibleSearchResponse(
        origin=request.origin,
        destination=request.destination,
        cheapest_offer=(
            _to_flexible_offer(cheapest_offer, cheapest_candidate)
            if cheapest_offer is not None and cheapest_candidate is not None
            else None
        ),
        searched_candidates=len(candidates),
        message="Menor tarifa encontrada dentro das combinacoes consultadas. Verifique a oferta antes de comprar.",
    )


def _is_valid_candidate(trip_days: int, request: FlexibleSearchRequest) -> bool:
    if trip_days <= 0:
        return False

    if request.min_trip_days is not None and trip_days < request.min_trip_days:
        return False

    if request.max_trip_days is not None and trip_days > request.max_trip_days:
        return False

    return True


def _to_flexible_offer(
    fare: FareResult,
    candidate: DateCandidate,
) -> FlexibleOfferResponse:
    return FlexibleOfferResponse(
        departure_date=candidate.departure_date,
        return_date=candidate.return_date,
        airline=fare.airline,
        total_price=fare.total_price,
        currency=fare.currency,
        stops=fare.stops,
        duration=fare.duration,
        source=fare.source,
    )
