from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_thread_service, get_db
from app.schemas.thread import ThreadCreate, ThreadRead
from app.services.thread_service import ThreadService

router = APIRouter()


@router.get("", response_model=list[ThreadRead])
async def list_threads(
    service: ThreadService  = Depends(get_thread_service),
    db:      AsyncSession   = Depends(get_db),
):
    return await service.list_all(db)


@router.post("", response_model=ThreadRead, status_code=201)
async def create_thread(
    data:    ThreadCreate   = Depends(),
    service: ThreadService  = Depends(get_thread_service),
    db:      AsyncSession   = Depends(get_db),
):
    return await service.create(db, data)


@router.get("/{thread_id}", response_model=ThreadRead)
async def get_thread(
    thread_id: str,
    service:   ThreadService = Depends(get_thread_service),
    db:        AsyncSession  = Depends(get_db),
):
    return await service.get(db, thread_id)


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: str,
    service:   ThreadService = Depends(get_thread_service),
    db:        AsyncSession  = Depends(get_db),
):
    await service.delete(db, thread_id)