from fastapi import APIRouter, HTTPException, status

from app.schemas import MonitorCreate, MonitorResponse, MonitorUpdate
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
