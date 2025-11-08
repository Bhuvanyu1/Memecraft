import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from PIL import Image
import io
import logging
from config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """Local file storage service"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_file(self, file: UploadFile, folder: str = "general") -> str:
        """Save uploaded file and return URL"""
        try:
            # Create folder if doesn't exist
            folder_path = self.upload_dir / folder
            folder_path.mkdir(exist_ok=True)
            
            # Generate unique filename
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = folder_path / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Return relative URL path
            relative_path = f"/uploads/{folder}/{unique_filename}"
            logger.info(f"Saved file: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            raise Exception(f"Failed to save file: {str(e)}")
    
    async def save_image(self, file: UploadFile, folder: str = "images", 
                        max_width: Optional[int] = None, max_height: Optional[int] = None) -> str:
        """Save and optionally resize image"""
        try:
            content = await file.read()
            image = Image.open(io.BytesIO(content))
            
            # Resize if needed
            if max_width or max_height:
                image.thumbnail((max_width or 9999, max_height or 9999), Image.Resampling.LANCZOS)
            
            # Save to temporary buffer
            buffer = io.BytesIO()
            image_format = image.format or 'PNG'
            image.save(buffer, format=image_format)
            buffer.seek(0)
            
            # Create folder if doesn't exist
            folder_path = self.upload_dir / folder
            folder_path.mkdir(exist_ok=True)
            
            # Generate unique filename
            file_ext = f".{image_format.lower()}"
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = folder_path / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(buffer.getvalue())
            
            # Return relative URL path
            relative_path = f"/uploads/{folder}/{unique_filename}"
            logger.info(f"Saved image: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Image save error: {str(e)}")
            raise Exception(f"Failed to save image: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            # Remove /uploads/ prefix if present
            if file_path.startswith('/uploads/'):
                file_path = file_path[9:]
            
            full_path = self.upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"File delete error: {str(e)}")
            return False
    
    def get_storage_used(self, user_id: str) -> int:
        """Calculate storage used by user (in bytes)"""
        try:
            user_folder = self.upload_dir / user_id
            if not user_folder.exists():
                return 0
            
            total_size = sum(f.stat().st_size for f in user_folder.rglob('*') if f.is_file())
            return total_size
            
        except Exception as e:
            logger.error(f"Storage calculation error: {str(e)}")
            return 0

storage_service = StorageService()
