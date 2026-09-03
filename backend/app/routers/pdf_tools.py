from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.dependencies import get_current_user
from app.models.user import User
from app.services.pdf_date_service import replace_expiry_date

router = APIRouter(prefix='/pdf-tools', tags=['pdf-tools'])

_DATE_RE = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
_MAX_UPLOAD_BYTES = 500 * 1024 * 1024


def _validate_date(value: str, field_name: str) -> str:
    if not _DATE_RE.fullmatch(value):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'{field_name}: используйте формат ДД.ММ.ГГГГ',
        )
    try:
        datetime.strptime(value, '%d.%m.%Y')
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'{field_name}: некорректная дата',
        ) from exc
    return value


def _remove_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


@router.post('/replace-expiry-date')
async def replace_pdf_expiry_date(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    manufacture_date: str = Form(...),
    current_expiry_date: str = Form(...),
    new_expiry_date: str = Form(...),
    _: User = Depends(get_current_user),
) -> FileResponse:
    if file.content_type != 'application/pdf' and not (file.filename or '').lower().endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='Нужен PDF-файл')

    manufacture_date = _validate_date(manufacture_date, 'Дата от')
    current_expiry_date = _validate_date(current_expiry_date, 'Текущая дата до')
    new_expiry_date = _validate_date(new_expiry_date, 'Новая дата до')

    source_fd, source_path = tempfile.mkstemp(suffix='.pdf', prefix='prostomark-source-')
    os.close(source_fd)
    output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='prostomark-result-')
    os.close(output_fd)

    try:
        total = 0
        with open(source_path, 'wb') as target:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > _MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail='PDF больше 500 МБ. Разделите файл на части.',
                    )
                target.write(chunk)

        try:
            result = replace_expiry_date(
                source_path=source_path,
                output_path=output_path,
                manufacture_date=manufacture_date,
                current_expiry_date=current_expiry_date,
                new_expiry_date=new_expiry_date,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Не удалось обработать PDF. Проверьте, что даты находятся в текстовом слое файла.',
            ) from exc

        if result.replacements == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    'Совпадения не найдены. Проверьте дату производства и текущую дату окончания срока годности.'
                ),
            )

        original_stem = Path(file.filename or 'labels').stem
        download_name = f'{original_stem}_expiry_fixed.pdf'
        background_tasks.add_task(_remove_file, output_path)

        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename=download_name,
            headers={
                'X-ProstoMark-Replacements': str(result.replacements),
                'X-ProstoMark-Pages-Changed': str(result.pages_changed),
                'X-ProstoMark-Pages-Total': str(result.pages_total),
            },
        )
    finally:
        _remove_file(source_path)
        # If an error happened before FileResponse was returned, output is not
        # scheduled for cleanup and must be deleted immediately.
        if not background_tasks.tasks:
            _remove_file(output_path)
