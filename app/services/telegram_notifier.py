from collections.abc import Callable
from datetime import UTC, datetime
import json
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models import FareResult, Monitor


class TelegramNotifierError(Exception):
    pass


class TelegramConfigurationError(TelegramNotifierError):
    pass


class TelegramDeliveryError(TelegramNotifierError):
    pass


Transport = Callable[[str, dict, float], tuple[int, dict]]


def _default_transport(url: str, payload: dict, timeout: float) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        try:
            response_payload = json.loads(exc.read().decode("utf-8"))
        except json.JSONDecodeError:
            response_payload = {}
        return exc.code, response_payload
    except (SocketTimeout, TimeoutError, URLError) as exc:
        raise TelegramDeliveryError("Telegram request failed or timed out") from exc


class TelegramNotifier:
    def __init__(
        self,
        bot_token: str | None = None,
        chat_id: str | None = None,
        timeout_seconds: float | None = None,
        transport: Transport = _default_transport,
    ) -> None:
        settings = get_settings()
        self.bot_token = bot_token if bot_token is not None else settings.telegram_bot_token
        self.chat_id = chat_id if chat_id is not None else settings.telegram_chat_id
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.telegram_timeout_seconds
        )
        self.transport = transport

    def send_alert(self, monitor: Monitor, fare: FareResult) -> None:
        if not self.bot_token or not self.chat_id:
            raise TelegramConfigurationError("Telegram token or chat id is not configured")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": format_alert_message(monitor, fare),
            "disable_web_page_preview": True,
        }
        status, response = self.transport(url, payload, self.timeout_seconds)

        if status >= 400 or response.get("ok") is False:
            raise TelegramDeliveryError("Telegram message could not be delivered")


def format_alert_message(monitor: Monitor, fare: FareResult) -> str:
    checked_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    return "\n".join(
        [
            "Alerta de passagem encontrada",
            f"Trecho: {monitor.origin} -> {monitor.destination}",
            f"Ida: {monitor.departure_date}",
            f"Volta: {monitor.return_date or 'N/A'}",
            f"Preco encontrado: {fare.currency} {fare.total_price:.2f}",
            f"Limite configurado: {monitor.currency} {monitor.max_price:.2f}",
            f"Companhia: {fare.airline or 'N/A'}",
            f"Escalas: {fare.stops if fare.stops is not None else 'N/A'}",
            f"Fonte: {fare.source}",
            f"Consulta: {checked_at}",
            "Verifique a oferta antes de comprar.",
        ]
    )


def send_alert(monitor: Monitor, fare: FareResult) -> None:
    TelegramNotifier().send_alert(monitor, fare)
