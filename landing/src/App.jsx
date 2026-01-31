import { useState, useEffect } from "react";

/* ─── Reusable Section Wrapper ─────────────────────────────────────────────── */
const Section = ({ children, className = "" }) => (
  <section className={`px-6 md:px-12 lg:px-24 py-20 ${className}`}>
    <div className="max-w-6xl mx-auto">{children}</div>
  </section>
);

/* ─── Animated gradient blob (hero background) ─────────────────────────────── */
const GradientBlob = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-indigo-600/15 blur-[160px] animate-pulse" />
    <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] rounded-full bg-purple-600/10 blur-[120px] animate-pulse [animation-delay:1s]" />
    <div className="absolute bottom-1/3 right-1/3 w-[350px] h-[350px] rounded-full bg-cyan-500/8 blur-[100px] animate-pulse [animation-delay:2s]" />
  </div>
);

/* ─── Nav ──────────────────────────────────────────────────────────────────── */
const Nav = () => {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", h, { passive: true });
    return () => window.removeEventListener("scroll", h);
  }, []);
  return (
    <nav
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-zinc-950/80 backdrop-blur-xl border-b border-white/5"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 md:px-12 lg:px-24 h-16">
        <a href="#" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
            F
          </div>
          <span className="text-white font-semibold text-lg tracking-tight">
            FixMe
          </span>
        </a>
        <div className="hidden md:flex items-center gap-8 text-sm text-zinc-400">
          <a href="#features" className="hover:text-white transition">
            Features
          </a>
          <a href="#how-it-works" className="hover:text-white transition">
            How It Works
          </a>
          <a href="#languages" className="hover:text-white transition">
            Languages
          </a>
        </div>
        <a
          href="https://github.com/surindersingh1699/fixme/releases"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-5 py-2 rounded-full transition"
        >
          Download
        </a>
      </div>
    </nav>
  );
};

/* ─── Hero ─────────────────────────────────────────────────────────────────── */
const Hero = () => (
  <section className="relative min-h-screen flex items-center justify-center text-center pt-16">
    <GradientBlob />
    <div className="relative z-10 max-w-3xl mx-auto px-6">
      <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 text-sm text-zinc-400 mb-8">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        Built for Hackathon 2025
      </div>

      <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
        AI IT Support
        <br />
        <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
          That Speaks Your Language
        </span>
      </h1>

      <p className="mt-6 text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
        FixMe sees your screen, diagnoses issues in real time, and walks you
        through fixes step by step — with voice, in 5 languages. No jargon.
        No hold music.
      </p>

      <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
        <a
          href="https://github.com/surindersingh1699/fixme/releases"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-8 py-3.5 rounded-full text-base transition shadow-lg shadow-indigo-600/25 hover:shadow-indigo-600/40"
        >
          Download for Free
        </a>
        <a
          href="https://github.com/surindersingh1699/fixme"
          target="_blank"
          rel="noopener noreferrer"
          className="text-zinc-400 hover:text-white border border-white/10 hover:border-white/20 px-8 py-3.5 rounded-full text-base transition"
        >
          View on GitHub
        </a>
      </div>

      {/* Mock UI preview */}
      <div className="mt-16 relative">
        <div className="bg-zinc-900/60 border border-white/10 rounded-2xl p-1 shadow-2xl backdrop-blur">
          <div className="bg-zinc-950 rounded-xl overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="ml-3 text-xs text-zinc-500 font-mono">
                FixMe — AI IT Support
              </span>
            </div>
            <div className="p-8 space-y-4">
              <div className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                  F
                </div>
                <div className="bg-zinc-800/60 rounded-xl px-4 py-3 text-sm text-zinc-300 max-w-md text-left">
                  Hey! I scanned your screen and found a DNS resolution error. I
                  have 3 steps to fix it. Shall I walk you through?
                </div>
              </div>
              <div className="flex gap-3 items-start justify-end">
                <div className="bg-indigo-600 rounded-xl px-4 py-3 text-sm text-white max-w-xs text-left">
                  Yes, please fix it!
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                  F
                </div>
                <div className="bg-zinc-800/60 rounded-xl px-4 py-3 text-sm text-zinc-300 max-w-md text-left">
                  <span className="text-emerald-400 font-medium">Step 1/3</span>{" "}
                  — Flushing DNS cache... Done!
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

/* ─── Stats Bar ────────────────────────────────────────────────────────────── */
const stats = [
  { value: "5", label: "Languages Supported" },
  { value: "< 30s", label: "Average Diagnosis" },
  { value: "100%", label: "Open Source" },
  { value: "0", label: "Jargon" },
];

const Stats = () => (
  <Section className="!py-12 border-y border-white/5">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
      {stats.map((s, i) => (
        <div key={i}>
          <div className="text-3xl font-bold text-white">{s.value}</div>
          <div className="text-sm text-zinc-500 mt-1">{s.label}</div>
        </div>
      ))}
    </div>
  </Section>
);

/* ─── Features ─────────────────────────────────────────────────────────────── */
const features = [
  {
    icon: "🖥️",
    title: "Screen Diagnosis",
    desc: "Takes a screenshot, analyzes it with AI, and identifies the exact issue — no manual explanation needed.",
  },
  {
    icon: "🔧",
    title: "Step-by-Step Fixes",
    desc: "Walks you through each fix one at a time, asking for your permission before executing anything.",
  },
  {
    icon: "🎙️",
    title: "Voice Interaction",
    desc: "Speak your problem out loud. FixMe listens, understands, and responds — hands-free IT support.",
  },
  {
    icon: "🌍",
    title: "5 Languages",
    desc: "English, Spanish, Punjabi, Hindi, and French. Speak in your language, get help in your language.",
  },
  {
    icon: "🔒",
    title: "Permission First",
    desc: "Every fix step requires your explicit approval. Nothing runs on your machine without your say-so.",
  },
  {
    icon: "🧠",
    title: "Powered by Claude",
    desc: "Uses Anthropic's Claude for intelligent diagnosis and natural conversation about your issues.",
  },
];

const Features = () => (
  <Section>
    <div className="text-center mb-16" id="features">
      <h2 className="text-3xl md:text-4xl font-bold text-white">
        Everything you need to fix IT issues
      </h2>
      <p className="text-zinc-400 mt-4 max-w-xl mx-auto">
        No tickets. No hold music. No confusing jargon. Just tell FixMe what's
        wrong and it handles the rest.
      </p>
    </div>
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {features.map((f, i) => (
        <div
          key={i}
          className="group bg-white/[0.03] border border-white/5 rounded-2xl p-6 hover:border-indigo-500/30 hover:bg-white/[0.05] transition-all duration-300"
        >
          <div className="text-3xl mb-4">{f.icon}</div>
          <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
          <p className="text-zinc-400 text-sm leading-relaxed">{f.desc}</p>
        </div>
      ))}
    </div>
  </Section>
);

/* ─── How It Works ─────────────────────────────────────────────────────────── */
const steps = [
  {
    num: "01",
    title: "Describe or Show",
    desc: "Speak your problem aloud or type it. Or just hit 'Diagnose Screen' and FixMe will look at what's on your screen.",
  },
  {
    num: "02",
    title: "AI Diagnosis",
    desc: "FixMe analyzes your screen with Claude AI, identifies the root cause, and generates a step-by-step fix plan.",
  },
  {
    num: "03",
    title: "Guided Fix",
    desc: "Each step is explained in plain language. Say 'yes' to apply, 'skip' to move on, or 'stop' at any time.",
  },
];

const HowItWorks = () => (
  <Section className="bg-zinc-950/50">
    <div className="text-center mb-16" id="how-it-works">
      <h2 className="text-3xl md:text-4xl font-bold text-white">
        Three steps to fixed
      </h2>
      <p className="text-zinc-400 mt-4">
        From broken to working in under a minute.
      </p>
    </div>
    <div className="grid md:grid-cols-3 gap-8">
      {steps.map((s, i) => (
        <div key={i} className="relative">
          <div className="text-5xl font-extrabold text-indigo-600/20 mb-4">
            {s.num}
          </div>
          <h3 className="text-xl font-semibold text-white mb-3">{s.title}</h3>
          <p className="text-zinc-400 text-sm leading-relaxed">{s.desc}</p>
          {i < 2 && (
            <div className="hidden md:block absolute top-8 -right-4 text-zinc-700 text-2xl">
              &rarr;
            </div>
          )}
        </div>
      ))}
    </div>
  </Section>
);

/* ─── Languages ────────────────────────────────────────────────────────────── */
const langs = [
  { code: "en", name: "English", greeting: "Hello, how can I help?" },
  { code: "es", name: "Spanish", greeting: "Hola, ¿cómo puedo ayudar?" },
  { code: "pa", name: "Punjabi", greeting: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਂ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?" },
  { code: "hi", name: "Hindi", greeting: "नमस्ते, मैं कैसे मदद कर सकता हूँ?" },
  { code: "fr", name: "French", greeting: "Bonjour, comment puis-je aider?" },
];

const Languages = () => {
  const [active, setActive] = useState(0);
  return (
    <Section>
      <div className="text-center mb-16" id="languages">
        <h2 className="text-3xl md:text-4xl font-bold text-white">
          Speaks your language
        </h2>
        <p className="text-zinc-400 mt-4">
          Voice input and output in 5 languages — more coming soon.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-3 mb-10">
        {langs.map((l, i) => (
          <button
            key={l.code}
            onClick={() => setActive(i)}
            className={`px-5 py-2.5 rounded-full text-sm font-medium transition ${
              i === active
                ? "bg-indigo-600 text-white"
                : "bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-white"
            }`}
          >
            {l.name}
          </button>
        ))}
      </div>
      <div className="bg-white/[0.03] border border-white/10 rounded-2xl p-8 text-center max-w-lg mx-auto">
        <div className="w-16 h-16 rounded-full bg-indigo-600/20 flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-7 h-7 text-indigo-400"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        </div>
        <p className="text-2xl text-white font-medium">
          "{langs[active].greeting}"
        </p>
        <p className="text-zinc-500 text-sm mt-3">
          FixMe in {langs[active].name}
        </p>
      </div>
    </Section>
  );
};

/* ─── Comparison ───────────────────────────────────────────────────────────── */
const Comparison = () => (
  <Section className="bg-zinc-950/50">
    <div className="text-center mb-16">
      <h2 className="text-3xl md:text-4xl font-bold text-white">
        The old way vs the FixMe way
      </h2>
    </div>
    <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
      <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-8">
        <div className="text-red-400 font-semibold text-sm uppercase tracking-wide mb-4">
          Without FixMe
        </div>
        <ul className="space-y-3 text-zinc-400 text-sm">
          {[
            "Google error messages for 30 minutes",
            "Call IT, wait on hold for an hour",
            "Try random Stack Overflow solutions",
            "Explain your problem in English only",
            "Give full remote access to a stranger",
          ].map((t, i) => (
            <li key={i} className="flex gap-3">
              <span className="text-red-400/60">✕</span>
              {t}
            </li>
          ))}
        </ul>
      </div>
      <div className="bg-indigo-600/5 border border-indigo-500/20 rounded-2xl p-8">
        <div className="text-indigo-400 font-semibold text-sm uppercase tracking-wide mb-4">
          With FixMe
        </div>
        <ul className="space-y-3 text-zinc-300 text-sm">
          {[
            "AI scans your screen instantly",
            "Get a fix plan in under 30 seconds",
            "Each step explained in plain language",
            "Speak in 5 different languages",
            "You approve every action — full control",
          ].map((t, i) => (
            <li key={i} className="flex gap-3">
              <span className="text-emerald-400">✓</span>
              {t}
            </li>
          ))}
        </ul>
      </div>
    </div>
  </Section>
);

/* ─── CTA ──────────────────────────────────────────────────────────────────── */
const CTA = () => (
  <Section>
    <div className="relative text-center bg-gradient-to-b from-indigo-600/10 to-transparent border border-white/5 rounded-3xl py-20 px-8 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(99,102,241,0.15),_transparent_70%)]" />
      <div className="relative z-10">
        <h2 className="text-3xl md:text-5xl font-bold text-white">
          Ready to fix things?
        </h2>
        <p className="text-zinc-400 mt-4 max-w-md mx-auto">
          Download FixMe — it's free, open source, and ready to help.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="https://github.com/surindersingh1699/fixme/releases"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-10 py-4 rounded-full text-lg transition shadow-lg shadow-indigo-600/25"
          >
            Download Now
          </a>
          <a
            href="https://github.com/surindersingh1699/fixme"
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-400 hover:text-white transition text-sm"
          >
            Star on GitHub &rarr;
          </a>
        </div>
      </div>
    </div>
  </Section>
);

/* ─── Footer ───────────────────────────────────────────────────────────────── */
const Footer = () => (
  <footer className="border-t border-white/5 py-8 px-6 md:px-12 lg:px-24">
    <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-zinc-500">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
          F
        </div>
        <span>FixMe</span>
      </div>
      <div>Built for the Hackathon &middot; Open Source &middot; MIT License</div>
      <a
        href="https://github.com/surindersingh1699/fixme"
        target="_blank"
        rel="noopener noreferrer"
        className="hover:text-white transition"
      >
        GitHub
      </a>
    </div>
  </footer>
);

/* ─── App ──────────────────────────────────────────────────────────────────── */
export default function App() {
  return (
    <div className="bg-[#09090B] text-white min-h-screen antialiased">
      <Nav />
      <Hero />
      <Stats />
      <Features />
      <HowItWorks />
      <Languages />
      <Comparison />
      <CTA />
      <Footer />
    </div>
  );
}
