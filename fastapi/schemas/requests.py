from pydantic import BaseModel


class SignupReq(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class LoginReq(BaseModel):
    login: str
    password: str


class ChangeUserInfoReq(BaseModel):
    login: str
    password: str
    new_login: str | None = None
    new_password: str | None = None
    new_first_name: str | None = None
    new_last_name: str | None = None


class Create_role_req(BaseModel):
    name: str
    can_read_limited: bool = False
    can_read_all: bool = False
    can_subscribe: bool = False
    can_manage: bool = False


class Delete_role_req(BaseModel):
    name: str


class Change_role_req(BaseModel):
    name: str
    can_read_limited: bool = False
    can_read_all: bool = False
    can_subscribe: bool = False
    can_manage: bool = False


class Assign_user_role_req(BaseModel):
    for_user_login: str
    role_name: str


class Deprive_user_role_req(BaseModel):
    for_user_login: str
    role_name: str


class Show_user_rights_req(BaseModel):
    for_user_login: str
