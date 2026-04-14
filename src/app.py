from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.routers.log_router import router as logs_router
from src.api.routers.user_router import router as users_router
from src.api.routers.secrets_router import router as secrets_router
from src.db.session import init_db
from src.security.rate_limit import limiter
from src.security.runtime_config import validate_runtime_config
# from dotenv import load_dotenv

def create_app() -> FastAPI:
    app = FastAPI(title="SFF Bot API")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    validate_runtime_config()
    # load_dotenv()
    init_db()

    app.include_router(users_router, prefix="/api")
    app.include_router(logs_router, prefix="/api")
    app.include_router(secrets_router, prefix="/api")

    return app