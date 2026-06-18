from collections.abc import Callable
import json
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models import FareResult, Monitor


class AmadeusClientError(Exception):
    pass


class AmadeusConfigurationError(AmadeusClientError):
    pass


class AmadeusAuthenticationError(AmadeusClientError):
    pass


class AmadeusRateLimitError(AmadeusClientError):
    pass


class AmadeusUnavailableError(AmadeusClientError):
    pass


Transport = Callable[[str, str, dict[str, str], bytes | None, float], tuple[int, dict]]


def _default_transport(
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None,
    timeout: float,
) -> tuple[int, dict]:
    request = Request(url=url, data=body, headers=headers, method=method)

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload
    except HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except json.JSONDecodeError:
            payload = {}
        return exc.code, payload
    except (SocketTimeout, TimeoutError, URLError) as exc:
        raise AmadeusUnavailableError("Amadeus request failed or timed out") from exc


class AmadeusClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        transport: Transport = _default_transport,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.amadeus_api_key
        self.api_secret = api_secret if api_secret is not None else settings.amadeus_api_secret
        self.base_url = (base_url or settings.amadeus_base_url).rstrip("/")
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.amadeus_timeout_seconds
        )
        self.transport = transport
        self._access_token: str | None = None

    def search_flight_offers(self, monitor: Monitor, max_results: int = 10) -> list[FareResult]:
        token = self._get_access_token()
        query_params = {
            "originLocationCode": monitor.origin,
            "destinationLocationCode": monitor.destination,
            "departureDate": monitor.departure_date,
            "adults": str(monitor.adults),
            "currencyCode": monitor.currency,
            "maxPrice": str(int(monitor.max_price)),
            "max": str(max_results),
        }

        if monitor.return_date:
            query_params["returnDate"] = monitor.return_date

        url = f"{self.base_url}/v2/shopping/flight-offers?{urlencode(query_params)}"
        status, payload = self.transport(
            "GET",
            url,
            {"Authorization": f"Bearer {token}"},
            None,
            self.timeout_seconds,
        )
        self._raise_for_status(status)

        return [
            self._normalize_offer(offer, monitor)
            for offer in payload.get("data", [])
        ]

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token

        if not self.api_key or not self.api_secret:
            raise AmadeusConfigurationError("Amadeus credentials are not configured")

        body = urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
            }
        ).encode("utf-8")
        status, payload = self.transport(
            "POST",
            f"{self.base_url}/v1/security/oauth2/token",
            {"Content-Type": "application/x-www-form-urlencoded"},
            body,
            self.timeout_seconds,
        )
        self._raise_for_status(status)

        access_token = payload.get("access_token")
        if not access_token:
            raise AmadeusAuthenticationError("Amadeus token response did not include access_token")

        self._access_token = access_token
        return access_token

    def _raise_for_status(self, status: int) -> None:
        if status == 401:
            self._access_token = None
            raise AmadeusAuthenticationError("Amadeus authentication failed")

        if status == 429:
            raise AmadeusRateLimitError("Amadeus rate limit exceeded")

        if status >= 500:
            raise AmadeusUnavailableError("Amadeus service is unavailable")

        if status >= 400:
            raise AmadeusClientError(f"Amadeus request failed with status {status}")

    def _normalize_offer(self, offer: dict, monitor: Monitor) -> FareResult:
        price = offer.get("price", {})
        itineraries = offer.get("itineraries", [])
        first_itinerary = itineraries[0] if itineraries else {}
        first_segments = first_itinerary.get("segments", [])
        first_segment = first_segments[0] if first_segments else {}
        validating_carriers = offer.get("validatingAirlineCodes") or []

        return_itinerary = itineraries[1] if len(itineraries) > 1 else {}
        return_segments = return_itinerary.get("segments", [])
        return_segment = return_segments[0] if return_segments else {}

        return FareResult(
            id=None,
            monitor_id=monitor.id or 0,
            source="amadeus",
            airline=validating_carriers[0] if validating_carriers else first_segment.get("carrierCode"),
            total_price=float(price["total"]),
            currency=price["currency"],
            stops=_count_stops(itineraries),
            duration=first_itinerary.get("duration"),
            departure_at=first_segment.get("departure", {}).get("at"),
            return_at=return_segment.get("departure", {}).get("at"),
            raw_json=json.dumps(offer, sort_keys=True),
        )


def search_flight_offers(monitor: Monitor) -> list[FareResult]:
    return AmadeusClient().search_flight_offers(monitor)


def _count_stops(itineraries: list[dict]) -> int:
    stops = 0
    for itinerary in itineraries:
        segments = itinerary.get("segments", [])
        stops += max(len(segments) - 1, 0)
    return stops
