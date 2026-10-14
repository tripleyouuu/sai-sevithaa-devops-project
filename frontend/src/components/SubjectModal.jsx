import { useState } from "react";
import Modal from "./Modal.jsx";

const PALETTE = ["#6366f1", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#8b5cf6", "#14b8a6"];

export default function SubjectModal({ subject, onSave, onDelete, onClose }) {
  const editing = Boolean(subject.id);
  const [form, setForm] = useState({
    name: subject.name || "",
    code: subject.code || "",
    color: subject.color || PALETTE[0],
    exam_date: subject.exam_date || "",
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
          name: form.name.trim(),
          code: form.code.trim() || null,
          color: form.color,
          exam_date: form.exam_date || null,
        },
        subject.id
      );
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  }

  return (
    <Modal title={editing ? "Edit subject" : "New subject"} onClose={onClose}>
      <form className="form" onSubmit={submit}>
        <div className="row">
          <label className="grow">
            Name
            <input autoFocus required maxLength={120} value={form.name} onChange={set("name")} placeholder="e.g. Signals and Systems" />
          </label>
          <label className="narrow">
            Code
            <input maxLength={20} value={form.code} onChange={set("code")} placeholder="EC204" />
          </label>
        </div>

        <label>
          Exam date
          <input type="date" value={form.exam_date} onChange={set("exam_date")} />
        </label>

        <fieldset className="swatches">
          <legend>Colour</legend>
          {PALETTE.map((c) => (
            <button
              type="button"
              key={c}
              className={`swatch ${form.color === c ? "picked" : ""}`}
              style={{ background: c }}
              onClick={() => setForm({ ...form, color: c })}
              aria-label={c}
            />
          ))}
        </fieldset>

        {error && <p className="form-error">{error}</p>}

        <div className="form-actions">
          {editing && (
            <button type="button" className="btn danger-ghost" onClick={() => onDelete(subject)}>
              Delete subject
            </button>
          )}
          <span className="spacer" />
          <button type="button" className="btn ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn primary" disabled={saving}>
            {saving ? "Saving…" : editing ? "Save" : "Add subject"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
