export default function PermissionDialog({ step, command, onRespond }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-zinc-900 border border-white/10 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 className="text-white font-semibold text-base mb-3">
          Permission Required
        </h3>
        <p className="text-zinc-300 text-sm mb-2">{step}</p>
        <div className="bg-zinc-950 rounded-lg px-3 py-2 mb-5 border border-white/5">
          <code className="text-xs text-indigo-300 break-all">{command}</code>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onRespond("yes")}
            className="flex-1 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors"
          >
            Yes
          </button>
          <button
            onClick={() => onRespond("no")}
            className="flex-1 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white text-sm font-medium transition-colors"
          >
            No
          </button>
          <button
            onClick={() => onRespond("skip")}
            className="flex-1 py-2 rounded-lg bg-zinc-700 hover:bg-zinc-600 text-zinc-300 text-sm font-medium transition-colors"
          >
            Skip
          </button>
        </div>
      </div>
    </div>
  );
}
