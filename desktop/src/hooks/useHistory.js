import { useState, useEffect, useCallback } from "react";

const HISTORY_KEY = "fixme_history";

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(sessions) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(sessions));
  } catch {
    // quota exceeded or other error
  }
}

export function useHistory() {
  const [sessions, setSessions] = useState(loadHistory);

  useEffect(() => {
    saveHistory(sessions);
  }, [sessions]);

  const newSession = useCallback(() => {
    const s = {
      id: Date.now().toString(),
      title: "New conversation",
      created: new Date().toISOString(),
      messages: [],
    };
    setSessions((prev) => [s, ...prev]);
    return s;
  }, []);

  const addMessage = useCallback((sessionId, role, text) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== sessionId) return s;
        const messages = [
          ...s.messages,
          { role, text, time: new Date().toISOString() },
        ];
        const title =
          role === "user" && s.title === "New conversation"
            ? text.slice(0, 50) + (text.length > 50 ? "..." : "")
            : s.title;
        return { ...s, messages, title };
      })
    );
  }, []);

  const getSession = useCallback(
    (id) => sessions.find((s) => s.id === id) || null,
    [sessions]
  );

  return { sessions, newSession, addMessage, getSession };
}
