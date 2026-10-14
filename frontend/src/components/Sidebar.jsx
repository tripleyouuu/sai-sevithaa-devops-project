export default function Sidebar({ subjects, selected, onSelect, onAddSubject, onEditSubject, onClose }) {
  return (
    <>
      <div className="scrim" onClick={onClose} />
      <aside className="sidebar">
        <div className="brand">
          <img src="/favicon.svg" alt="" width="28" height="28" />
          <span>Syllabus</span>
        </div>

        <nav>
          <button className={`nav-item ${selected === "" ? "active" : ""}`} onClick={() => onSelect("")}>
            <span className="nav-icon">◎</span>
            Overview
          </button>
        </nav>

        <div className="nav-section">
          <span>Subjects</span>
          <button className="icon-btn add" onClick={onAddSubject} aria-label="Add subject">
            +
          </button>
        </div>

        <nav className="subject-list">
          {subjects.length === 0 && <p className="muted small pad">No subjects yet</p>}
          {subjects.map((s) => (
            <div key={s.id} className={`nav-item subject ${String(selected) === String(s.id) ? "active" : ""}`}>
              <button className="subject-link" onClick={() => onSelect(String(s.id))}>
                <span className="dot" style={{ background: s.color }} />
                <span className="truncate">{s.name}</span>
                <span className="count">{Math.round(s.progress)}%</span>
              </button>
              <button className="icon-btn edit" onClick={() => onEditSubject(s)} aria-label={`Edit ${s.name}`}>
                ⋯
              </button>
            </div>
          ))}
        </nav>

        <div className="sidebar-foot">
          <a href="/docs" target="_blank" rel="noreferrer">
            API docs
          </a>
        </div>
      </aside>
    </>
  );
}
