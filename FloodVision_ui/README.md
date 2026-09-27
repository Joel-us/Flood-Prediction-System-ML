# FloodVision UI

FloodVision is a modern web interface for a machine-learning-based flood prediction system.

The frontend allows users to:

- Search for a location
- View weather and rainfall information
- Check flood risk
- View estimated flood probability
- View flood severity when a flood is predicted
- View supporting CWC and historical reference information
- Use the dashboard in light and dark themes

## Project Overview

FloodVision uses a two-stage prediction approach:

1. **Flood Prediction**
   - Predicts whether flooding is likely or not.
   - Displays the model-estimated flood probability.

2. **Flood Severity Prediction**
   - Runs only when a flood is predicted.
   - Estimates the flood type/severity.

The frontend communicates with the FloodVision FastAPI backend to obtain prediction results.

## Technology Stack

- React
- TypeScript
- TanStack Start
- TanStack Router
- Vite
- Tailwind CSS
- Recharts
- Lucide React

## Project Structure

```text
FloodVision_ui/
│
├── public/
├── src/
│   ├── components/
│   │   └── ui/
│   │
│   ├── features/
│   │   └── floodvision/
│   │       ├── brand-shell.tsx
│   │       ├── location-search.tsx
│   │       ├── result-cards.tsx
│   │       ├── loading-state.tsx
│   │       ├── types.ts
│   │       └── use-session.ts
│   │
│   ├── routes/
│   │   ├── index.tsx
│   │   ├── auth.tsx
│   │   └── __root.tsx
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   └── assets/
│       └── floodvision-logo.png
│
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md