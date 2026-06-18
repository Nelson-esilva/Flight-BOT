from fastapi import APIRouter, HTTPException, status

from app.schemas import FlexibleSearchRequest, FlexibleSearchResponse
from app.services.flexible_search_service import FlexibleSearchError, search_flexible


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/flexible", response_model=FlexibleSearchResponse)
def flexible_search(data: FlexibleSearchRequest) -> FlexibleSearchResponse:
    try:
        return search_flexible(data)
    except FlexibleSearchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
