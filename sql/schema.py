from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    host: str
    password: str
    smtp_username: None | str
    smtp_password: None | str
    smtp_host: None | str
    smtp_port: None | str
    pop_username: None | str
    pop_password: None | str
    pop_port: None | str
    pop_host: None | str


class Mail(BaseModel):
    id: int
    message_id: str
    from_name: str
    from_id: str
    subject: str
    body_plain: str
    body_html: str
    headers: str
    date: str
    to_addresses: str
    owner: int

    class Config:
        orm_mode = True


class User(UserCreate):
    id: int
    mails: list[Mail] = []

    class Config:
        orm_mode = True
