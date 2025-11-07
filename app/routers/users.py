from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import UserResponse
from app.utils.jsend import JSendResponse
from app.auth.dependencies import get_current_user
from app.services.websocket import manager

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.delete("/me")
async def delete_user(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Delete current user account (requires authentication).

    This will:
    - Delete user from database
    - Delete user's avatar file
    - Revoke all refresh tokens
    - Close all WebSocket connections
    """
    user_id = current_user.id

    # Delete avatar file if exists
    if current_user.avatar_url:
        avatar_path = Path(current_user.avatar_url.lstrip("/"))
        if avatar_path.exists():
            try:
                avatar_path.unlink()
            except Exception:
                pass

    # Revoke all refresh tokens
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()

    # Delete user
    db.delete(current_user)
    db.commit()

    # Close all WebSocket connections
    manager.disconnect_all_user_connections(user_id)

    return JSendResponse.success(
        data={"message": "User account successfully deleted"}
    )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information (requires authentication)."""
    return JSendResponse.success(data={
        "id": current_user.id,
        "identifier": current_user.identifier,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    })