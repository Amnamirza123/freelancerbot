from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services import knowledge_base as kb_service
from app.auth.dependencies import require_admin
from fastapi import UploadFile, File, Form

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


class KnowledgeBaseCreate(BaseModel):
    category: str  # services | pricing | technologies | packages | policies | faq
    content: str
    source_label: str | None = None


class KnowledgeBaseUpdate(BaseModel):
    content: str


@router.get("")
def list_entries(category: str | None = None, user: dict = Depends(require_admin)):
    return kb_service.list_entries(category)


@router.post("")
def create_entry(payload: KnowledgeBaseCreate, user: dict = Depends(require_admin)):
    return kb_service.create_entry(payload.category, payload.content, payload.source_label)


@router.put("/{entry_id}")
def update_entry(entry_id: str, payload: KnowledgeBaseUpdate, user: dict = Depends(require_admin)):
    return kb_service.update_entry_content(entry_id, payload.content)


@router.delete("/{entry_id}")
def delete_entry(entry_id: str, user: dict = Depends(require_admin)):
    return kb_service.delete_entry(entry_id)


@router.delete("/by-source/{source_label}")
def delete_by_source(source_label: str, user: dict = Depends(require_admin)):
    count = kb_service.delete_by_source_label(source_label)
    return {"deleted_chunks": count}


@router.post("/upload")
async def upload_document(
    category: str = Form(...), file: UploadFile = File(...), user: dict = Depends(require_admin)
):
    file_bytes = await file.read()
    try:
        return kb_service.create_entry_from_file(category, file.filename, file_bytes)
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(400, str(exc))