import poplib
from main import User
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import smtplib, ssl
import mailparser


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


def clean_msg(lines: list[bytes]):
    msg_content = b"\r\n".join(lines).decode("utf-8")
    mail = mailparser.parse_from_string(msg_content)
    return mail
