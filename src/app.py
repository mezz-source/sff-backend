from fastapi import FastAPI

from src.api.routers.log_router import router as logs_router
from src.api.routers.user_router import router as users_router
from src.db.session import init_db

def create_app() -> FastAPI:
    app = FastAPI(title="SFF Bot API")
    init_db()

    app.include_router(users_router, prefix="/api")
    app.include_router(logs_router, prefix="/api")

    return app