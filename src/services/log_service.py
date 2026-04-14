from src.repo.log_repo import LogRepository
from src.repo.user_repo import UserRepository
from src.schemas.core.log_core import (
	CreateLog,
	GetLog,
	ListLogs,
	LogData,
	ModifyLog,
	PaginatedLogsData,
	Pagination,
)
from src.schemas.core.reponse_scheme import Error, Response
import requests

class LogService:
	def __init__(self, db):
		self.repo = LogRepository(db)
		self.user_repo = UserRepository(db)

	async def list_logs(self, request: ListLogs) -> Error | Response:
		if request.user_id is not None:
			rows = self.repo.list_by_user_id(request.user_id, request.offset, request.limit)
			total = self.repo.count_by_user_id(request.user_id)
		else:
			rows = self.repo.list_all(request.offset, request.limit)
			total = self.repo.count_all()

		result = [
			LogData(
				id=row.id,
				user_id=row.user_id,
				username=row.user.username,
				message=row.message,
				created_at=row.created_at,
			)
			for row in rows
		]

		return Response(
			response_code=200,
			status="SUCCESS",
			detail="Logs retrieved successfully",
			result=PaginatedLogsData(
				items=result,
				pagination=Pagination(
					offset=request.offset,
					limit=request.limit,
					total=total,
					has_more=(request.offset + len(rows)) < total,
				),
			),
		)

	async def get_log(self, request: GetLog) -> Error | Response:
		log = self.repo.get_by_id(request.log_id)
		if not log:
			return Error(response_code=404, status="NOT_FOUND", detail="Log not found")

		return Response(
			response_code=200,
			status="SUCCESS",
			detail="Log retrieved successfully",
			result=LogData(
				id=log.id,
				user_id=log.user_id,
				username=log.user.username,
				message=log.message,
				created_at=log.created_at,
			),
		)

	async def create_log(self, request: CreateLog) -> Error | Response:
		user = self.user_repo.get_by_id(request.acting_user_id)
		if not user:
			return Error(response_code=404, status="NOT_FOUND", detail="User not found")

		created_at_override = None
		if request.created_at is not None:
			if request.created_at.tzinfo is None or request.created_at.utcoffset() is None:
				return Error(
					response_code=400,
					status="BAD_REQUEST",
					detail="created_at must include a timezone offset",
				)

			# Preserve client wall-clock timestamp for explicit overrides.
			created_at_override = request.created_at.replace(tzinfo=None)

		created = self.repo.create_log(
			user_id=request.acting_user_id,
			message=request.message,
			created_at=created_at_override,
		)

		try:
			display_time = created.created_at.strftime("%b %d, %Y %I:%M:%S %p")
			message_body = (request.message or "").strip() or "(empty)"
			quoted_message = message_body.replace("\n", "\n> ")
			discord_content = (
				f"## {user.username} | Log — {display_time}\n"
				f"> {quoted_message}"
			)

			requests.post(
				"https://discord.com/api/webhooks/1493468797611409410/TTusysvyf6bblJvKxFzJyWPVck2UjLk8j9tBulEbR1kHmPZxDHboYPWFlqm6H1uWImhT",
				json={"username": "Log Bot", "content": discord_content},
				timeout=5,
			)
		except Exception as exc:
			print("Failed to send Discord webhook:", str(exc))

		return Response(
			response_code=201,
			status="SUCCESS",
			detail="Log created successfully",
			result=LogData(
				id=created.id,
				user_id=created.user_id,
				username=user.username,
				message=created.message,
				created_at=created.created_at,
			),
		)
	async def modify_log(self, request: ModifyLog) -> Error | Response:
		log = self.repo.get_by_id(request.log_id)
		if not log:
			return Error(response_code=404, status="NOT_FOUND", detail="Log not found")
		if log.user_id != request.acting_user_id:
			return Error(response_code=403, status="FORBIDDEN", detail="Cannot modify this log")

		if request.message is not None:
			log.message = request.message

		updated = self.repo.update_log(log)
		return Response(
			response_code=200,
			status="SUCCESS",
			detail="Log updated successfully",
			result=LogData(
				id=updated.id,
				user_id=updated.user_id,
				username=updated.user.username,
				message=updated.message,
				created_at=updated.created_at,
			),
		)