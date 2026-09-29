from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.db import get_conn


settings = get_settings()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        password_hash
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if not subject:
            return None

        return int(subject)

    except (JWTError, ValueError, TypeError):
        return None


def create_user(
    name: str,
    email: str,
    password: str
):
    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()

        if existing:
            return None

        password_hash = hash_password(password)

        cursor = conn.execute(
            """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                name.strip(),
                email.lower(),
                password_hash,
            ),
        )

        conn.commit()

        return conn.execute(
            """
            SELECT id, name, email, created_at
            FROM users
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    finally:
        conn.close()


def authenticate_user(
    email: str,
    password: str
):
    conn = get_conn()

    try:
        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email.lower(),),
        ).fetchone()

        if not user:
            return None

        if not verify_password(
            password,
            user["password_hash"]
        ):
            return None

        return user

    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_conn()

    try:
        return conn.execute(
            """
            SELECT id, name, email, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    finally:
        conn.close()