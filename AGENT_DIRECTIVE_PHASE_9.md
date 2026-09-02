# AGENT DIRECTIVE: Phase 9 — Frontend v2: Modern React + TypeScript + TanStack Query + PWA Architecture

You are a senior frontend architect. Implement Phase 9 (v2 Modernization) of the `mcp-data-server`. Your objective is to migrate the vanilla frontend into a production-grade, type-safe Single Page Application (SPA) and Progressive Web App (PWA) using Vite, React 18+, TypeScript, Tailwind CSS, TanStack Query v5 (React Query), and Zustand.

The application must support declarative state management, automatic background refetching, optimistic UI updates, zero-latency local caching, and offline Service Worker support for students checking commute schedules inside low-connectivity railway transit zones.

Every file below must be written in full production quality. Do not use placeholders, dummy stub methods, or un-typed `any` primitives.

---

## 1. PROJECT SETUP & TOOLING

Initialize the project under `frontend-v2/` with Vite and install runtime dependencies:
```bash
npm create vite@latest frontend-v2 -- --template react-ts
cd frontend-v2
npm install @tanstack/react-query @tanstack/react-query-devtools zustand lucide-react clsx tailwind-merge
npm install -D tailwindcss postcss autoprefixer vite-plugin-pwa @types/node vitest @testing-library/react @testing-library/jest-dom jsdom
npx tailwindcss init -p
```

---

## 2. FILE-BY-FILE PRODUCTION SPECIFICATIONS

### File 1: `frontend-v2/src/types/index.ts`
Define strict, immutable domain models and API response types matching the backend schemas.

### File 2: `frontend-v2/src/store/useAuthStore.ts`
Implement persistent client-side state management using Zustand with `localStorage` synchronization.

### File 3: `frontend-v2/src/api/client.ts`
Implement a centralized, typed fetch client with configurable timeout and error handling.

### File 4: `frontend-v2/src/hooks/useAcademic.ts`
Implement declarative data-fetching hooks using TanStack Query.

### File 5: `frontend-v2/src/hooks/useTrains.ts`
Implement real-time suburban railway tracking with 30-second background polling.

### File 6: `frontend-v2/src/components/AttendanceCard.tsx`
Create the responsive attendance monitor component with calculated aggregates and warning markers.

### File 7: `frontend-v2/src/components/TrainTrackerCard.tsx`
Create the suburban transit widget with dynamic countdown counters and line/type badges.

### File 8: `frontend-v2/src/App.tsx`
Create the main layout container with `QueryClientProvider` and `Dashboard`.

### File 9: `frontend-v2/vite.config.ts`
Configure Vite with TypeScript and `vite-plugin-pwa` for offline service worker caching.

### File 10: `frontend-v2/src/components/__tests__/AttendanceCard.test.tsx`
Write Vitest unit tests verifying aggregate attendance calculations and sub-75% alerts.

---

## 3. VERIFICATION COMMANDS

Execute the build verification and test suite:
```bash
cd frontend-v2
npm run build
npx vitest run
```
