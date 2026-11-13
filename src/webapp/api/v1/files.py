
from pathlib import Path
from uuid import uuid4

import aiofiles

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from webapp.api.deps import get_current_user
from webapp.models.user import User


router = APIRouter(prefix="/files", tags=["File Upload"])


# Storage directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

# Maximum file size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/single", status_code=status.HTTP_201_CREATED)
async def upload_single_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    print('file===>',file)
    # 1. Validate filename
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed",
        )

    # 2. Generate a unique filename
    unique_filename = f"{uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / unique_filename

    # 3. Save file in chunks and validate size
    total_size = 0

    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds 5 MB",
                    )

                await buffer.write(chunk)

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()

    # 4. Return file information
    return {
        "message": "File uploaded successfully",
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "content_type": file.content_type,
        "size": total_size,
        "uploaded_by": current_user.id,
    }





@router.post("/multiple", status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    print("files =====>",files)
    uploaded_files = []
    saved_paths = []

    try:
        for file in files:

            # Validate extension
            extension = Path(file.filename or "").suffix.lower()

            if extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}",
                )

            unique_filename = f"{uuid4().hex}{extension}"
            file_path = UPLOAD_DIR / unique_filename

            total_size = 0

            async with aiofiles.open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    total_size += len(chunk)

                    if total_size > MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=413,
                            detail=f"{file.filename} exceeds 5 MB",
                        )

                    await buffer.write(chunk)

            saved_paths.append(file_path)

            uploaded_files.append({
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "content_type": file.content_type,
                "size": total_size,
            })

    except Exception:
        # Remove already saved files if any upload fails
        for path in saved_paths:
            path.unlink(missing_ok=True)
        raise

    finally:
        for file in files:
            await file.close()

    return {
        "message": "Files uploaded successfully",
        "total_files": len(uploaded_files),
        "uploaded_by": current_user.id,
        "files": uploaded_files,
    }



# Needed packages:
# uv add python-multipart
# uv add aiofiles