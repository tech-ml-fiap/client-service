from fastapi import FastAPI
from app.adapters.driver.controllers.customer_controller import router as client_router
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from app.adapters.driver.controllers.auth_controller import router as auth_router

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()


def create_app() -> FastAPI:
    app = FastAPI(title="Client-Service")
    app.include_router(client_router, prefix="/api/client", tags=["clients"])
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    return app


app = create_app()
