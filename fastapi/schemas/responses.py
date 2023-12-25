from pydantic import BaseModel, UUID4


class SignupResp(BaseModel):
    id: UUID4
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class TokenResp(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True


class HistoryResp(BaseModel):
    action: str
    user_agent: str
    created_at: str

    class Config:
        from_attributes = True


class ShowRolesResp(BaseModel):
    name: str
    can_read_limited: bool
    can_read_all: bool
    can_subscribe: bool
    can_manage: bool

    class Config:
        from_attributes = True


class ShowUserRightsResp(BaseModel):
    user_login: str
    can_read_limited: bool = False
    can_read_all: bool = False
    can_subscribe: bool = False
    can_manage: bool = False

    class Config:
        from_attributes = True
