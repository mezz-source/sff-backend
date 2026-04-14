from typing import Any

from msgspec import Struct

class Response(Struct):
    response_code: int
    status: str
    detail: str | None = None
    result: Any | None = None

class Error(Struct):
    response_code: int
    status: str
    detail: str