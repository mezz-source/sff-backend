import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user_model import User

SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def _b64url_encode(data: bytes) -> str:
	return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
	padding = "=" * (-len(data) % 4)
	return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
	now = datetime.now(timezone.utc)
	expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	payload = {
		"sub": str(user_id),
		"iat": int(now.timestamp()),
		"exp": int(expire.timestamp()),
	}
	header = {"alg": "HS256", "typ": "JWT"}

	header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
	payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
	signing_input = f"{header_part}.{payload_part}".encode("utf-8")
	signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
	signature_part = _b64url_encode(signature)

	return f"{header_part}.{payload_part}.{signature_part}"


def verify_token(token: str) -> dict:
	try:
		header_part, payload_part, signature_part = token.split(".")
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

	signing_input = f"{header_part}.{payload_part}".encode("utf-8")
	expected_signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
	provided_signature = _b64url_decode(signature_part)

	if not hmac.compare_digest(expected_signature, provided_signature):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

	payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
	exp = payload.get("exp")
	if not isinstance(exp, int) or datetime.now(timezone.utc).timestamp() > exp:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

	return payload


def get_current_user(
	token: str = Depends(oauth2_scheme),
	db: Session = Depends(get_db),
) -> User:
	payload = verify_token(token)
	subject = payload.get("sub")
	if not subject or not str(subject).isdigit():
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

	user = db.get(User, int(subject))
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
	return user
