const STATUS_CONFIG = {
  pending: { icon: "○", color: "text-zinc-500", bg: "bg-zinc-900" },
  running: { icon: "●", color: "text-amber-400", bg: "bg-amber-950/50" },
  done: { icon: "✓", color: "text-emerald-400", bg: "bg-emerald-950/50" },
  failed: { icon: "✕", color: "text-red-400", bg: "bg-red-950/50" },
  skipped: { icon: "–", color: "text-zinc-500", bg: "bg-zinc-900" },
};

export default function StepCard({ num, total, description, status = "pending" }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  return (
    <div className="px-4 py-1">
      <div className={`flex items-center gap-3 rounded-xl px-4 py-2.5 ${cfg.bg} border border-white/5`}>
        <span className={`text-base font-bold ${cfg.color}`}>{cfg.icon}</span>
        <span className="text-[10px] text-zinc-500 font-medium">
          Step {num}/{total}
        </span>
        <span className="text-sm text-zinc-200 flex-1">{description}</span>
        {status === "running" && (
          <div className="w-3 h-3 rounded-full border-2 border-amber-400 border-t-transparent animate-spin" />
        )}
      </div>
    </div>
  );
}
