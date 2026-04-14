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


class LogData(Struct):
	id: int
	user_id: int
	username: str
	message: str
	created_at: datetime
