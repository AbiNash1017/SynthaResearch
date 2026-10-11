from typing import Optional
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from beanie import PydanticObjectId
from db.models import User
from auth.utils import decode_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """FastAPI dependency to extract and validate the authenticated user from the Bearer JWT."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user identifier.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await User.get(PydanticObjectId(user_id))
    except Exception:
        user = None

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_user_from_auth_or_query(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Query(None)
) -> User:
    """Dependency supporting either Authorization Bearer header or ?token= query parameter."""
    raw_token = None
    if credentials and credentials.credentials:
        raw_token = credentials.credentials
    elif token:
        raw_token = token

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token or token parameter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(raw_token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject.")
        user = await User.get(PydanticObjectId(user_id))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive.")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")
