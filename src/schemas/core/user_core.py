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


class ListUsers(Struct):
	acting_user_id: int
	offset: int = 0
	limit: int = 10


class Pagination(Struct):
	offset: int
	limit: int
	total: int
	has_more: bool


class UserData(Struct):
	id: int
	username: str
	created_at: datetime


class PaginatedUsersData(Struct):
	items: list[UserData]
	pagination: Pagination


class TokenData(Struct):
	access_token: str
	token_type: str = "bearer"
