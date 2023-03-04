from typing import List
from fastapi import FastAPI, HTTPException, status
import uvicorn
import os
import poplib
from pydantic import BaseModel
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr


port = int(os.environ["PORT"])

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


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
    msg = Parser().parsestr(msg_content)
    return msg


@app.get("/")
async def main():
    return {"hello": "world"}


@app.get("/api/login")
async def login(user: User):
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


@app.get("/api/messages")
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
            messages = []

            for i in range(1, numMsgs + 1):
                (header, lines, octets) = pop_client_instance.retr(i)
                print(
                    {
                        "id": i,
                        "header": header,
                        "msg": clean_msg(lines),
                        "octets": octets,
                    }
                )
                messages.append(
                    {
                        "id": i,
                        "header": header,
                        "msg": clean_msg(lines),
                        "octets": octets,
                    }
                )
            pop_client_instance.quit()
            return {
                "data": {
                    "numMsgs": numMsgs,
                    "totalSize": totalSize,
                    "messages": messages,
                }
            }


uvicorn.run(app, host="0.0.0.0", port=port)
