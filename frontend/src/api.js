const BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join(", ");
    } catch {}
    throw new Error(message);
  }

  return res.status === 204 ? null : res.json();
}

export const api = {
  stats: () => request("/api/stats"),

  subjects: () => request("/api/subjects"),
  createSubject: (data) => request("/api/subjects", { method: "POST", body: JSON.stringify(data) }),
  updateSubject: (id, data) => request(`/api/subjects/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteSubject: (id) => request(`/api/subjects/${id}`, { method: "DELETE" }),

  topics: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null));
    return request(`/api/topics${qs.toString() ? `?${qs}` : ""}`);
  },
  createTopic: (data) => request("/api/topics", { method: "POST", body: JSON.stringify(data) }),
  updateTopic: (id, data) => request(`/api/topics/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteTopic: (id) => request(`/api/topics/${id}`, { method: "DELETE" }),
};
