import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings


def save_uploaded_file(company_id: str, file: UploadFile) -> str:
    extension = Path(file.filename or '').suffix
    safe_name = f'{uuid.uuid4()}{extension}'
    company_dir = settings.storage_path / 'documents' / company_id
    company_dir.mkdir(parents=True, exist_ok=True)

    target_path = company_dir / safe_name
    with target_path.open('wb') as output:
        output.write(file.file.read())

    return str(target_path)


def delete_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
