from typing import List, Union, Any
from fastapi import Depends, FastAPI, HTTPException, status
import uvicorn
import os
import poplib
from pydantic import BaseModel
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import smtplib, ssl
import mailparser
from fastapi.middleware.cors import CORSMiddleware

# from envelope import Envelope
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import Session

from sql import crud, models, schema
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


port = int(os.environ["PORT"])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    username: str
    password: str


class Message(BaseModel):
    from_addr: str
    password: str
    subject: str
    body: str
    to_addr: str


class BaseResponse(BaseModel):
    data: str


class FetchMailResponse_(BaseModel):
    number_of_messages: int
    total_size: int
    messages: List[Any]


class FetchMailResponse(BaseModel):
    data: FetchMailResponse_


def pop_login(user: User):
    try:
        pop_client_instance = poplib.POP3_SSL("box.0xparc.space", port=995)
        print(user)
        pop_client_instance.user(user.username)
        pop_client_instance.pass_(user.password)
    except:
        pop_client_instance = None
    finally:
        return pop_client_instance


def clean_msg(lines: List[bytes]):
    msg_content = b"\r\n".join(lines).decode("utf-8")
    mail = mailparser.parse_from_string(msg_content)
    return mail


@app.get("/ping")
async def main() -> BaseResponse:
    return BaseResponse(**({"data": "pong"}))


@app.post("/api/login/")
async def login(user: User, response_model=BaseResponse):
    pop_client_instance = pop_login(user)
    match pop_client_instance:
        case None:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication not successful",
            )
        case pop_client_instance:
            pop_client_instance.quit()
            return {"data": "Successfully Authenticated"}


@app.post("/api/messages/")
async def messages(user: User):
    pop_client_instance = pop_login(user)
    match pop_client_instance:
        case None:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication not successful",
            )
        case pop_client_instance:
            (numMsgs, totalSize) = pop_client_instance.stat()
            messages: List[mailparser.MailParser] = []

            for i in range(1, numMsgs + 1):
                (header, lines, octets) = pop_client_instance.retr(i)
                print(
                    clean_msg(lines),
                )
                messages.append(
                    clean_msg(lines),
                )
            pop_client_instance.quit()
            return {
                "data": {
                    "number_of_messages": numMsgs,
                    "total_size": totalSize,
                    "messages": messages,
                }
            }


@app.post("/api/message/")
async def message(message: Message):
    try:
        message_mime = MIMEMultipart()
        message_mime["From"] = message.from_addr
        message_mime["To"] = message.to_addr
        message_mime["Subject"] = message.subject
        # message_mime["Bcc"] = receiver_email  # Recommended for mass emails

        # Add body to email
        message_mime.attach(MIMEText(message.body, "plain"))
        text = message_mime.as_string()
        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("box.0xparc.space", 465, context=context) as server:
            server.login(message.from_addr, message.password)
            server.sendmail(message.from_addr, message.to_addr, text)
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mail transfer failed",
        )
    else:
        return {"data": "Mail transfer succeded"}


@app.post("/api/signup/")
async def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    crud.create_user(db, user)


@app.post("/api/users/")
async def get_users(user: schema.UserCreate, db: Session = Depends(get_db)):
    return crud.get_users(db)


uvicorn.run(app, host="0.0.0.0", port=port)
