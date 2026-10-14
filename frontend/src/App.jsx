import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import Sidebar from "./components/Sidebar.jsx";
import StatCards from "./components/StatCards.jsx";
import SubjectProgress from "./components/SubjectProgress.jsx";
import TopicTable from "./components/TopicTable.jsx";
import TopicModal from "./components/TopicModal.jsx";
import SubjectModal from "./components/SubjectModal.jsx";

const STATUS_FILTERS = [
  { value: "", label: "All" },
  { value: "todo", label: "To study" },
  { value: "in_progress", label: "In progress" },
  { value: "done", label: "Done" },
];

export default function App() {
  const [subjects, setSubjects] = useState([]);
  const [stats, setStats] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [topicModal, setTopicModal] = useState(null);
  const [subjectModal, setSubjectModal] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setQuery(search.trim()), 250);
    return () => clearTimeout(t);
  }, [search]);

  const refresh = useCallback(async () => {
    try {
      const [s, st, t] = await Promise.all([
        api.subjects(),
        api.stats(),
        api.topics({ subject_id: subjectId, status, search: query }),
      ]);
      setSubjects(s);
      setStats(st);
      setTopics(t);
      setError("");
    } catch (err) {
      setError(err.message || "Could not reach the API");
    } finally {
      setLoading(false);
    }
  }, [subjectId, status, query]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const selectedSubject = subjects.find((s) => String(s.id) === String(subjectId));

  async function saveTopic(data, id) {
    if (id) await api.updateTopic(id, data);
    else await api.createTopic(data);
    setTopicModal(null);
    refresh();
  }

  async function saveSubject(data, id) {
    if (id) await api.updateSubject(id, data);
    else await api.createSubject(data);
    setSubjectModal(null);
    refresh();
  }

  async function removeSubject(subject) {
    if (!confirm(`Delete "${subject.name}" and all of its topics?`)) return;
    await api.deleteSubject(subject.id);
    setSubjectModal(null);
    if (String(subjectId) === String(subject.id)) setSubjectId("");
    refresh();
  }

  async function changeStatus(topic, next) {
    setTopics((prev) => prev.map((t) => (t.id === topic.id ? { ...t, status: next } : t)));
    try {
      await api.updateTopic(topic.id, { status: next });
    } finally {
      refresh();
    }
  }

  async function removeTopic(topic) {
    if (!confirm(`Delete "${topic.title}"?`)) return;
    await api.deleteTopic(topic.id);
    refresh();
  }

  return (
    <div className={`layout ${menuOpen ? "menu-open" : ""}`}>
      <Sidebar
        subjects={subjects}
        selected={subjectId}
        onSelect={(id) => {
          setSubjectId(id);
          setMenuOpen(false);
        }}
        onAddSubject={() => setSubjectModal({})}
        onEditSubject={(s) => setSubjectModal(s)}
        onClose={() => setMenuOpen(false)}
      />

      <main className="main">
        <header className="topbar">
          <button className="icon-btn menu-btn" onClick={() => setMenuOpen(true)} aria-label="Open menu">
            <span />
            <span />
            <span />
          </button>
          <div>
            <p className="eyebrow">{selectedSubject ? selectedSubject.code || "Subject" : "Overview"}</p>
            <h1>{selectedSubject ? selectedSubject.name : "My syllabus"}</h1>
          </div>
          <button
            className="btn primary"
            disabled={!subjects.length}
            title={subjects.length ? "" : "Add a subject first"}
            onClick={() => setTopicModal({ subject_id: subjectId || subjects[0]?.id })}
          >
            + Add topic
          </button>
        </header>

        {error && (
          <div className="banner error">
            <strong>Backend unavailable.</strong> {error}
            <button className="btn ghost small" onClick={refresh}>
              Retry
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading">
            <div className="spinner" />
            Loading your syllabus…
          </div>
        ) : (
          <>
            <StatCards stats={stats} />

            {stats?.subjects?.length > 0 && !subjectId && (
              <SubjectProgress subjects={stats.subjects} onSelect={(id) => setSubjectId(String(id))} />
            )}

            <section className="panel">
              <div className="panel-head">
                <div className="tabs" role="tablist">
                  {STATUS_FILTERS.map((f) => (
                    <button
                      key={f.value}
                      role="tab"
                      aria-selected={status === f.value}
                      className={`tab ${status === f.value ? "active" : ""}`}
                      onClick={() => setStatus(f.value)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
                <input
                  className="search"
                  type="search"
                  placeholder="Search topics…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

              <TopicTable
                topics={topics}
                subjects={subjects}
                emptyHint={
                  subjects.length
                    ? "No topics here yet. Add one to start tracking."
                    : "Start by adding a subject from the sidebar."
                }
                onStatusChange={changeStatus}
                onEdit={(t) => setTopicModal(t)}
                onDelete={removeTopic}
              />
            </section>
          </>
        )}
      </main>

      {topicModal && (
        <TopicModal
          topic={topicModal}
          subjects={subjects}
          onSave={saveTopic}
          onClose={() => setTopicModal(null)}
        />
      )}

      {subjectModal && (
        <SubjectModal
          subject={subjectModal}
          onSave={saveSubject}
          onDelete={removeSubject}
          onClose={() => setSubjectModal(null)}
        />
      )}
    </div>
  );
}
