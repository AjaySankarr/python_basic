from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from webapp.api.deps import get_current_user, get_db
from webapp.core.config import settings
from webapp.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from webapp.models.user import RefreshToken, User
from webapp.schemas.user import (
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.scalar(select(User).where(User.email == data.email))
    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        ) from exc
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user",
        ) from exc

    return user


@router.post("/login", response_model=TokenResponse)
async def login_user(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == data.email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_token = create_access_token(user.id)
    raw_refresh_token = generate_refresh_token()

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_record)

    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Could not complete login") from exc

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(data.refresh_token)

    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )
    stored_token = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if (
        stored_token is None
        or stored_token.revoked_at is not None
        or stored_token.expires_at <= now
    ):
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token"
        )

    user = await db.get(User, stored_token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    stored_token.revoked_at = now
    new_raw_token = generate_refresh_token()
    new_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_raw_token),
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_record)

    new_access_token = create_access_token(user.id)

    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail="Could not refresh session"
        ) from exc

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_raw_token,
        token_type="bearer",
    )


@router.post("/logout")
async def logout_user(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(data.refresh_token)

    stored_token = await db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )

    if stored_token is None or stored_token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    stored_token.revoked_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Could not complete logout") from exc

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user