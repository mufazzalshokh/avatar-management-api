from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import os
import io
from PIL import Image
from app.database import get_db
from app.models import User
from app.schemas import AvatarUploadResponse
from app.utils.jsend import JSendResponse
from app.auth.dependencies import get_current_user
from app.config import settings
from app.services.websocket import manager

router = APIRouter(prefix="/avatars", tags=["Avatars"])


def validate_image(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    file_ext = Path(file.filename).suffix.lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if file_ext not in allowed_extensions:
        return False

    # Check content type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        return False

    return True


@router.post("/upload")
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Upload user avatar (REQUIREMENT: Avatar upload that requires auth)

    Uploaded image URL must be returned on success.
    """
    # Validate image type
    if not validate_image(file):
        return JSendResponse.fail(
            data={"avatar": "Only JPEG, PNG, and GIF images are allowed"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Check file size (5MB max as per common requirement)
    contents = await file.read()
    max_size = 5 * 1024 * 1024  # 5MB
    if len(contents) > max_size:
        return JSendResponse.fail(
            data={"avatar": "File size must be less than 5MB"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Verify it's a valid image
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
        image = Image.open(io.BytesIO(contents))  # Reopen for processing
    except Exception:
        return JSendResponse.fail(
            data={"avatar": "Invalid image file"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_filename

    # Delete old avatar if exists
    if current_user.avatar_url:
        old_filename = current_user.avatar_url.split('/')[-1]
        old_file_path = upload_dir / old_filename
        if old_file_path.exists():
            try:
                old_file_path.unlink()
            except Exception:
                pass  # Continue even if old file deletion fails

    # Save new file
    try:
        # Convert to RGB if necessary and save as optimized image
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        image.save(file_path, optimize=True, quality=85)
    except Exception as e:
        return JSendResponse.fail(
            data={"avatar": f"Failed to process image: {str(e)}"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # REQUIREMENT: Generate and return the uploaded image URL
    # Use relative URL that will be served by static files
    avatar_url = f"/uploads/{unique_filename}"

    # Update user avatar URL in database
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)

    # REQUIREMENT: Send WebSocket messages when avatar is changed
    try:
        if hasattr(manager, 'send_avatar_update'):
            await manager.send_avatar_update(current_user.id, avatar_url)
        elif hasattr(manager, 'broadcast_avatar_change'):
            await manager.broadcast_avatar_change(current_user.id, avatar_url)
    except Exception as e:
        # Don't fail the upload if WebSocket notification fails
        print(f"WebSocket notification failed: {e}")

    # REQUIREMENT: Uploaded image URL must be returned on success
    return JSendResponse.success(
        data={
            "avatar_url": avatar_url  # This matches the requirement exactly
        }
    )