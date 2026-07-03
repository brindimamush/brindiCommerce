import os
import shutil
from abc import ABC, abstractmethod
from fastapi import UploadFile
from pathlib import Path
import uuid

class StorageBackend(ABC):
    @abstractmethod
    async def save_file(self, file: UploadFile, directory: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        pass

class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str = "media"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, directory: str) -> str:
        target_dir = self.base_path / directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = target_dir / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return f"/{self.base_path}/{directory}/{unique_filename}"

    async def delete_file(self, file_path: str) -> bool:
        path = Path(file_path.lstrip("/"))
        if path.exists() and path.is_file():
            os.remove(path)
            return True
        return False

# Dependency to be injected in routers
def get_storage_backend() -> StorageBackend:
    return LocalStorageBackend()