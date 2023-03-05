from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    host = Column(String, index=True)
    password = Column(String)
    smtp_username = Column(String, default=email)
    smtp_password = Column(String, default=password)
    smtp_port = Column(Integer, default=465)
    smtp_host = Column(String, default=host)
    pop_username = Column(String, default=email)
    pop_password = Column(String, default=password)
    pop_port = Column(Integer, default=110)
    pop_host = Column(String, default=host)
    mails = relationship("Mail", back_populates="owner")


class Mail(Base):
    __tablename__ = "mails"

    id = Column(Integer, index=True)
    message_id = Column(String)
    from_name = Column(String)
    from_id = Column(String)
    subject = Column(String)
    body_plain = Column(String)
    body_html = Column(String)
    headers = Column(String)
    date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    to_addresses = Column(String)
    owner = relationship("User", back_populates="mails")
