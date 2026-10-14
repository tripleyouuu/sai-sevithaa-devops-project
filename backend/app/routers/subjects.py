from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Subject, Topic
from ..schemas import SubjectCreate, SubjectOut, SubjectUpdate

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def with_counts(db: Session, subjects: list[Subject]) -> list[SubjectOut]:
    if not subjects:
        return []

    rows = db.execute(
        select(
            Topic.subject_id,
            func.count(Topic.id),
            func.sum(case((Topic.status == "done", 1), else_=0)),
        )
        .where(Topic.subject_id.in_([s.id for s in subjects]))
        .group_by(Topic.subject_id)
    ).all()
    counts = {sid: (total, done or 0) for sid, total, done in rows}

    result = []
    for s in subjects:
        total, done = counts.get(s.id, (0, 0))
        out = SubjectOut.model_validate(s)
        out.topic_count = total
        out.done_count = done
        out.progress = round(done / total * 100, 1) if total else 0.0
        result.append(out)
    return result


def get_or_404(db: Session, subject_id: int) -> Subject:
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.get("", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.scalars(select(Subject).order_by(Subject.name)).all()
    return with_counts(db, list(subjects))


@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    return with_counts(db, [get_or_404(db, subject_id)])[0]


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    subject = Subject(**payload.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return with_counts(db, [subject])[0]


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, payload: SubjectUpdate, db: Session = Depends(get_db)):
    subject = get_or_404(db, subject_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return with_counts(db, [subject])[0]


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = get_or_404(db, subject_id)
    db.delete(subject)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
