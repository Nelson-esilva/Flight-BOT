import pytest

from app.models import FareResult, Monitor
from app.services.telegram_notifier import (
    TelegramConfigurationError,
    TelegramDeliveryError,
    TelegramNotifier,
    format_alert_message,
)


def make_monitor() -> Monitor:
    return Monitor(
        id=1,
        origin="MAO",
        destination="GRU",
        departure_date="2026-07-10",
        return_date=None,
        trip_type="one_way",
        max_price=1000,
        currency="BRL",
        adults=1,
        max_stops=1,
        status="active",
    )


def make_fare() -> FareResult:
    return FareResult(
        id=1,
        monitor_id=1,
        source="amadeus",
        airline="LA",
        total_price=850,
        currency="BRL",
        stops=0,
        duration="PT3H",
        departure_at="2026-07-10T10:00:00",
        return_at=None,
        raw_json="{}",
    )


def test_format_alert_message_contains_required_fields() -> None:
    message = format_alert_message(make_monitor(), make_fare())

    assert "Trecho: MAO -> GRU" in message
    assert "Ida: 2026-07-10" in message
    assert "Preco encontrado: BRL 850.00" in message
    assert "Limite configurado: BRL 1000.00" in message
    assert "Companhia: LA" in message
    assert "Escalas: 0" in message
    assert "Fonte: amadeus" in message
    assert "Consulta:" in message
    assert "Verifique a oferta antes de comprar." in message


def test_send_alert_posts_message_without_exposing_token_in_payload() -> None:
    calls = []

    def transport(url, payload, timeout):
        calls.append((url, payload, timeout))
        return 200, {"ok": True}

    notifier = TelegramNotifier(
        bot_token="secret-token",
        chat_id="123",
        timeout_seconds=5,
        transport=transport,
    )

    notifier.send_alert(make_monitor(), make_fare())

    url, payload, timeout = calls[0]
    assert url == "https://api.telegram.org/botsecret-token/sendMessage"
    assert payload["chat_id"] == "123"
    assert "secret-token" not in payload["text"]
    assert payload["disable_web_page_preview"] is True
    assert timeout == 5


def test_missing_configuration_raises_error() -> None:
    notifier = TelegramNotifier(bot_token="", chat_id="", transport=lambda *args: (200, {}))

    with pytest.raises(TelegramConfigurationError):
        notifier.send_alert(make_monitor(), make_fare())


def test_delivery_error_raises_error() -> None:
    notifier = TelegramNotifier(
        bot_token="token",
        chat_id="123",
        transport=lambda *args: (500, {"ok": False}),
    )

    with pytest.raises(TelegramDeliveryError):
        notifier.send_alert(make_monitor(), make_fare())
