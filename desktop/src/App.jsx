import { useState, useCallback, useRef, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import VoiceOrb from "./components/VoiceOrb";
import InputBar from "./components/InputBar";
import StatusBadge from "./components/StatusBadge";
import PermissionDialog from "./components/PermissionDialog";
import VoiceInputDialog from "./components/VoiceInputDialog";
import { useSidecar } from "./hooks/useSidecar";
import { useHistory } from "./hooks/useHistory";
import { useSpeechRecognition } from "./hooks/useSpeechRecognition";

const WELCOME_MSG =
  "Hey! I'm FixMe, your AI IT assistant.\n\n" +
  "Tell me what's wrong \u2014 in any language.\n" +
  "I'll diagnose it, walk you through each fix step by step, " +
  "and ask your permission before doing anything.";

export default function App() {
  const { call } = useSidecar();
  const { sessions, newSession, addMessage, getSession } = useHistory();
  const { isListening, transcript, startListening, stopListening } =
    useSpeechRecognition();

  const [activeSessionId, setActiveSessionId] = useState(null);
  const [lang, setLang] = useState("en");
  const [chatItems, setChatItems] = useState([]);
  const [status, setStatus] = useState("ready");
  const [statusLabel, setStatusLabel] = useState("Ready");
  const [busy, setBusy] = useState(false);
  const [orbState, setOrbState] = useState("idle");
  const [permDialog, setPermDialog] = useState(null);
  const [showVoiceDialog, setShowVoiceDialog] = useState(false);
  const permResolveRef = useRef(null);

  // Initialize first session
  useEffect(() => {
    if (!activeSessionId) {
      const s = newSession();
      setActiveSessionId(s.id);
      setChatItems([
        { type: "message", role: "assistant", text: WELCOME_MSG, time: new Date().toISOString() },
      ]);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle voice transcript
  useEffect(() => {
    if (transcript && !isListening) {
      handleSend(transcript);
    }
  }, [transcript, isListening]); // eslint-disable-line react-hooks/exhaustive-deps

  const addChatItem = useCallback((item) => {
    setChatItems((prev) => [...prev, item]);
  }, []);

  const handleNewSession = useCallback(() => {
    const s = newSession();
    setActiveSessionId(s.id);
    setChatItems([
      { type: "message", role: "assistant", text: WELCOME_MSG, time: new Date().toISOString() },
    ]);
  }, [newSession]);

  const handleSelectSession = useCallback(
    (id) => {
      const s = getSession(id);
      if (!s) return;
      setActiveSessionId(id);
      const items = s.messages.map((m) => ({
        type: "message",
        role: m.role,
        text: m.text,
        time: m.time,
      }));
      setChatItems(items.length > 0 ? items : [
        { type: "message", role: "assistant", text: WELCOME_MSG, time: new Date().toISOString() },
      ]);
    },
    [getSession]
  );

  const askPermission = (stepDesc, command) => {
    return new Promise((resolve) => {
      permResolveRef.current = resolve;
      setPermDialog({ step: stepDesc, command });
    });
  };

  const handlePermResponse = (answer) => {
    setPermDialog(null);
    if (permResolveRef.current) {
      permResolveRef.current(answer);
      permResolveRef.current = null;
    }
  };

  const runFixSteps = async (commands) => {
    addChatItem({
      type: "message",
      role: "assistant",
      text: `I have ${commands.length} fix steps. I'll ask permission for each.`,
      time: new Date().toISOString(),
    });

    let applied = 0;
    for (let i = 0; i < commands.length; i++) {
      const step = commands[i];
      const num = i + 1;
      const total = commands.length;

      addChatItem({
        type: "step",
        num,
        total,
        description: step.description,
        status: "running",
      });
      setStatus("diagnosing");
      setStatusLabel(`Step ${num}/${total}`);

      const answer = await askPermission(
        `Step ${num}: ${step.description}`,
        step.command
      );

      if (answer === "yes") {
        setOrbState("processing");
        try {
          const result = await call("execute_step", {
            command: step.command,
            admin: step.needs_admin,
          });
          const ok = result?.success;
          applied += ok ? 1 : 0;
          // Update the step status by adding a new step card
          addChatItem({
            type: "step",
            num,
            total,
            description: step.description,
            status: ok ? "done" : "failed",
          });
          addChatItem({
            type: "message",
            role: "assistant",
            text: `Result: ${result?.message || "Done"}`,
            time: new Date().toISOString(),
          });
        } catch (err) {
          addChatItem({
            type: "step",
            num,
            total,
            description: step.description,
            status: "failed",
          });
          addChatItem({
            type: "message",
            role: "assistant",
            text: `Error: ${err}`,
            time: new Date().toISOString(),
          });
        }
      } else if (answer === "no") {
        addChatItem({
          type: "step",
          num,
          total,
          description: step.description,
          status: "skipped",
        });
        break;
      } else {
        // skip
        addChatItem({
          type: "step",
          num,
          total,
          description: step.description,
          status: "skipped",
        });
      }
    }

    const summary =
      applied > 0
        ? `Done! ${applied}/${commands.length} steps applied.`
        : "No fixes applied.";
    addChatItem({
      type: "message",
      role: "assistant",
      text: summary,
      time: new Date().toISOString(),
    });

    // TTS
    try {
      await call("speak", { text: summary, lang });
    } catch {
      // silent
    }

    // Verification if fixes were applied
    if (applied > 0) {
      setStatus("processing");
      setStatusLabel("Verifying fix");
      addChatItem({
        type: "message",
        role: "assistant",
        text: "Verifying if the fix worked...",
        time: new Date().toISOString(),
      });
      try {
        const verifyResult = await call("verify");
        const vSteps = verifyResult?.steps || [];
        if (vSteps.length === 0) {
          addChatItem({
            type: "message",
            role: "assistant",
            text: "Looks good! No issues detected on screen.",
            time: new Date().toISOString(),
          });
        } else {
          addChatItem({
            type: "message",
            role: "assistant",
            text: `Still seeing an issue: ${verifyResult?.diagnosis || "Unknown"}. You can try Diagnose again.`,
            time: new Date().toISOString(),
          });
        }
      } catch {
        // verification failed silently
      }
    }
  };

  const handleSend = async (text) => {
    if (busy) return;
    setBusy(true);
    setOrbState("processing");
    setStatus("processing");
    setStatusLabel("Thinking");

    const now = new Date().toISOString();
    addChatItem({ type: "message", role: "user", text, time: now });
    if (activeSessionId) addMessage(activeSessionId, "user", text);

    try {
      const session = getSession(activeSessionId);
      const history = (session?.messages || []).slice(-10);
      const result = await call("chat", { text, lang, history });

      const reply = result?.reply || "I had trouble processing that.";
      addChatItem({ type: "message", role: "assistant", text: reply, time: new Date().toISOString() });
      if (activeSessionId) addMessage(activeSessionId, "assistant", reply);

      // TTS
      try {
        await call("speak", { text: reply, lang });
      } catch {
        // silent
      }

      // If commands were returned, run fix steps
      const commands = result?.commands || [];
      if (commands.length > 0) {
        await runFixSteps(commands);
      }
    } catch (err) {
      addChatItem({
        type: "message",
        role: "assistant",
        text: `I had trouble connecting: ${err}`,
        time: new Date().toISOString(),
      });
    } finally {
      setBusy(false);
      setOrbState("idle");
      setStatus("ready");
      setStatusLabel("Ready");
    }
  };

  const handleDiagnose = async () => {
    if (busy) return;
    setBusy(true);
    setOrbState("processing");
    setStatus("diagnosing");
    setStatusLabel("Diagnosing");

    addChatItem({
      type: "message",
      role: "assistant",
      text: "Scanning your screen...",
      time: new Date().toISOString(),
    });

    try {
      setStatusLabel("Capturing");
      const result = await call("diagnose");

      const diag = result?.diagnosis || "Unknown issue";
      const steps = result?.steps || [];

      addChatItem({
        type: "message",
        role: "assistant",
        text: `Diagnosis: ${diag}`,
        time: new Date().toISOString(),
      });

      try {
        await call("speak", { text: `I found the issue: ${diag}`, lang });
      } catch {
        // silent
      }

      if (steps.length > 0) {
        const commands = steps.map((s) => ({
          description: s.description,
          command: s.command,
          needs_admin: s.needs_admin || false,
        }));
        await runFixSteps(commands);
      } else {
        addChatItem({
          type: "message",
          role: "assistant",
          text: "No automated fix steps available.",
          time: new Date().toISOString(),
        });
      }
    } catch (err) {
      addChatItem({
        type: "message",
        role: "assistant",
        text: `Diagnosis failed: ${err}`,
        time: new Date().toISOString(),
      });
    } finally {
      setBusy(false);
      setOrbState("idle");
      setStatus("ready");
      setStatusLabel("Ready");
    }
  };

  const handleScreenshot = async () => {
    if (busy) return;
    setStatus("diagnosing");
    setStatusLabel("Capturing");
    try {
      const result = await call("screenshot");
      addChatItem({
        type: "message",
        role: "assistant",
        text: `Screenshot saved: ${result?.path || "unknown"}\nHit Diagnose to analyze it.`,
        time: new Date().toISOString(),
      });
    } catch (err) {
      addChatItem({
        type: "message",
        role: "assistant",
        text: `Screenshot failed: ${err}`,
        time: new Date().toISOString(),
      });
    } finally {
      setStatus("ready");
      setStatusLabel("Ready");
    }
  };

  const handleVoiceClick = () => {
    if (busy) return;
    if (isListening) {
      stopListening();
      setOrbState("idle");
    } else {
      const ok = startListening(lang);
      if (ok) {
        setOrbState("listening");
        setStatus("listening");
        setStatusLabel("Listening");
      } else {
        // Speech API not available — show text input dialog
        setShowVoiceDialog(true);
      }
    }
  };

  const handleVoiceDialogSubmit = (text) => {
    setShowVoiceDialog(false);
    setOrbState("idle");
    handleSend(text);
  };

  const handleVoiceDialogClose = () => {
    setShowVoiceDialog(false);
    setOrbState("idle");
    setStatus("ready");
    setStatusLabel("Ready");
  };

  // Update orb when speech recognition stops (only for real speech, not dialog fallback)
  useEffect(() => {
    if (!isListening && orbState === "listening" && !showVoiceDialog) {
      setOrbState("idle");
      setStatus("ready");
      setStatusLabel("Ready");
    }
  }, [isListening, orbState, showVoiceDialog]);

  return (
    <div className="flex h-screen bg-[#09090B]">
      <Sidebar
        sessions={sessions}
        activeId={activeSessionId}
        lang={lang}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onChangeLang={setLang}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <div className="flex items-center justify-between px-4 h-12 border-b border-white/5 flex-shrink-0">
          <h2 className="text-white font-semibold text-sm truncate">
            {getSession(activeSessionId)?.title || "New conversation"}
          </h2>
          <StatusBadge status={status} label={statusLabel} />
        </div>

        {/* Chat area */}
        <ChatArea items={chatItems} />

        {/* Voice orb */}
        <div className="flex justify-center py-2 flex-shrink-0">
          <VoiceOrb state={orbState} onClick={handleVoiceClick} />
        </div>

        {/* Input */}
        <InputBar
          onSend={handleSend}
          onDiagnose={handleDiagnose}
          onScreenshot={handleScreenshot}
          disabled={busy}
        />
      </div>

      {/* Permission dialog overlay */}
      {permDialog && (
        <PermissionDialog
          step={permDialog.step}
          command={permDialog.command}
          onRespond={handlePermResponse}
        />
      )}

      {/* Voice input fallback dialog */}
      {showVoiceDialog && (
        <VoiceInputDialog
          lang={lang}
          onSubmit={handleVoiceDialogSubmit}
          onClose={handleVoiceDialogClose}
        />
      )}
    </div>
  );
}
