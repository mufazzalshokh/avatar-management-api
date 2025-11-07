from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserResponse
from app.utils.password import hash_password, verify_password
from app.utils.jsend import JSendResponse
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user with identifier and password.
    Returns OAuth2.0 compliant access and refresh tokens.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.identifier == user_data.identifier).first()
    if existing_user:
        return JSendResponse.fail(
            data={"identifier": "User with this identifier already exists"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        identifier=user_data.identifier,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create tokens
    access_token = create_access_token(data={"sub": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.id})

    # Store refresh token in database
    refresh_token_obj = RefreshToken(
        user_id=new_user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token_obj)
    db.commit()

    # Prepare response
    token_data = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return JSendResponse.success(
        data={
            "user": {
                "id": new_user.id,
                "identifier": new_user.identifier,
                "avatar_url": new_user.avatar_url,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        },
        status_code=status.HTTP_201_CREATED
    )


@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with identifier and password.
    Returns OAuth2.0 compliant access and refresh tokens.
    """
    # Find user
    user = db.query(User).filter(User.identifier == credentials.identifier).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        return JSendResponse.fail(
            data={"credentials": "Invalid identifier or password"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return JSendResponse.fail(
            data={"account": "Account is inactive"},
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Store refresh token
    refresh_token_obj = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token_obj)
    db.commit()

    # Prepare response
    token_data = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    user_response = UserResponse.model_validate(user)

    return JSendResponse.success(
        data={
            "user": user_response.model_dump(),
            "tokens": token_data.model_dump()
        }
    )


@router.post("/refresh")
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token (OAuth2.0 token rotation).
    """
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    if not payload or not verify_token_type(token_data.refresh_token, "refresh"):
        return JSendResponse.fail(
            data={"token": "Invalid refresh token"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Check if token exists and is not revoked
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.is_revoked == False
    ).first()

    if not stored_token:
        return JSendResponse.fail(
            data={"token": "Refresh token not found or revoked"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Check expiration
    if stored_token.expires_at < datetime.utcnow():
        return JSendResponse.fail(
            data={"token": "Refresh token expired"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    user_id = payload.get("sub")

    # Create new tokens (token rotation)
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    # Revoke old refresh token
    stored_token.is_revoked = True

    # Store new refresh token
    new_refresh_token_obj = RefreshToken(
        user_id=user_id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_refresh_token_obj)
    db.commit()

    # Prepare response
    token_response = TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return JSendResponse.success(data=token_response.model_dump())