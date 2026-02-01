const COLOR_MAP = {
  ready: { dot: "bg-emerald-400", text: "text-emerald-400", bg: "bg-emerald-950/50" },
  processing: { dot: "bg-violet-400", text: "text-violet-400", bg: "bg-violet-950/50" },
  listening: { dot: "bg-indigo-400", text: "text-indigo-400", bg: "bg-indigo-950/50" },
  diagnosing: { dot: "bg-amber-400", text: "text-amber-400", bg: "bg-amber-950/50" },
  error: { dot: "bg-red-400", text: "text-red-400", bg: "bg-red-950/50" },
};

export default function StatusBadge({ status = "ready", label }) {
  const cfg = COLOR_MAP[status] || COLOR_MAP.ready;
  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium ${cfg.bg} ${cfg.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {label || status.charAt(0).toUpperCase() + status.slice(1)}
    </div>
  );
}
