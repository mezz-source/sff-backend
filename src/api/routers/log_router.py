from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.db.session import SessionLocal, get_db
from src.models.user_model import User
from src.schemas.core.log_core import (
    CreateLog as CreateLogCore,
    GetLog as GetLogCore,
    ListLogs as ListLogsCore,
    ModifyLog as ModifyLogCore,
)
from src.schemas.core.reponse_scheme import Response
from src.schemas.log_scheme import CreateLog, ModifyLog
from src.security.jwt import get_current_user, verify_token
from src.security.rate_limit import limiter
from src.services.log_service import LogService
from src.util.response import create_dictionary, handle_request, handle_response

router = APIRouter(prefix="/logs")


class LogWebSocketHub:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        dead_connections: list[WebSocket] = []
        for websocket in self.connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.disconnect(websocket)


log_ws_hub = LogWebSocketHub()


@router.websocket("/ws")
async def logs_ws(websocket: WebSocket, token: str | None = Query(default=None)):
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    db = SessionLocal()
    try:
        payload = verify_token(token)
        subject = payload.get("sub")
        if not subject or not str(subject).isdigit() or not db.get(User, int(subject)):
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    finally:
        db.close()

    await log_ws_hub.connect(websocket)
    try:
        await websocket.send_json({"event": "connected", "detail": "Subscribed to new logs"})
        while True:
            # Keep the connection alive if a client sends ping or any text.
            await websocket.receive_text()
    except WebSocketDisconnect:
        log_ws_hub.disconnect(websocket)
    except Exception:
        log_ws_hub.disconnect(websocket)


@router.get("/")
@limiter.limit("60/minute")
async def list_logs(
    request: Request,
    user_id: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LogService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        ListLogsCore,
        service.list_logs,
        acting_user_id=current_user.id,
        user_id=user_id,
        offset=offset,
        limit=limit,
    )


@router.get("/{log_id}")
@limiter.limit("60/minute")
async def get_log(
    request: Request,
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
@limiter.limit("40/minute")
async def create_log(
    request: Request,
    log: CreateLog,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LogService(db)
    result = await service.create_log(
        CreateLogCore(
            message=log.message,
            acting_user_id=current_user.id,
        )
    )

    if isinstance(result, Response) and result.result is not None:
        log_payload = await create_dictionary(result.result)
        await log_ws_hub.broadcast({"event": "log.created", "log": log_payload})

    return await handle_response("result", result)


@router.patch("/{log_id}")
@limiter.limit("40/minute")
async def modify_log(
    request: Request,
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
