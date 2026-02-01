import { useState, useEffect, useRef } from "react";

const PROMPTS = {
  en: "Type your message:",
  es: "Escriba su mensaje:",
  pa: "ਆਪਣਾ ਸੁਨੇਹਾ ਟਾਈਪ ਕਰੋ:",
  hi: "अपना संदेश टाइप करें:",
  fr: "Tapez votre message:",
};

export default function VoiceInputDialog({ lang, onSubmit, onClose }) {
  const [text, setText] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e) => {
    e?.preventDefault?.();
    const trimmed = text.trim();
    if (trimmed) {
      onSubmit(trimmed);
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 className="text-white font-semibold text-base mb-4 text-center">
          {PROMPTS[lang] || PROMPTS.en}
        </h3>
        <form onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="..."
            className="w-full bg-zinc-950 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-zinc-500 outline-none focus:border-indigo-500/50 transition-colors mb-4"
          />
          <div className="flex gap-2">
            <button
              type="submit"
              className="flex-1 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
            >
              Send
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-sm font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
