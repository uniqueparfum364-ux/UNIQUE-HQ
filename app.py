import { useState, useMemo } from "react";

const STATUSES = ["NEW", "PENDING", "SOLD", "LOST"];

const STATUS_STYLES = {
  NEW:     { bg: "#F1EFE8", color: "#5F5E5A", dot: "#B4B2A9" },
  PENDING: { bg: "#FAEEDA", color: "#854F0B", dot: "#EF9F27" },
  SOLD:    { bg: "#EAF3DE", color: "#3B6D11", dot: "#639922" },
  LOST:    { bg: "#FCEBEB", color: "#A32D2D", dot: "#E24B4A" },
};

const SAMPLE_LEADS = [
  { id: 1, submitted: "2026-03-10 09:14", status: "SOLD",    quote: 4200, contact: "Amara Osei",      email: "amara@bloom.co",     phone: "0412 555 001", eventDate: "2026-04-12", location: "Sydney", notes: "Garden wedding, 200 guests" },
  { id: 2, submitted: "2026-03-18 14:32", status: "PENDING", quote: 3100, contact: "James Thornton",  email: "jt@thornton.com",    phone: "0412 555 002", eventDate: "2026-05-03", location: "Melbourne", notes: "Corporate gala, 80 guests" },
  { id: 3, submitted: "2026-03-25 11:05", status: "NEW",     quote: 1800, contact: "Sofia Reyes",     email: "sofia@reyesco.io",   phone: "0412 555 003", eventDate: "2026-06-20", location: "Brisbane", notes: "Birthday dinner party" },
  { id: 4, submitted: "2026-04-01 08:50", status: "LOST",    quote: 5500, contact: "Daniel Park",     email: "d.park@email.com",   phone: "0412 555 004", eventDate: "2026-04-28", location: "Perth", notes: "Went with competitor" },
  { id: 5, submitted: "2026-04-02 16:20", status: "PENDING", quote: 2700, contact: "Chloe Dubois",    email: "chloe@dubois.fr",    phone: "0412 555 005", eventDate: "2026-07-14", location: "Sydney", notes: "Awaiting final headcount" },
];

const EMPTY_LEAD = { status: "NEW", quote: "", contact: "", email: "", phone: "", eventDate: "", location: "", notes: "" };

function fmt(n) { return n.toLocaleString("en-AU", { style: "currency", currency: "AUD", maximumFractionDigits: 0 }); }
function initials(name) { return name.split(" ").map(w => w[0]).join("").slice(0,2).toUpperCase(); }
function avatarColor(name) {
  const colors = ["#9FE1CB","#FAC775","#F4C0D1","#B5D4F4","#C0DD97","#F5C4B3"];
  let h = 0; for (let c of name) h = (h * 31 + c.charCodeAt(0)) % colors.length;
  return colors[h];
}

export default function CRM() {
  const [leads, setLeads] = useState(SAMPLE_LEADS);
  const [view, setView] = useState("list");
  const [selected, setSelected] = useState(null);
  const [filterStatus, setFilterStatus] = useState("ALL");
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(null);
  const [sortBy, setSortBy] = useState("submitted");

  const metrics = useMemo(() => {
    const active = leads.filter(l => l.status !== "LOST");
    const sold = leads.filter(l => l.status === "SOLD");
    return {
      active: active.length,
      pipeline: active.reduce((s, l) => s + (+l.quote || 0), 0),
      sold: sold.reduce((s, l) => s + (+l.quote || 0), 0),
      lost: leads.filter(l => l.status === "LOST").length,
    };
  }, [leads]);

  const filtered = useMemo(() => leads
    .filter(l => filterStatus === "ALL" || l.status === filterStatus)
    .filter(l => !search || [l.contact, l.email, l.location, l.notes].join(" ").toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === "quote") return (+b.quote||0) - (+a.quote||0);
      if (sortBy === "event") return (a.eventDate||"").localeCompare(b.eventDate||"");
      return b.submitted.localeCompare(a.submitted);
    }), [leads, filterStatus, search, sortBy]);

  function openNew() { setForm({ ...EMPTY_LEAD, _new: true }); setView("form"); }
  function openEdit(lead) { setForm({ ...lead }); setView("form"); }
  function openDetail(lead) { setSelected(lead); setView("detail"); }

  function saveForm() {
    if (!form.contact) return;
    if (form._new) {
      const newLead = { ...form, id: Date.now(), submitted: new Date().toISOString().slice(0,16).replace("T"," "), _new: undefined };
      setLeads(prev => [newLead, ...prev]);
    } else {
      setLeads(prev => prev.map(l => l.id === form.id ? { ...form, _new: undefined } : l));
    }
    setView("list"); setForm(null);
  }

  function deleteSelected() {
    setLeads(prev => prev.filter(l => l.id !== selected.id));
    setView("list"); setSelected(null);
  }

  function updateStatus(id, status) {
    setLeads(prev => prev.map(l => l.id === id ? { ...l, status } : l));
    if (selected?.id === id) setSelected(prev => ({ ...prev, status }));
  }

  const ss = STATUS_STYLES;

  return (
    <div style={{ fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif", background: "var(--color-background-tertiary)", minHeight: "100vh", padding: "0" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* TOP NAV */}
      <div style={{ background: "var(--color-background-primary)", borderBottom: "0.5px solid var(--color-border-tertiary)", padding: "0 28px", display: "flex", alignItems: "center", height: 52, gap: 16 }}>
        <span style={{ fontSize: 18, letterSpacing: "-0.5px", fontWeight: 600, color: "var(--color-text-primary)" }}>Unique Parfum</span>
        <span style={{ fontSize: 11, color: "var(--color-text-tertiary)", background: "var(--color-background-secondary)", padding: "2px 8px", borderRadius: 4, fontFamily: "var(--font-mono)" }}>CRM</span>
        <div style={{ flex: 1 }} />
        <button onClick={openNew} style={{ background: "var(--color-text-primary)", color: "var(--color-background-primary)", border: "none", borderRadius: 6, padding: "6px 16px", fontSize: 13, fontWeight: 500, cursor: "pointer", fontFamily: "inherit" }}>
          + New Lead
        </button>
      </div>

      <div style={{ padding: "24px 28px", maxWidth: 1100, margin: "0 auto" }}>

        {/* METRICS ROW */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
          {[
            { label: "Active Leads", value: metrics.active, mono: true },
            { label: "Pipeline", value: fmt(metrics.pipeline) },
            { label: "Closed Won", value: fmt(metrics.sold), green: true },
            { label: "Lost Deals", value: metrics.lost, mono: true, red: true },
          ].map(m => (
            <div key={m.label} style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 10, padding: "14px 18px" }}>
              <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 6, letterSpacing: "0.04em", textTransform: "uppercase" }}>{m.label}</div>
              <div style={{ fontSize: 22, fontWeight: 500, color: m.green ? "#3B6D11" : m.red ? "#A32D2D" : "var(--color-text-primary)", fontFamily: m.mono ? "var(--font-mono)" : "inherit" }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* LIST VIEW */}
        {view === "list" && (
          <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 12 }}>
            {/* Toolbar */}
            <div style={{ padding: "14px 18px", display: "flex", gap: 10, alignItems: "center", borderBottom: "0.5px solid var(--color-border-tertiary)", flexWrap: "wrap" }}>
              <input
                value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search leads…"
                style={{ flex: 1, minWidth: 160, background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 6, padding: "7px 12px", fontSize: 13, color: "var(--color-text-primary)", outline: "none", fontFamily: "inherit" }}
              />
              <div style={{ display: "flex", gap: 4 }}>
                {["ALL", ...STATUSES].map(s => (
                  <button key={s} onClick={() => setFilterStatus(s)} style={{ fontSize: 12, padding: "5px 11px", borderRadius: 5, border: "0.5px solid", cursor: "pointer", fontFamily: "inherit", fontWeight: filterStatus === s ? 500 : 400,
                    background: filterStatus === s ? "var(--color-text-primary)" : "transparent",
                    color: filterStatus === s ? "var(--color-background-primary)" : "var(--color-text-secondary)",
                    borderColor: filterStatus === s ? "var(--color-text-primary)" : "var(--color-border-tertiary)"
                  }}>{s}</button>
                ))}
              </div>
              <select value={sortBy} onChange={e => setSortBy(e.target.value)} style={{ fontSize: 12, background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 6, padding: "6px 10px", color: "var(--color-text-secondary)", fontFamily: "inherit" }}>
                <option value="submitted">Sort: Recent</option>
                <option value="quote">Sort: Quote</option>
                <option value="event">Sort: Event Date</option>
              </select>
            </div>

            {/* Table Header */}
            <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1.5fr 1fr", padding: "9px 18px", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
              {["Contact", "Status", "Quote", "Event / Location", "Submitted"].map(h => (
                <div key={h} style={{ fontSize: 11, color: "var(--color-text-tertiary)", letterSpacing: "0.05em", textTransform: "uppercase", fontWeight: 500 }}>{h}</div>
              ))}
            </div>

            {/* Rows */}
            {filtered.length === 0 && (
              <div style={{ padding: "32px 18px", textAlign: "center", color: "var(--color-text-tertiary)", fontSize: 13 }}>No leads match your filters.</div>
            )}
            {filtered.map((lead, i) => {
              const st = ss[lead.status] || ss.NEW;
              return (
                <div key={lead.id} onClick={() => openDetail(lead)}
                  style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1.5fr 1fr", padding: "12px 18px", borderBottom: i < filtered.length - 1 ? "0.5px solid var(--color-border-tertiary)" : "none", cursor: "pointer", transition: "background 0.1s" }}
                  onMouseEnter={e => e.currentTarget.style.background = "var(--color-background-secondary)"}
                  onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ width: 30, height: 30, borderRadius: "50%", background: avatarColor(lead.contact || "?"), display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600, color: "#444441", flexShrink: 0 }}>
                      {initials(lead.contact || "?")}
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)" }}>{lead.contact}</div>
                      <div style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>{lead.email}</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center" }}>
                    <span style={{ background: st.bg, color: st.color, fontSize: 11, fontWeight: 500, padding: "3px 9px", borderRadius: 4, display: "flex", alignItems: "center", gap: 5 }}>
                      <span style={{ width: 5, height: 5, borderRadius: "50%", background: st.dot, display: "inline-block" }} />
                      {lead.status}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)", fontFamily: "var(--font-mono)" }}>
                    {lead.quote ? fmt(+lead.quote) : "—"}
                  </div>
                  <div style={{ display: "flex", alignItems: "center" }}>
                    <div>
                      <div style={{ fontSize: 13, color: "var(--color-text-primary)" }}>{lead.eventDate || "—"}</div>
                      <div style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>{lead.location}</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", fontSize: 11, color: "var(--color-text-tertiary)" }}>
                    {lead.submitted?.slice(0, 10)}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* DETAIL VIEW */}
        {view === "detail" && selected && (() => {
          const st = ss[selected.status] || ss.NEW;
          return (
            <div>
              <button onClick={() => setView("list")} style={{ fontSize: 13, color: "var(--color-text-secondary)", background: "none", border: "none", cursor: "pointer", padding: "0 0 16px", fontFamily: "inherit" }}>← All Leads</button>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 16 }}>
                {/* Left panel */}
                <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 12, padding: "24px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 24 }}>
                    <div style={{ width: 48, height: 48, borderRadius: "50%", background: avatarColor(selected.contact || "?"), display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 600, color: "#444441" }}>
                      {initials(selected.contact || "?")}
                    </div>
                    <div>
                      <div style={{ fontSize: 18, fontWeight: 500, color: "var(--color-text-primary)" }}>{selected.contact}</div>
                      <div style={{ fontSize: 13, color: "var(--color-text-tertiary)" }}>{selected.email}</div>
                    </div>
                    <div style={{ flex: 1 }} />
                    <button onClick={() => openEdit(selected)} style={{ fontSize: 13, padding: "7px 16px", border: "0.5px solid var(--color-border-secondary)", borderRadius: 6, background: "transparent", cursor: "pointer", color: "var(--color-text-primary)", fontFamily: "inherit" }}>Edit</button>
                    <button onClick={deleteSelected} style={{ fontSize: 13, padding: "7px 16px", border: "0.5px solid #F09595", borderRadius: 6, background: "transparent", cursor: "pointer", color: "#A32D2D", fontFamily: "inherit" }}>Delete</button>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                    {[
                      { label: "Phone", value: selected.phone },
                      { label: "Location", value: selected.location },
                      { label: "Event Date", value: selected.eventDate },
                      { label: "Quote", value: selected.quote ? fmt(+selected.quote) : "—" },
                      { label: "Submitted", value: selected.submitted },
                    ].map(f => (
                      <div key={f.label}>
                        <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 3, textTransform: "uppercase", letterSpacing: "0.04em" }}>{f.label}</div>
                        <div style={{ fontSize: 14, color: "var(--color-text-primary)", fontWeight: 400 }}>{f.value || "—"}</div>
                      </div>
                    ))}
                  </div>

                  {selected.notes && (
                    <div style={{ marginTop: 20, paddingTop: 20, borderTop: "0.5px solid var(--color-border-tertiary)" }}>
                      <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.04em" }}>Notes</div>
                      <div style={{ fontSize: 14, color: "var(--color-text-secondary)", lineHeight: 1.6 }}>{selected.notes}</div>
                    </div>
                  )}
                </div>

                {/* Right panel - status */}
                <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 12, padding: "24px" }}>
                  <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.04em" }}>Pipeline Stage</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {STATUSES.map(s => {
                      const active = selected.status === s;
                      const sst = ss[s];
                      return (
                        <button key={s} onClick={() => updateStatus(selected.id, s)} style={{
                          display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 8,
                          border: active ? `1.5px solid ${sst.dot}` : "0.5px solid var(--color-border-tertiary)",
                          background: active ? sst.bg : "transparent",
                          cursor: "pointer", fontFamily: "inherit", textAlign: "left", transition: "all 0.1s"
                        }}>
                          <span style={{ width: 8, height: 8, borderRadius: "50%", background: sst.dot, display: "inline-block" }} />
                          <span style={{ fontSize: 13, fontWeight: active ? 500 : 400, color: active ? sst.color : "var(--color-text-secondary)" }}>{s}</span>
                          {active && <span style={{ marginLeft: "auto", fontSize: 11, color: sst.color }}>current</span>}
                        </button>
                      );
                    })}
                  </div>

                  <div style={{ marginTop: 24, paddingTop: 20, borderTop: "0.5px solid var(--color-border-tertiary)" }}>
                    <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.04em" }}>Deal Value</div>
                    <div style={{ fontSize: 28, fontWeight: 500, color: "var(--color-text-primary)", fontFamily: "var(--font-mono)" }}>{selected.quote ? fmt(+selected.quote) : "—"}</div>
                  </div>
                </div>
              </div>
            </div>
          );
        })()}

        {/* FORM VIEW */}
        {view === "form" && form && (
          <div>
            <button onClick={() => { setView(form._new ? "list" : "detail"); setForm(null); }} style={{ fontSize: 13, color: "var(--color-text-secondary)", background: "none", border: "none", cursor: "pointer", padding: "0 0 16px", fontFamily: "inherit" }}>
              ← {form._new ? "All Leads" : "Back"}
            </button>
            <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 12, padding: "28px", maxWidth: 640 }}>
              <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 24, color: "var(--color-text-primary)" }}>{form._new ? "New Lead" : "Edit Lead"}</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                {[
                  { key: "contact", label: "Contact Name", span: 2 },
                  { key: "email", label: "Email" },
                  { key: "phone", label: "Phone" },
                  { key: "location", label: "Location" },
                  { key: "eventDate", label: "Event Date", type: "date" },
                  { key: "quote", label: "Quote (AUD)", type: "number" },
                ].map(f => (
                  <div key={f.key} style={{ gridColumn: f.span === 2 ? "1/-1" : undefined }}>
                    <label style={{ display: "block", fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.04em" }}>{f.label}</label>
                    <input
                      type={f.type || "text"} value={form[f.key] || ""}
                      onChange={e => setForm(prev => ({ ...prev, [f.key]: e.target.value }))}
                      style={{ width: "100%", boxSizing: "border-box", background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 6, padding: "8px 12px", fontSize: 13, color: "var(--color-text-primary)", fontFamily: "inherit", outline: "none" }}
                    />
                  </div>
                ))}
                <div>
                  <label style={{ display: "block", fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.04em" }}>Status</label>
                  <select value={form.status} onChange={e => setForm(prev => ({ ...prev, status: e.target.value }))}
                    style={{ width: "100%", background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 6, padding: "8px 12px", fontSize: 13, color: "var(--color-text-primary)", fontFamily: "inherit" }}>
                    {STATUSES.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div style={{ gridColumn: "1/-1" }}>
                  <label style={{ display: "block", fontSize: 11, color: "var(--color-text-tertiary)", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.04em" }}>Notes</label>
                  <textarea value={form.notes || ""} onChange={e => setForm(prev => ({ ...prev, notes: e.target.value }))} rows={3}
                    style={{ width: "100%", boxSizing: "border-box", background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: 6, padding: "8px 12px", fontSize: 13, color: "var(--color-text-primary)", fontFamily: "inherit", resize: "vertical", outline: "none" }} />
                </div>
              </div>
              <div style={{ marginTop: 20, display: "flex", gap: 8, justifyContent: "flex-end" }}>
                <button onClick={() => { setView(form._new ? "list" : "detail"); setForm(null); }}
                  style={{ padding: "8px 18px", borderRadius: 6, border: "0.5px solid var(--color-border-secondary)", background: "transparent", color: "var(--color-text-secondary)", cursor: "pointer", fontFamily: "inherit", fontSize: 13 }}>
                  Cancel
                </button>
                <button onClick={saveForm}
                  style={{ padding: "8px 18px", borderRadius: 6, border: "none", background: "var(--color-text-primary)", color: "var(--color-background-primary)", cursor: "pointer", fontFamily: "inherit", fontSize: 13, fontWeight: 500 }}>
                  {form._new ? "Create Lead" : "Save Changes"}
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
