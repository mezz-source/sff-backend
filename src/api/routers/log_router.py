from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user_model import User
from src.schemas.core.log_core import (
    CreateLog as CreateLogCore,
    GetLog as GetLogCore,
    ListLogs as ListLogsCore,
    ModifyLog as ModifyLogCore,
)
from src.schemas.log_scheme import CreateLog, ModifyLog
from src.security.jwt import get_current_user
from src.services.log_service import LogService
from src.util.response import handle_request

router = APIRouter(prefix="/logs")


@router.get("/")
async def list_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = LogService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        ListLogsCore,
        service.list_logs,
        acting_user_id=current_user.id,
    )


@router.get("/{log_id}")
async def get_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = LogService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        GetLogCore,
        service.get_log,
        log_id=log_id,
        acting_user_id=current_user.id,
    )


@router.post("/")
async def create_log(log: CreateLog, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = LogService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        CreateLogCore,
        service.create_log,
        message=log.message,
        acting_user_id=current_user.id,
    )


@router.patch("/{log_id}")
async def modify_log(
    log_id: int,
    modifications: ModifyLog,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LogService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        ModifyLogCore,
        service.modify_log,
        log_id=log_id,
        acting_user_id=current_user.id,
        **modifications.model_dump(exclude_none=True),
    )
