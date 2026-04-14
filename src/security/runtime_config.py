import os


def _require_env(name: str) -> str:
	value = os.getenv(name)
	if not value:
		raise RuntimeError(f"{name} is not configured.")
	return value


def validate_runtime_config() -> None:
	"""Fail fast at startup if required deployment settings are missing."""
	_require_env("JWT_SECRET")
	_require_env("USER_CREATION_TOKEN")