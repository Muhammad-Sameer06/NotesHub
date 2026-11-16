"""Notes CRUD API: Create, Read, Update, Delete + search and tag filter."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Note, Tag
from app.schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _escape_like(s: str) -> str:
    """So a search for '50%' matches the text '50%', not 'anything starting with 50'."""
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    if not names:
        return []
    found = {t.name: t for t in db.scalars(select(Tag).where(Tag.name.in_(names)))}
    for name in names:
        if name not in found:
            found[name] = Tag(name=name)
            db.add(found[name])
    return [found[n] for n in names]


def _get_note_or_404(db: Session, note_id: int) -> Note:
    note = db.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("", response_model=list[NoteOut])
def list_notes(
    search: str | None = Query(default=None, max_length=100, description="Text in title or content"),
    tag: str | None = Query(default=None, max_length=50, description="Only notes with this tag"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Note).order_by(Note.updated_at.desc(), Note.id.desc())
    if search:
        pattern = f"%{_escape_like(search)}%"
        stmt = stmt.where(or_(Note.title.ilike(pattern, escape="\\"), Note.content.ilike(pattern, escape="\\")))
    if tag:
        stmt = stmt.where(Note.tags.any(Tag.name == tag.strip().lower()))
    return db.scalars(stmt.limit(limit).offset(offset)).all()


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=data.title, content=data.content, tags=_get_or_create_tags(db, data.tags))
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    return _get_note_or_404(db, note_id)


@router.patch("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteUpdate, db: Session = Depends(get_db)):
    note = _get_note_or_404(db, note_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("title") is None:
        changes.pop("title", None)  # title can't be cleared
    if "content" in changes:
        note.content = changes["content"] or ""
    if "title" in changes:
        note.title = changes["title"]
    if "tags" in changes:
        note.tags = _get_or_create_tags(db, changes["tags"] or [])
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = _get_note_or_404(db, note_id)
    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
