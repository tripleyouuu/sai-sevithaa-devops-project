from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Subject, Topic
from ..schemas import Stats, SubjectProgress

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    subjects = db.scalars(select(Subject).order_by(Subject.name)).all()
    topics = db.scalars(select(Topic)).all()

    counts = {"todo": 0, "in_progress": 0, "done": 0}
    by_difficulty = {level: 0 for level in range(1, 6)}
    hours_total = hours_done = 0.0
    per_subject = {s.id: {"total": 0, "done": 0, "hours_left": 0.0} for s in subjects}

    for t in topics:
        counts[t.status] = counts.get(t.status, 0) + 1
        by_difficulty[t.difficulty] = by_difficulty.get(t.difficulty, 0) + 1
        hours_total += t.estimated_hours
        bucket = per_subject.setdefault(t.subject_id, {"total": 0, "done": 0, "hours_left": 0.0})
        bucket["total"] += 1
        if t.status == "done":
            hours_done += t.estimated_hours
            bucket["done"] += 1
        else:
            bucket["hours_left"] += t.estimated_hours

    total = len(topics)
    return Stats(
        total_topics=total,
        todo=counts["todo"],
        in_progress=counts["in_progress"],
        done=counts["done"],
        completion=round(counts["done"] / total * 100, 1) if total else 0.0,
        hours_total=round(hours_total, 1),
        hours_done=round(hours_done, 1),
        hours_left=round(hours_total - hours_done, 1),
        avg_difficulty=round(sum(t.difficulty for t in topics) / total, 2) if total else 0.0,
        by_difficulty=by_difficulty,
        subjects=[
            SubjectProgress(
                id=s.id,
                name=s.name,
                color=s.color,
                total=per_subject[s.id]["total"],
                done=per_subject[s.id]["done"],
                progress=(
                    round(per_subject[s.id]["done"] / per_subject[s.id]["total"] * 100, 1)
                    if per_subject[s.id]["total"]
                    else 0.0
                ),
                hours_left=round(per_subject[s.id]["hours_left"], 1),
                exam_date=s.exam_date,
            )
            for s in subjects
        ],
    )
