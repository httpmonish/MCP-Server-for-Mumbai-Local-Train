import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/Header';
import { CorridorSelector } from './components/CorridorSelector';
import { BlockClearanceMap } from './components/BlockClearanceMap';
import { LiveRakeList } from './components/LiveRakeList';
import { AttendanceRadar } from './components/AttendanceRadar';
import { CoreTelemetry } from './components/CoreTelemetry';
import { DispatchStream } from './components/DispatchStream';
import { Footer } from './components/Footer';
import { AuthModal } from './components/AuthModal';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false },
  },
});

export const MainApp: React.FC = () => {
  const [activeLine, setActiveLine] = useState('central-main');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<{
    name: string;
    org: string;
    role: string;
    token: string;
  } | null>(null);

  const [origin, setOrigin] = useState({
    code: 'TNA',
    name: 'Thane',
    platform: '05',
    activeGate: '08:42 AM Active Gate',
  });

  const [destination, setDestination] = useState({
    code: 'DR',
    name: 'Matunga / Dadar',
    campus: 'VJTI Academic Campus',
  });

  const [attendanceSummary, setAttendanceSummary] = useState({
    percentage: 74.3,
    min_percentage_required: 75.0,
    status: 'BELOW_THRESHOLD' as const,
    total_sessions: 35,
    counted_sessions: 35,
    present_count: 26,
    absent_count: 9,
    shortage_percentage: 0.7,
    sessions_needed_to_recover: 1,
  });

  const handleSwapCorridor = () => {
    const tempOrigin = {
      code: destination.code,
      name: destination.name,
      platform: '01',
      activeGate: 'Platform Gate East',
    };
    const tempDest = {
      code: origin.code,
      name: origin.name,
      campus: 'Thane Central Junction',
    };
    setOrigin(tempOrigin);
    setDestination(tempDest);
  };

  const handleFetchAttendance = async (token: string) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/attendance/me/summary', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setAttendanceSummary(data);
      }
    } catch (e) {
      console.log('Using offline attendance fallback telemetry', e);
    }
  };

  return (
    <div className="bg-surface-obsidian font-body text-text-primary relative min-h-screen selection:bg-primary-container selection:text-black">
      {/* Subtle Volumetric Radial Accents */}
      <div className="fixed inset-0 pointer-events-none z-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-10%,#14171F_0%,transparent_100%)]"></div>

      {/* Header */}
      <Header
        activeLine={activeLine}
        onSelectLine={setActiveLine}
        user={currentUser}
        onOpenAuth={() => setAuthModalOpen(true)}
      />

      {/* Main Content Dashboard */}
      <main className="relative z-10 w-full pt-24 min-h-[calc(100vh-5rem)]">
        <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 py-4 flex flex-col gap-6">
          {/* Corridor Selector */}
          <CorridorSelector
            origin={origin}
            destination={destination}
            onSwap={handleSwapCorridor}
            onSearch={() => console.log('Searching rakes...')}
          />

          {/* Block Clearance Topology Map */}
          <BlockClearanceMap />

          {/* Two-Column Editorial Layout */}
          <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Column 1: Live Upcoming Schedules (8 Cols) */}
            <div className="lg:col-span-8 flex flex-col gap-6">
              <LiveRakeList />
            </div>

            {/* Column 2: Commute AI & Academic Attendance Radar (4 Cols) */}
            <aside className="lg:col-span-4 flex flex-col gap-6">
              <AttendanceRadar summary={attendanceSummary} />
              <CoreTelemetry />
              <DispatchStream />
            </aside>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onLoginSuccess={(user) => {
          setCurrentUser(user);
          handleFetchAttendance(user.token);
        }}
      />
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainApp />
    </QueryClientProvider>
  );
}
