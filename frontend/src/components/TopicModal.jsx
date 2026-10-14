import { useState } from "react";
import Modal from "./Modal.jsx";

export default function TopicModal({ topic, subjects, onSave, onClose }) {
  const editing = Boolean(topic.id);
  const [form, setForm] = useState({
    title: topic.title || "",
    subject_id: topic.subject_id || subjects[0]?.id || "",
    status: topic.status || "todo",
    difficulty: topic.difficulty || 3,
    estimated_hours: topic.estimated_hours || 1,
    notes: topic.notes || "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await onSave(
        {
          ...form,
          subject_id: Number(form.subject_id),
          difficulty: Number(form.difficulty),
          estimated_hours: Number(form.estimated_hours),
          notes: form.notes.trim() || null,
        },
        topic.id
      );
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  }

  return (
    <Modal title={editing ? "Edit topic" : "New topic"} onClose={onClose}>
      <form className="form" onSubmit={submit}>
        <label>
          Topic
          <input autoFocus required maxLength={200} value={form.title} onChange={set("title")} placeholder="e.g. Fourier series" />
        </label>

        <div className="row">
          <label>
            Subject
            <select value={form.subject_id} onChange={set("subject_id")}>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Status
            <select value={form.status} onChange={set("status")}>
              <option value="todo">To study</option>
              <option value="in_progress">In progress</option>
              <option value="done">Done</option>
            </select>
          </label>
        </div>

        <div className="row">
          <label>
            <span>
              Difficulty <span className="muted">({form.difficulty}/5)</span>
            </span>
            <input type="range" min="1" max="5" value={form.difficulty} onChange={set("difficulty")} />
          </label>
          <label>
            Estimated hours
            <input type="number" min="0.25" max="200" step="0.25" required value={form.estimated_hours} onChange={set("estimated_hours")} />
          </label>
        </div>

        <label>
          Notes
          <textarea rows="3" value={form.notes} onChange={set("notes")} placeholder="Chapters, past paper questions, links…" />
        </label>

        {error && <p className="form-error">{error}</p>}

        <div className="form-actions">
          <button type="button" className="btn ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn primary" disabled={saving}>
            {saving ? "Saving…" : editing ? "Save changes" : "Add topic"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
