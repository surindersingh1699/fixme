# Landing Page

React + Vite + Tailwind CSS v4 single-page application deployed on Vercel.

## Directory Structure

```
landing/
├── src/
│   ├── App.jsx         # Main landing page component
│   ├── App.css         # (empty — Tailwind only)
│   ├── index.css       # Tailwind base + dark body
│   └── main.jsx        # React root mount
├── index.html          # HTML shell
├── vite.config.js      # Vite + Tailwind CSS v4 plugin
└── package.json        # Dependencies
```

## Sections

- **Nav** — Logo + navigation links
- **Hero** — Gradient blobs, headline, CTA button
- **Stats** — Key metrics (cost savings, ticket resolution)
- **Features** — 6 feature cards (screenshot diagnosis, voice, multilingual, etc.)
- **HowItWorks** — Step-by-step flow explanation
- **Languages** — 5-language selector (EN/ES/PA/HI/FR)
- **Comparison** — FixMe vs traditional IT support
- **CTA** — Call-to-action section
- **Footer** — Links and credits

## Theme

- **Background:** Dark (#09090B)
- **Brand accent:** Indigo (indigo-600)
- **Font:** Inter (Google Fonts)
- **Design system:** Matches the desktop app styling

## Running

```bash
cd landing
npm install
npm run dev     # Development (http://localhost:5173)
npm run build   # Production build
```

## Deployment

Deployed on Vercel. Push to `main` branch triggers automatic deployment.
