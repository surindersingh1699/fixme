import { useState, useRef, useCallback } from "react";

const LANG_MAP = {
  en: "en-US",
  es: "es-ES",
  pa: "pa-IN",
  hi: "hi-IN",
  fr: "fr-FR",
};

export function useSpeechRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);

  const startListening = useCallback((lang = "en") => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("SpeechRecognition not available");
      return false;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = LANG_MAP[lang] || "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      setIsListening(false);
    };

    recognition.onerror = (e) => {
      console.warn("SpeechRecognition error:", e.error);
      setIsListening(false);
      setError(e.error || "not-allowed");
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (e) {
      console.warn("SpeechRecognition.start() failed:", e);
      return false;
    }
    setIsListening(true);
    setTranscript("");
    setError(null);
    return true;
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  return { isListening, transcript, error, startListening, stopListening };
}
