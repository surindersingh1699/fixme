import { useState } from "react";

export default function InputBar({
  onSend,
  onDiagnose,
  onScreenshot,
  disabled,
}) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e?.preventDefault?.();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <div className="border-t border-white/5 bg-zinc-900/50 px-4 py-3">
      <form onSubmit={handleSubmit} className="flex gap-2 mb-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Describe your issue..."
          disabled={disabled}
          className="flex-1 bg-zinc-950 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-zinc-500 outline-none focus:border-indigo-500/50 transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !text.trim()}
          className="w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white flex items-center justify-center transition-colors"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="12" y1="19" x2="12" y2="5" />
            <polyline points="5 12 12 5 19 12" />
          </svg>
        </button>
      </form>
      <div className="flex gap-2">
        <button
          onClick={onDiagnose}
          disabled={disabled}
          className="flex-1 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-sm font-medium transition-colors"
        >
          Diagnose Screen
        </button>
        <button
          onClick={onScreenshot}
          disabled={disabled}
          className="flex-1 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 disabled:opacity-40 text-zinc-400 text-sm font-medium transition-colors"
        >
          Screenshot
        </button>
      </div>
    </div>
  );
}
