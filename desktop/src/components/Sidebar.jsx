import { LANGS } from "../lib/tokens";

export default function Sidebar({
  sessions,
  activeId,
  lang,
  onSelectSession,
  onNewSession,
  onChangeLang,
}) {
  const today = new Date().toISOString().slice(0, 10);

  let lastGroup = null;
  const items = sessions.map((s) => {
    const created = (s.created || "").slice(0, 10);
    const group = created === today ? "Today" : "Earlier";
    const showGroup = group !== lastGroup;
    lastGroup = group;
    return { ...s, group, showGroup };
  });

  return (
    <div className="w-56 flex-shrink-0 flex flex-col bg-[#0F0F12] border-r border-white/5 h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 h-12 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xs">
            F
          </div>
          <span className="text-white font-semibold text-base tracking-tight">
            FixMe
          </span>
        </div>
        <button
          onClick={onNewSession}
          className="w-7 h-7 rounded-lg bg-[#1C1C21] hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors text-lg"
        >
          +
        </button>
      </div>

      <div className="h-px bg-white/5" />

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {items.map((s) => (
          <div key={s.id}>
            {s.showGroup && (
              <div className="px-2 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
                {s.group}
              </div>
            )}
            <button
              onClick={() => onSelectSession(s.id)}
              className={`w-full text-left px-3 py-1.5 rounded-lg text-sm truncate transition-colors ${
                s.id === activeId
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:bg-[#1C1C21] hover:text-zinc-300"
              }`}
            >
              {(s.title || "Untitled").slice(0, 30)}
            </button>
          </div>
        ))}
      </div>

      <div className="h-px bg-white/5" />

      {/* Language selector */}
      <div className="flex gap-1 px-3 py-2.5 flex-shrink-0">
        {LANGS.map((l) => (
          <button
            key={l.code}
            onClick={() => onChangeLang(l.code)}
            className={`flex-1 py-1 rounded text-xs font-semibold transition-colors ${
              lang === l.code
                ? "bg-indigo-600 text-white"
                : "bg-[#1C1C21] text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>
    </div>
  );
}
