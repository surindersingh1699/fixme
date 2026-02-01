const STATE_COLORS = {
  idle: "#6366F1",
  listening: "#6366F1",
  processing: "#8B5CF6",
  success: "#10B981",
  error: "#EF4444",
};

export default function VoiceOrb({ state = "idle", onClick }) {
  const color = STATE_COLORS[state] || STATE_COLORS.idle;
  const isAnimating = state === "listening" || state === "processing";

  return (
    <button
      onClick={onClick}
      className="relative flex items-center justify-center outline-none group"
      style={{ width: 130, height: 130 }}
    >
      <svg width="130" height="130" viewBox="0 0 130 130">
        {/* Outer rings */}
        {[0, 1, 2].map((i) => (
          <circle
            key={i}
            cx="65"
            cy="65"
            r={42 + i * 8}
            fill="none"
            stroke={["#818CF8", "#A78BFA", "#C084FC"][i]}
            strokeWidth={isAnimating ? 1.5 : 0.8}
            opacity={isAnimating ? 0.6 : 0.3}
            className={isAnimating ? "animate-pulse" : ""}
            style={isAnimating ? { animationDelay: `${i * 0.3}s` } : {}}
          />
        ))}

        {/* Main circle */}
        <circle
          cx="65"
          cy="65"
          r="34"
          fill={color}
          className="transition-colors duration-300 group-hover:brightness-110"
        />

        {/* State-specific content */}
        {state === "idle" && (
          <g transform="translate(53, 50)">
            <rect x="4" y="0" width="4" height="12" rx="2" fill="white" />
            <rect x="10" y="0" width="4" height="12" rx="2" fill="white" />
            <rect x="16" y="0" width="4" height="12" rx="2" fill="white" />
            <path
              d="M2 14 Q12 22 22 14"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <line
              x1="12"
              y1="22"
              x2="12"
              y2="26"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <line
              x1="6"
              y1="26"
              x2="18"
              y2="26"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </g>
        )}

        {state === "listening" &&
          [0, 1, 2, 3, 4].map((i) => (
            <rect
              key={i}
              x={53 + i * 6}
              y="59"
              width="3"
              rx="1.5"
              fill="white"
              className="animate-bounce"
              style={{
                animationDelay: `${i * 0.1}s`,
                animationDuration: "0.6s",
                height: 12,
                transformOrigin: "center",
              }}
            />
          ))}

        {state === "processing" &&
          [0, 1, 2].map((i) => (
            <circle
              key={i}
              cx={57 + i * 8}
              cy="65"
              r="2.5"
              fill="white"
              className="animate-bounce"
              style={{ animationDelay: `${i * 0.15}s`, animationDuration: "0.8s" }}
            />
          ))}

        {state === "success" && (
          <text
            x="65"
            y="70"
            textAnchor="middle"
            fill="white"
            fontSize="20"
            fontWeight="bold"
          >
            ✓
          </text>
        )}

        {state === "error" && (
          <text
            x="65"
            y="70"
            textAnchor="middle"
            fill="white"
            fontSize="20"
            fontWeight="bold"
          >
            ✕
          </text>
        )}
      </svg>

      {/* Label */}
      <span className="absolute -bottom-5 text-[11px] text-zinc-500 font-medium">
        {state === "idle" && "Tap to speak"}
        {state === "listening" && "Listening... tap to stop"}
        {state === "processing" && "Thinking..."}
        {state === "success" && "Done!"}
        {state === "error" && "Error"}
      </span>
    </button>
  );
}
