import aiofiles
from fastapi import UploadFile, HTTPException
from pathlib import Path
import uuid
from PIL import Image
from io import BytesIO
from config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE


async def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> str:
    """
    Save uploaded file and return the file path

    Args:
        upload_file: The uploaded file
        subfolder: Optional subfolder within uploads directory

    Returns:
        str: Relative path to the saved file
    """
    # Check file extension
    file_ext = Path(upload_file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await upload_file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.1f}MB"
        )

    # Validate image
    try:
        image = Image.open(BytesIO(content))
        image.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    file_path = upload_dir / filename

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Return relative path
    return f"/{settings.UPLOAD_DIR}/{subfolder}/{filename}"


def delete_file(file_path: str) -> bool:
    """
    Delete a file from the filesystem

    Args:
        file_path: Path to the file

    Returns:
        bool: True if file was deleted, False otherwise
    """
    try:
        # Remove leading slash if present
        if file_path.startswith("/"):
            file_path = file_path[1:]

        full_path = Path(file_path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception:
        return False