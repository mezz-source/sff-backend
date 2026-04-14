from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user_model import User
from src.schemas.core.user_core import (
    CreateUser as CreateUserCore,
    DeleteUser as DeleteUserCore,
    GetUser as GetUserCore,
    LoginUser as LoginUserCore,
    ModifyUser as ModifyUserCore,
)
from src.schemas.user_scheme import CreateUser, LoginUser, ModifyUser
from src.security.jwt import get_current_user
from src.services.user_service import UserService
from src.util.response import handle_request

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    service = UserService(db)
    return await handle_request(
        "result",
        None,
        CreateUserCore,
        service.create_user,
        **user.model_dump(),
    )


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
async def update_user(
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
async def login(login: LoginUser, db: Session = Depends(get_db)):
    service = UserService(db)
    return await handle_request(
        "result",
        None,
        LoginUserCore,
        service.login,
        **login.model_dump(),
    )