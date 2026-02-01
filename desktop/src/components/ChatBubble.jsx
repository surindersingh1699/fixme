export default function ChatBubble({ text, role, time }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} px-4 py-1`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${
          isUser
            ? "bg-indigo-600 text-white"
            : "bg-zinc-900 text-zinc-100 border border-white/5"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap leading-relaxed">{text}</p>
        {time && (
          <p
            className={`text-[10px] mt-1 ${
              isUser ? "text-indigo-200" : "text-zinc-500"
            }`}
          >
            {new Date(time).toLocaleTimeString([], {
              hour: "numeric",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
