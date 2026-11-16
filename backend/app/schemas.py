"""API input/output shapes (Pydantic). FastAPI uses these to validate requests
and returns a clear 422 error if the client sends bad data."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_tags(tags: list[str]) -> list[str]:
    """'  Work', 'work', '' -> ['work']  (trim, lowercase, remove empty + duplicates, keep order)."""
    seen: list[str] = []
    for t in tags:
        t = t.strip().lower()
        if t and t not in seen:
            seen.append(t)
    return seen


TagList = list[str]


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", max_length=10_000)
    tags: TagList = Field(default_factory=list, max_length=10)

    @field_validator("tags")
    @classmethod
    def _tags(cls, v: list[str]) -> list[str]:
        if any(len(t.strip()) > 50 for t in v):
            raise ValueError("each tag must be at most 50 characters")
        return normalize_tags(v)


class NoteUpdate(BaseModel):
    """PATCH: every field is optional; only the fields you send are changed."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=10_000)
    tags: TagList | None = Field(default=None, max_length=10)

    @field_validator("tags")
    @classmethod
    def _tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        if any(len(t.strip()) > 50 for t in v):
            raise ValueError("each tag must be at most 50 characters")
        return normalize_tags(v)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("tags", mode="before")
    @classmethod
    def _tag_names(cls, v):
        # DB gives Tag objects; API returns plain names
        return [t.name if hasattr(t, "name") else t for t in v]
