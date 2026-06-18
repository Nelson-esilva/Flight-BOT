from app.main import app, health_check


def test_app_uses_project_name() -> None:
    assert app.title == "Flight_BOT"


def test_health_check_returns_operational_status() -> None:
    assert health_check() == {
        "status": "ok",
        "service": "Flight_BOT",
        "environment": "local",
    }
