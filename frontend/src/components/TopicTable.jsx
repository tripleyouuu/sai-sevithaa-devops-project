const STATUS_LABEL = { todo: "To study", in_progress: "In progress", done: "Done" };
const NEXT_STATUS = { todo: "in_progress", in_progress: "done", done: "todo" };

function Difficulty({ level }) {
  return (
    <span className="difficulty" title={`Difficulty ${level}/5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={`pip ${n <= level ? `on d${level}` : ""}`} />
      ))}
    </span>
  );
}

export default function TopicTable({ topics, subjects, emptyHint, onStatusChange, onEdit, onDelete }) {
  const subjectById = Object.fromEntries(subjects.map((s) => [s.id, s]));

  if (!topics.length) {
    return <div className="empty">{emptyHint}</div>;
  }

  return (
    <div className="table-wrap">
      <table className="topics">
        <thead>
          <tr>
            <th>Topic</th>
            <th>Subject</th>
            <th>Status</th>
            <th>Difficulty</th>
            <th className="num">Hours</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {topics.map((t) => {
            const subject = subjectById[t.subject_id];
            return (
              <tr key={t.id} className={t.status === "done" ? "is-done" : ""}>
                <td data-label="Topic">
                  <button className="link title" onClick={() => onEdit(t)}>
                    {t.title}
                  </button>
                  {t.notes && <p className="notes">{t.notes}</p>}
                </td>
                <td data-label="Subject">
                  {subject && (
                    <span className="subject-tag">
                      <span className="dot" style={{ background: subject.color }} />
                      {subject.code || subject.name}
                    </span>
                  )}
                </td>
                <td data-label="Status">
                  <button
                    className={`status ${t.status}`}
                    onClick={() => onStatusChange(t, NEXT_STATUS[t.status])}
                    title="Click to move to the next stage"
                  >
                    {STATUS_LABEL[t.status]}
                  </button>
                </td>
                <td data-label="Difficulty">
                  <Difficulty level={t.difficulty} />
                </td>
                <td data-label="Hours" className="num">
                  {t.estimated_hours}h
                </td>
                <td className="row-actions">
                  <button className="icon-btn" onClick={() => onEdit(t)} aria-label="Edit topic">
                    ✎
                  </button>
                  <button className="icon-btn danger" onClick={() => onDelete(t)} aria-label="Delete topic">
                    ✕
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
