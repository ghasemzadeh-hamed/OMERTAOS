from datetime import datetime, timedelta
from typing import Any, Optional
from jose import jwt
from passlib.context import CryptContext
from .settings import settings

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str, expires_delta: Optional[int] = None) -> str:
    expires = datetime.utcnow() + timedelta(minutes=expires_delta or 60)
    payload: dict[str, Any] = {'sub': subject, 'email': subject, 'role': role, 'exp': expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm='HS256')


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=['HS256'])
