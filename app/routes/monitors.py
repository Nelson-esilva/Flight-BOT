from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    FareResultResponse,
    MonitorCreate,
    MonitorResponse,
    MonitorRunResponse,
    MonitorUpdate,
)
from app.services import monitor_service


router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.post("", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
def create_monitor(data: MonitorCreate) -> MonitorResponse:
    monitor = monitor_service.create_monitor(data)
    return MonitorResponse.model_validate(monitor)


@router.get("", response_model=list[MonitorResponse])
def list_monitors() -> list[MonitorResponse]:
    return [
        MonitorResponse.model_validate(monitor)
        for monitor in monitor_service.list_monitors()
    ]


@router.get("/{monitor_id}", response_model=MonitorResponse)
def get_monitor(monitor_id: int) -> MonitorResponse:
    monitor = monitor_service.get_monitor(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found")

    return MonitorResponse.model_validate(monitor)


@router.patch("/{monitor_id}", response_model=MonitorResponse)
def update_monitor(monitor_id: int, data: MonitorUpdate) -> MonitorResponse:
    monitor = monitor_service.update_monitor_status(monitor_id, data)
    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found")

    return MonitorResponse.model_validate(monitor)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(monitor_id: int) -> None:
    deleted = monitor_service.delete_monitor(monitor_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found")


@router.post("/{monitor_id}/run-now", response_model=MonitorRunResponse)
def run_monitor_now(monitor_id: int) -> MonitorRunResponse:
    result = monitor_service.run_monitor_now(monitor_id)
    monitor = result.monitor
    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found")

    if monitor.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Monitor is inactive")

    return MonitorRunResponse(
        monitor_id=monitor.id or monitor_id,
        offers_found=len(result.offers),
        best_offer=(
            FareResultResponse.model_validate(result.best_offer)
            if result.best_offer is not None
            else None
        ),
        alerts_sent=result.alerts_sent,
        duplicate_alerts=result.duplicate_alerts,
        alert_error=result.alert_error,
    )
