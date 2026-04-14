from src.repo.user_repo import UserRepository
from src.schemas.core.reponse_scheme import Error, Response
from src.schemas.core.user_core import (
	CreateUser,
	DeleteUser,
	GetUser,
	LoginUser,
	ModifyUser,
	TokenData,
	UserData,
)
from src.security.hash import hash_password, verify_password
from src.security.jwt import create_access_token
from datetime import timedelta


class UserService:
	def __init__(self, db):
		self.repo = UserRepository(db)

	async def create_user(self, request: CreateUser) -> Error | Response:
		existing = self.repo.get_by_username(request.username)
		if existing:
			return Error(
				response_code=409,
				status="ALREADY_EXISTS",
				detail=f"Username {request.username} already exists",
			)

		created = self.repo.create_user(request.username, hash_password(request.password))
		return Response(
			response_code=201,
			status="SUCCESS",
			detail="User created successfully",
			result=UserData(id=created.id, username=created.username, created_at=created.created_at),
		)

	async def login(self, request: LoginUser) -> Error | Response:
		user = self.repo.get_by_username(request.username)
		if not user or not verify_password(request.password, user.password_hash):
			return Error(response_code=401, status="UNAUTHORIZED", detail="Invalid username or password")

		token = create_access_token(user.id, expires_delta=timedelta(days=30))
		return Response(
			response_code=200,
			status="SUCCESS",
			detail="Login successful",
			result=TokenData(access_token=token),
		)

	async def get_user(self, request: GetUser) -> Error | Response:
		if request.user_id != request.acting_user_id:
			return Error(response_code=403, status="FORBIDDEN", detail="Cannot access this user")

		user = self.repo.get_by_id(request.user_id)
		if not user:
			return Error(response_code=404, status="NOT_FOUND", detail="User not found")

		return Response(
			response_code=200,
			status="SUCCESS",
			detail="User retrieved successfully",
			result=UserData(id=user.id, username=user.username, created_at=user.created_at),
		)

	async def modify_user(self, request: ModifyUser) -> Error | Response:
		if request.user_id != request.acting_user_id:
			return Error(response_code=403, status="FORBIDDEN", detail="Cannot modify this user")

		user = self.repo.get_by_id(request.user_id)
		if not user:
			return Error(response_code=404, status="NOT_FOUND", detail="User not found")

		if request.username and request.username != user.username:
			existing = self.repo.get_by_username(request.username)
			if existing:
				return Error(
					response_code=409,
					status="ALREADY_EXISTS",
					detail=f"Username {request.username} already exists",
				)
			user.username = request.username

		if request.password:
			user.password_hash = hash_password(request.password)

		updated = self.repo.update_user(user)
		return Response(
			response_code=200,
			status="SUCCESS",
			detail="User updated successfully",
			result=UserData(id=updated.id, username=updated.username, created_at=updated.created_at),
		)

	async def delete_user(self, request: DeleteUser) -> Error | Response:
		if request.user_id != request.acting_user_id:
			return Error(response_code=403, status="FORBIDDEN", detail="Cannot delete this user")

		user = self.repo.get_by_id(request.user_id)
		if not user:
			return Error(response_code=404, status="NOT_FOUND", detail="User not found")

		self.repo.delete_user(user)
		return Response(response_code=200, status="SUCCESS", detail="User deleted successfully", result=None)