from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from async_fastapi_jwt_auth import AuthJWT

from api.v1 import manage, users
from core.config import settings
from db import redis_db
from db.redis_db import get_redis


@AuthJWT.load_config
def get_config():
    return settings


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    atoken_jti = str(decrypted_token["jti"])
    redis = await get_redis()
    return await redis.get(atoken_jti) is not None


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_db.redis = Redis(
        host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
    )
    yield


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(users.router, prefix="/api/v1/users")
app.include_router(manage.router, prefix="/api/v1/manage")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
