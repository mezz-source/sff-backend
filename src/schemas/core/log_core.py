from datetime import datetime

from msgspec import Struct


class CreateLog(Struct):
	message: str
	acting_user_id: int


class GetLog(Struct):
	log_id: int
	acting_user_id: int


class ModifyLog(Struct):
	log_id: int
	acting_user_id: int
	message: str | None = None


class ListLogs(Struct):
	acting_user_id: int
	user_id: int | None = None
	offset: int = 0
	limit: int = 10


class Pagination(Struct):
	offset: int
	limit: int
	total: int
	has_more: bool


class LogData(Struct):
	id: int
	user_id: int
	username: str
	message: str
	created_at: datetime


class PaginatedLogsData(Struct):
	items: list[LogData]
	pagination: Pagination
