from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
import jwt
from beanie import PydanticObjectId

from db.models import User
from auth.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
)
from auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from auth.dependencies import get_current_user
from config.settings import REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister, response: Response):
    """Registers a new user account and returns JWT credentials."""
    existing = await User.find_one(User.email == payload.email.lower().strip())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = User(
        email=payload.email.lower().strip(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip() if payload.full_name else None
    )
    await user.insert()

    user_id_str = str(user.id)
    access_token = create_access_token(user_id=user_id_str)
    refresh_token = create_refresh_token(user_id=user_id_str)

    # Set secure HttpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False  # Set to True in production HTTPS
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user_id_str,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, response: Response):
    """Authenticates a user with email and password, returning JWT tokens."""
    user = await User.find_one(User.email == payload.email.lower().strip())
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated."
        )

    user_id_str = str(user.id)
    access_token = create_access_token(user_id=user_id_str)
    refresh_token = create_refresh_token(user_id=user_id_str)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user_id_str,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
    )


@router.post("/refresh")
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    payload: Optional[RefreshTokenRequest] = None
):
    """Issues a fresh access token using a valid refresh token from cookie or request body."""
    token = None
    if payload and payload.refresh_token:
        token = payload.refresh_token
    elif "refresh_token" in request.cookies:
        token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing."
        )

    try:
        decoded = decode_token(token)
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type."
            )
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing user identifier."
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please log in again."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    try:
        user = await User.get(PydanticObjectId(user_id))
    except Exception:
        user = None

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated."
        )

    new_access_token = create_access_token(user_id=str(user.id))
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(response: Response):
    """Logs the user out by clearing the refresh token cookie."""
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully."}
