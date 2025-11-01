# Financial Asset Relationship Frontend

This is the Next.js frontend for the Financial Asset Relationship Database.

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp ../.env.example .env.local
```

3. Make sure the backend API is running on `http://localhost:8000`

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build

Create a production build:

```bash
npm run build
```

### Start Production Server

After building:

```bash
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── components/      # React components
│   │   ├── AssetList.tsx
│   │   ├── MetricsDashboard.tsx
│   │   └── NetworkVisualization.tsx
│   ├── lib/            # Utility libraries
│   │                   # (no api.ts present)
│   ├── types/          # TypeScript type definitions
│   │   └── api.ts
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Main page
├── public/             # Static assets
├── next.config.js      # Next.js configuration
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript configuration
└── tailwind.config.js  # Tailwind CSS configuration
```

## Features

- **3D Visualization**: Interactive 3D network graph using Plotly
- **Metrics Dashboard**: Key statistics and analytics
- **Asset Explorer**: Filterable table of all assets
- **Responsive Design**: Works on desktop and mobile devices
- **Type Safety**: Full TypeScript support

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, set this to your deployed API URL.

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Plotly.js](https://plotly.com/javascript/)
