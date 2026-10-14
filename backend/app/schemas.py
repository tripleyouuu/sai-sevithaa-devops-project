from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["todo", "in_progress", "done"]


class SubjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    code: str | None = Field(default=None, max_length=20)
    color: str = Field(default="#6366f1", pattern=r"^#[0-9a-fA-F]{6}$")
    exam_date: date | None = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    code: str | None = Field(default=None, max_length=20)
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    exam_date: date | None = None


class SubjectOut(SubjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    topic_count: int = 0
    done_count: int = 0
    progress: float = 0.0


class TopicBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    status: Status = "todo"
    difficulty: int = Field(default=3, ge=1, le=5)
    estimated_hours: float = Field(default=1.0, gt=0, le=200)
    notes: str | None = None


class TopicCreate(TopicBase):
    subject_id: int


class TopicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: Status | None = None
    difficulty: int | None = Field(default=None, ge=1, le=5)
    estimated_hours: float | None = Field(default=None, gt=0, le=200)
    notes: str | None = None
    subject_id: int | None = None


class TopicOut(TopicBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class SubjectProgress(BaseModel):
    id: int
    name: str
    color: str
    total: int
    done: int
    progress: float
    hours_left: float
    exam_date: date | None


class Stats(BaseModel):
    total_topics: int
    todo: int
    in_progress: int
    done: int
    completion: float
    hours_total: float
    hours_done: float
    hours_left: float
    avg_difficulty: float
    by_difficulty: dict[int, int]
    subjects: list[SubjectProgress]
