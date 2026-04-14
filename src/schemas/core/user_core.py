from datetime import datetime

from msgspec import Struct


class CreateUser(Struct):
	username: str
	password: str


class LoginUser(Struct):
	username: str
	password: str


class GetUser(Struct):
	user_id: int
	acting_user_id: int


class ModifyUser(Struct):
	user_id: int
	acting_user_id: int
	username: str | None = None
	password: str | None = None


class DeleteUser(Struct):
	user_id: int
	acting_user_id: int


class UserData(Struct):
	id: int
	username: str
	created_at: datetime


class TokenData(Struct):
	access_token: str
	token_type: str = "bearer"
