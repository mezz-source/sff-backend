from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user_model import User
from src.schemas.core.user_core import (
    CreateUser as CreateUserCore,
    DeleteUser as DeleteUserCore,
    GetUser as GetUserCore,
    ListUsers as ListUsersCore,
    LoginUser as LoginUserCore,
    ModifyUser as ModifyUserCore,
)
from src.schemas.user_scheme import CreateUser, LoginUser, ModifyUser
from src.security.access import require_user_creation_token
from src.security.jwt import get_current_user
from src.security.rate_limit import limiter
from src.services.user_service import UserService
from src.util.response import handle_request

router = APIRouter(prefix="/users")


@router.get("/")
@limiter.limit("60/minute")
async def list_users(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        ListUsersCore,
        service.list_users,
        acting_user_id=current_user.id,
        offset=offset,
        limit=limit,
    )


@router.get("/{user_id}")
@limiter.limit("60/minute")
async def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        GetUserCore,
        service.get_user,
        user_id=user_id,
        acting_user_id=current_user.id,
    )


@router.post("/")
@limiter.limit("20/minute")
async def create_user(
    request: Request,
    user: CreateUser,
    db: Session = Depends(get_db),
    _: None = Depends(require_user_creation_token),
):
    service = UserService(db)
    return await handle_request(
        "result",
        None,
        CreateUserCore,
        service.create_user,
        **user.model_dump(),
    )


@router.delete("/{user_id}")
@limiter.limit("30/minute")
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        DeleteUserCore,
        service.delete_user,
        user_id=user_id,
        acting_user_id=current_user.id,
    )


@router.patch("/{user_id}")
@limiter.limit("30/minute")
async def update_user(
    request: Request,
    user_id: int,
    modifications: ModifyUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = UserService(db)
    return await handle_request(
        "result",
        {"id": current_user.id},
        ModifyUserCore,
        service.modify_user,
        user_id=user_id,
        acting_user_id=current_user.id,
        **modifications.model_dump(exclude_none=True),
    )


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, login: LoginUser, db: Session = Depends(get_db)):
    service = UserService(db)
    return await handle_request(
        "result",
        None,
        LoginUserCore,
        service.login,
        **login.model_dump(),
    )