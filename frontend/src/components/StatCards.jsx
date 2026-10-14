export default function StatCards({ stats }) {
  if (!stats) return null;

  const hard = (stats.by_difficulty?.["4"] || 0) + (stats.by_difficulty?.["5"] || 0);

  const cards = [
    {
      label: "Syllabus covered",
      value: `${stats.completion}%`,
      sub: `${stats.done} of ${stats.total_topics} topics done`,
      ring: stats.completion,
    },
    {
      label: "In progress",
      value: stats.in_progress,
      sub: `${stats.todo} still to study`,
    },
    {
      label: "Hours remaining",
      value: stats.hours_left,
      sub: `${stats.hours_done}h of ${stats.hours_total}h studied`,
    },
    {
      label: "Average difficulty",
      value: stats.avg_difficulty ? stats.avg_difficulty.toFixed(1) : "–",
      sub: `${hard} rated 4 or 5`,
    },
  ];

  return (
    <section className="stats">
      {cards.map((c) => (
        <div className="card stat" key={c.label}>
          <div>
            <p className="stat-label">{c.label}</p>
            <p className="stat-value">{c.value}</p>
            <p className="stat-sub">{c.sub}</p>
          </div>
          {c.ring !== undefined && <Ring value={c.ring} />}
        </div>
      ))}
    </section>
  );
}

function Ring({ value }) {
  const r = 22;
  const circ = 2 * Math.PI * r;
  return (
    <svg className="ring" width="56" height="56" viewBox="0 0 56 56" aria-hidden="true">
      <circle cx="28" cy="28" r={r} className="ring-track" />
      <circle
        cx="28"
        cy="28"
        r={r}
        className="ring-fill"
        strokeDasharray={circ}
        strokeDashoffset={circ - (circ * value) / 100}
      />
    </svg>
  );
}
