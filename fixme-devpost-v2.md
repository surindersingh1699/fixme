# FixMe - DevPost Submission

## Inspiration

Working with an IT firm, I saw that **70%+ of tickets are repetitive issues** with known fixes — yet people wait hours for help. Password resets alone account for **20-50% of all helpdesk calls** (Gartner) and consume **31-40% of IT staff time**.

Those with language barriers struggle most. In the US alone, **nearly 1 in 10 working-age adults (19.2 million people) are limited English proficient** — they can't easily Google errors or follow English tutorials. **70% of users feel more loyal to companies that provide support in their native language**, yet only **28% actually see support in their native language**.

I watched users spend 45 minutes trying random YouTube fixes for problems that take 30 seconds to solve. That frustration — and the hidden costs behind it — inspired FixMe.

## The Cost Problem

| Metric | Cost |
|--------|------|
| **Average Tier 1 ticket** | $22 (MetricNet 2024) |
| **Average Tier 2 ticket** | $70 |
| **Average Tier 3 ticket** | $104 |
| **Single password reset** | $70 (Forrester) |
| **Annual password resets (1,000 employees)** | $70,000+ |
| **Mean time to resolve** | 9.72 hours |

Companies using AI see **25-30% cost reductions** and **resolution times dropping from 7+ hours to seconds**. Unity saved **$1.3M deflecting just 8,000 tickets** with AI.

## What it does

**FixMe** is an AI helpdesk that fixes IT issues in seconds, not hours.

- **Screenshot or describe your problem** — in any language
- **Talk to FixMe** — natural voice conversation powered by ElevenLabs
- **Get a step-by-step fix** — visible, not hidden in the background
- **Approve each step** in your language
- **Auto-document everything** for Tier 2 escalation if needed

No more Googling error codes. No more helpdesk queues for simple fixes.

## How we built it

We built FixMe using **Prompt-Driven Development (PDD)** — treating prompts as the source of truth, iterating rapidly, and only shipping when the agent behaves correctly.

**Tech Stack:**

- **Toolhouse** — Backend-as-a-Service for AI agents
  - Agent Studio for defining our IT support agent in natural language
  - Built-in RAG connected to IT knowledge bases
  - Memory for maintaining context across troubleshooting sessions
  - MCP Server integrations for external tools
  - One-click deployment as production-ready API

- **ElevenLabs** — Conversational AI voice
  - Natural voice interaction so users can describe problems by talking
  - Multilingual support for users who prefer speaking in their native language
  - Text-to-speech for reading fix instructions aloud
  - Makes IT support accessible to users who struggle with typing or reading English

**Architecture:**
1. **Voice/Vision Input** — User talks to FixMe or screenshots an error (ElevenLabs + Vision)
2. **Toolhouse Agent** — Processes input, queries knowledge base, identifies fix
3. **Step-by-step Executor** — Presents each action with user permission prompts
4. **Documentation Logger** — Records every attempted fix for escalation

PDD let us iterate on agent behavior rapidly — prompts as source of truth, regenerate code, ship only if tests pass. Toolhouse + ElevenLabs let us go from idea to working prototype in hours.

## Challenges we ran into

**Balancing automation with transparency.** Microsoft's troubleshooters work in the background — you never know what they tried. We designed FixMe to show every action and ask permission at each step.

**Language accessibility.** We wanted someone with limited English to feel just as confident as a native speaker — that meant voice-first interaction (ElevenLabs), simpler language, and prompts in the user's preferred language.

## Accomplishments that we're proud of

- **Voice-first support** — Talk to FixMe like you'd talk to a coworker
- **Transparent fixes** — Users see exactly what's happening
- **Built-in escalation docs** — Tier 2 gets a complete record (no more "I already tried that")
- **Multilingual** — Works in the user's native language
- **Real cost impact** — Could save companies $65K+ annually on password resets alone

## What we learned

This problem is **massively underserved**. 

Microsoft's troubleshoot agents are black boxes. **Generative AI can reduce ticket volume by 60%**, and companies using automation **resolve tickets 52% faster** — yet most solutions sacrifice transparency for speed.

We learned **transparency builds trust**. When FixMe shows each step and asks permission, users feel empowered instead of anxious. And **voice changes everything** — users who struggled to type error messages can just describe what's wrong.

## What's next for FixMe

**Expanding coverage:**
- All Tier 1 issues, then Tier 2 complexity
- Partner with companies for **custom solutions using their internal docs**

**Enhanced features:**
- Step-by-step visible execution (watch FixMe fix in real-time)
- Permission prompts in user's preferred language
- Secure password management connectors
- Integration with ServiceNow, Zendesk, existing ticketing systems

**Our vision:** Turn IT issues from a frustrating experience into an easy one. No more dread when something breaks — just confidence that FixMe has your back, in your language.
