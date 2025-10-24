from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from .database import get_session
from .models import User
from .schemas import TokenPayload
from .security import decode_access_token
from sqlmodel import select

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing token')
    try:
        payload = decode_access_token(credentials.credentials)
        token = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    result = await session.exec(select(User).where(User.email == token.email))
    user = result.first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


def require_role(role: str):
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        hierarchy = {'admin': 3, 'manager': 2, 'user': 1}
        if hierarchy.get(user.role, 0) < hierarchy.get(role, 0):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        return user

    return _dependency
