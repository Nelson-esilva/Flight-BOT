from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


TripType = Literal["one_way", "round_trip"]
MonitorStatus = Literal["active", "inactive"]


class MonitorCreate(BaseModel):
    origin: str
    destination: str
    departure_date: date
    return_date: date | None = None
    trip_type: TripType = "one_way"
    max_price: float = Field(gt=0)
    currency: str = "BRL"
    adults: int = Field(default=1, gt=0)
    max_stops: int | None = Field(default=None, ge=0)

    @field_validator("origin", "destination")
    @classmethod
    def normalize_iata(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("IATA code must contain exactly 3 letters")
        return normalized

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must contain exactly 3 letters")
        return normalized

    @model_validator(mode="after")
    def validate_trip_dates(self) -> "MonitorCreate":
        if self.trip_type == "round_trip" and self.return_date is None:
            raise ValueError("return_date is required for round_trip")

        if self.return_date is not None and self.return_date < self.departure_date:
            raise ValueError("return_date cannot be before departure_date")

        return self


class MonitorUpdate(BaseModel):
    status: MonitorStatus


class MonitorResponse(BaseModel):
    id: int
    origin: str
    destination: str
    departure_date: date
    return_date: date | None
    trip_type: TripType
    max_price: float
    currency: str
    adults: int
    max_stops: int | None
    status: MonitorStatus

    model_config = ConfigDict(from_attributes=True)


class FareResultResponse(BaseModel):
    id: int | None
    monitor_id: int
    source: str
    total_price: float
    currency: str
    airline: str | None
    stops: int | None
    duration: str | None
    departure_at: str | None
    return_at: str | None

    model_config = ConfigDict(from_attributes=True)


class MonitorRunResponse(BaseModel):
    monitor_id: int
    offers_found: int
    best_offer: FareResultResponse | None
    alerts_sent: int = 0
    duplicate_alerts: int = 0
    alert_error: str | None = None
