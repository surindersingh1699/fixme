import { useRef, useEffect } from "react";
import ChatBubble from "./ChatBubble";
import StepCard from "./StepCard";

export default function ChatArea({ items }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [items]);

  return (
    <div className="flex-1 overflow-y-auto py-4">
      {items.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full opacity-40">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 flex items-center justify-center mb-4">
            <span className="text-2xl">🔧</span>
          </div>
          <p className="text-zinc-500 text-sm">Start a conversation or diagnose your screen</p>
        </div>
      )}
      {items.map((item, i) => {
        if (item.type === "step") {
          return (
            <StepCard
              key={i}
              num={item.num}
              total={item.total}
              description={item.description}
              status={item.status}
            />
          );
        }
        return (
          <ChatBubble
            key={i}
            text={item.text}
            role={item.role}
            time={item.time}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
