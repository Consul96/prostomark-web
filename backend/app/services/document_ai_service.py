from pathlib import Path

from openai import OpenAI
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.document import update_document
from app.models.document import Document
from app.models.enums import DocumentStatus


class DocumentAIService:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def extract_text(self, file_path: str, mime_type: str) -> str:
        path = Path(file_path)
        if not path.exists():
            return ''

        if mime_type == 'application/pdf' or path.suffix.lower() == '.pdf':
            reader = PdfReader(file_path)
            chunks = [page.extract_text() or '' for page in reader.pages]
            return '\n'.join(chunks).strip()

        try:
            return path.read_text(encoding='utf-8', errors='ignore').strip()
        except OSError:
            return ''

    def summarize(self, text: str) -> str:
        if not text:
            return ''
        if self._client is None:
            return 'AI summary unavailable: OPENAI_API_KEY is not configured.'

        response = self._client.responses.create(
            model=settings.openai_model,
            input=(
                'Сформируй структурированное краткое резюме документа для оператора маркировки. '
                'Укажи ключевые реквизиты, риски и недостающие данные. Текст:\n\n' + text[:12000]
            ),
        )
        return (response.output_text or '').strip()


service = DocumentAIService()


def process_document(db: Session, document: Document) -> None:
    update_document(db, document, {'status': DocumentStatus.PROCESSING})
    db.commit()

    try:
        extracted = service.extract_text(document.file_path, document.mime_type)
        summary = service.summarize(extracted)
        update_document(
            db,
            document,
            {
                'extracted_text': extracted,
                'ai_summary': summary,
                'status': DocumentStatus.PROCESSED,
            },
        )
        db.commit()
    except Exception:
        update_document(db, document, {'status': DocumentStatus.FAILED})
        db.commit()
        raise
