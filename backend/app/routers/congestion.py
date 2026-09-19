from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.metro_service import MetroService

router = APIRouter(tags=["congestion"])


class CongestionBody(BaseModel):
    a: str
    b: str
    level: str


@router.get("/congestion")
def list_congestion():
    with MetroService() as s:
        return {"items": s.congestion_edges()}


@router.put("/congestion")
def set_congestion(body: CongestionBody):
    with MetroService() as s:
        try:
            return s.set_congestion(body.a, body.b, body.level)
        except ValueError as exc:
            raise HTTPException(400, str(exc))


@router.delete("/congestion")
def clear_congestion(a: str, b: str):
    with MetroService() as s:
        return s.clear_congestion(a, b)
