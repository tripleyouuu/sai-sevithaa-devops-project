function daysUntil(dateStr) {
  if (!dateStr) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.round((new Date(dateStr + "T00:00:00") - today) / 86400000);
}

function examLabel(days) {
  if (days === null) return null;
  if (days < 0) return "Exam passed";
  if (days === 0) return "Exam today";
  if (days === 1) return "Exam tomorrow";
  return `Exam in ${days} days`;
}

export default function SubjectProgress({ subjects, onSelect }) {
  return (
    <section className="subject-grid">
      {subjects.map((s) => {
        const days = daysUntil(s.exam_date);
        const urgent = days !== null && days >= 0 && days <= 14 && s.progress < 80;
        return (
          <button key={s.id} className="card subject-card" onClick={() => onSelect(s.id)}>
            <div className="subject-card-head">
              <span className="dot" style={{ background: s.color }} />
              <span className="truncate">{s.name}</span>
              <span className="pct">{Math.round(s.progress)}%</span>
            </div>
            <div className="bar">
              <div className="bar-fill" style={{ width: `${s.progress}%`, background: s.color }} />
            </div>
            <div className="subject-card-foot">
              <span>
                {s.done}/{s.total} topics · {s.hours_left}h left
              </span>
              {days !== null && <span className={`exam ${urgent ? "urgent" : ""}`}>{examLabel(days)}</span>}
            </div>
          </button>
        );
      })}
    </section>
  );
}
