import hmac
import os

from fastapi import Header, HTTPException, status


def require_user_creation_token(
	x_user_creation_token: str | None = Header(default=None),
) -> None:
	expected = os.getenv("USER_CREATION_TOKEN")
	if not expected:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail="User creation is not available.",
		)

	if not x_user_creation_token or not hmac.compare_digest(x_user_creation_token, expected):
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Invalid user creation token.",
		)