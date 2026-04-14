import hashlib
import hmac
import os

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 200_000


def hash_password(password: str) -> str:
	salt = os.urandom(16).hex()
	digest = hashlib.pbkdf2_hmac(
		"sha256",
		password.encode("utf-8"),
		salt.encode("utf-8"),
		ITERATIONS,
	).hex()
	return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
	try:
		algorithm, iterations, salt, digest = password_hash.split("$")
		if algorithm != ALGORITHM:
			return False
		calculated = hashlib.pbkdf2_hmac(
			"sha256",
			password.encode("utf-8"),
			salt.encode("utf-8"),
			int(iterations),
		).hex()
		return hmac.compare_digest(calculated, digest)
	except Exception:
		return False
