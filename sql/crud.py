from sqlalchemy.orm import Session

from . import models, schema


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    db_user = models.User(
        email=user.email,
        password=user.password,
        host=user.host,
        smtp_username=user.smtp_username,
        smtp_password=user.smtp_password,
        smtp_host=user.smtp_host,
        pop_username=user.pop_username,
        pop_password=user.pop_password,
        pop_port=user.pop_port,
        pop_host=user.pop_host,
    )
    db.add(db_user)
    db.commit()

    db.refresh(db_user)
    return db_user


def create_mail(db: Session, mail: schema.Mail):
    db_mail = models.Mail(
        id=mail.id,
        message_id=mail.message_id,
        from_name=mail.from_name,
        from_id=mail.from_id,
        subject=mail.subject,
        body_plain=mail.body_plain,
        body_html=mail.body_html,
        headers=mail.headers,
        date=mail.date,
        owner=mail.owner,
        to_address=mail.to_addresses,
    )
    db.add(db_mail)
    db.commit()
    db.refresh(db_mail)
    return db_mail


def read_mail_with_id(db: Session, message_id: str):
    db.query(models.User).filter(models.Mail.message_id == message_id).first()


def get_user_mails(db: Session, user_id: int):
    db.query(models.User).filter(models.Mail.owner_id == user_id)
