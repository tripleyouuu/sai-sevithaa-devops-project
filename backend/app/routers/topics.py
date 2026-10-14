from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Subject, Topic, utcnow
from ..schemas import Status, TopicCreate, TopicOut, TopicUpdate

router = APIRouter(prefix="/api/topics", tags=["topics"])


def get_or_404(db: Session, topic_id: int) -> Topic:
    topic = db.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


def ensure_subject(db: Session, subject_id: int):
    if db.get(Subject, subject_id) is None:
        raise HTTPException(status_code=400, detail="Subject does not exist")


def sync_completed_at(topic: Topic):
    if topic.status == "done" and topic.completed_at is None:
        topic.completed_at = utcnow()
    elif topic.status != "done":
        topic.completed_at = None


@router.get("", response_model=list[TopicOut])
def list_topics(
    subject_id: int | None = None,
    status: Status | None = None,
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
):
    query = select(Topic).order_by(Topic.subject_id, Topic.id)
    if subject_id is not None:
        query = query.where(Topic.subject_id == subject_id)
    if status is not None:
        query = query.where(Topic.status == status)
    if search:
        query = query.where(Topic.title.ilike(f"%{search}%"))
    return db.scalars(query).all()


@router.get("/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, topic_id)


@router.post("", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic(payload: TopicCreate, db: Session = Depends(get_db)):
    ensure_subject(db, payload.subject_id)
    topic = Topic(**payload.model_dump())
    sync_completed_at(topic)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.put("/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, payload: TopicUpdate, db: Session = Depends(get_db)):
    topic = get_or_404(db, topic_id)
    changes = payload.model_dump(exclude_unset=True)
    if "subject_id" in changes:
        ensure_subject(db, changes["subject_id"])
    for field, value in changes.items():
        setattr(topic, field, value)
    sync_completed_at(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = get_or_404(db, topic_id)
    db.delete(topic)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
