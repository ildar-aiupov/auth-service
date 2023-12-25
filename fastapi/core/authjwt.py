from async_fastapi_jwt_auth import AuthJWT

from core.config import settings


authjwt = AuthJWT()


@authjwt.load_config
def get_config():
    return settings


def get_authjwt():
    return authjwt
