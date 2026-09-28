import React, { useState, useEffect } from 'react';
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
import type { PersonaType } from './components/modals/UserProfilePopover';
import { GapAnalysisDrawer } from './components/dev/GapAnalysisDrawer';
import {
  fetchCorridorTelemetry,
  fetchTrainSchedule,
  calculateAttendanceRisk,
  generateDelayToken,
  CORRIDOR_STATIONS,
} from './lib/services/telemetryService';
import type {
  CorridorId,
  Direction,
  TrainRakeTelemetry,
  StationTelemetry,
  AttendanceRiskResult,
  DelayTokenPayload,
} from './lib/services/telemetryService';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false },
  },
});

export const MainApp: React.FC = () => {
  const [activeLine, setActiveLine] = useState<CorridorId>('central-main');
  const [direction, setDirection] = useState<Direction>('DOWN');
  const [isReversed, setIsReversed] = useState(false);
  const [fastOnly, setFastOnly] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [persona, setPersona] = useState<PersonaType>('COMMUTER'); // Normal commuter by default
  const [selectedRakeId, setSelectedRakeId] = useState<string>('95401');
  const [isLoadingRakes, setIsLoadingRakes] = useState(false);

  // User Profile - null by default (Guest Commuter mode)
  const [currentUser, setCurrentUser] = useState<{
    name: string;
    org: string;
    role: string;
    token: string;
    prn?: string;
    semester?: string;
    utsPassId?: string;
  } | null>(null);

  // Stations & Active Telemetry
  const [corridorTelemetry, setCorridorTelemetry] = useState<{
    sectionTitle: string;
    activeRake: {
      trainNumber: string;
      speed: string;
      signal: string;
      headway: string;
    };
    stations: StationTelemetry[];
  }>({
    sectionTitle: 'Section: CSMT → KYN (Central Main Down Through)',
    activeRake: {
      trainNumber: '#95401 FAST',
      speed: '92 km/h',
      signal: 'Sig Clear (Proceed Aspect)',
      headway: 'Headway 3m 40s',
    },
    stations: CORRIDOR_STATIONS['central-main'],
  });

  // Schedule Rakes
  const [rakes, setRakes] = useState<TrainRakeTelemetry[]>([]);

  // Origin & Destination default
  const [origin, setOrigin] = useState({
    code: 'CSMT',
    name: 'CSMT Terminus',
    platform: '04',
    activeGate: 'Main Concourse Gate',
  });

  const [destination, setDestination] = useState({
    code: 'KYN',
    name: 'Kalyan Junction',
    campus: 'Central Suburban Hub',
  });

  // Attendance / Punctuality Risk State
  const [riskData, setRiskData] = useState<AttendanceRiskResult>({
    studentId: 'COMMUTER_98401',
    studentName: 'Commuter Aditya',
    college: 'Mumbai Suburban Network',
    currentPercentage: 75.4,
    simulatedPercentage: 75.4,
    minRequiredPercentage: 75.0,
    status: 'SAFE',
    selectedTrainNumber: '#95401 FAST',
    etaDadar: '09:23 AM',
    lectureStartTime: '09:30 AM',
    bufferMinutes: 12,
    walkMinutes: 7,
    willReachOnTime: true,
    contingencyProtocol: 'SPRINT_MATUNGA_WALK',
  });

  // Delay Token State
  const [tokenData, setTokenData] = useState<DelayTokenPayload>({
    tokenUuid: 'CR-TMS-98412-2026',
    verificationSha256: '9A8B7C6D5E4F3A2B1C0D9E8F7A6B5C4D',
    studentName: 'Commuter Aditya',
    rollNumber: 'COMMUTER-PASS-98401',
    collegeName: 'Mumbai Suburban Network',
    trainRakeId: '#95201 SLOW',
    lineCorridor: 'Central Main Line',
    delayMinutes: 6,
    incidentLocation: 'Kurla Jcn Platform 1 Up Through',
    tmsSignalFailurePoint: 'Sig S-44 Track Circuit Fault (Kurla-Vidyavihar)',
    motormanRemarks: 'Delayed due to precedence given to 12138 Punjab Mail and track circuit drop.',
    issuedAt: '08:45 AM',
    validUntil: '15 Oct 2026',
    hodEmail: 'commuter.support@transitpulse.app',
    digitalSignature: 'CR/MUM/TMS/SIG/2026/098412',
    verificationUrl: 'https://transitpulse.app/verify/delay/CR-TMS-98412',
  });

  // 1. Fetch Corridor Telemetry when activeLine or direction changes
  useEffect(() => {
    let mounted = true;
    const loadCorridor = async () => {
      const data = await fetchCorridorTelemetry(activeLine, direction);
      if (mounted) {
        setCorridorTelemetry({
          sectionTitle: data.sectionTitle,
          activeRake: data.activeRake,
          stations: data.stations,
        });

        // Set line-appropriate default origin and destination when switching lines
        if (data.stations.length >= 2) {
          const first = data.stations[0];
          const last = data.stations[data.stations.length - 1];
          setOrigin({
            code: first.code,
            name: first.name,
            platform: '02',
            activeGate: 'Active Gate 1',
          });
          setDestination({
            code: last.code,
            name: last.name,
            campus: `${activeLine.toUpperCase().replace('-', ' ')} Hub`,
          });
        }
      }
    };
    loadCorridor();
    return () => {
      mounted = false;
    };
  }, [activeLine, direction]);

  // 2. Fetch Train Schedules when origin, destination, corridor, or fastOnly changes
  useEffect(() => {
    let mounted = true;
    const loadSchedules = async () => {
      setIsLoadingRakes(true);
      const scheduleList = await fetchTrainSchedule(origin.code, destination.code, activeLine);
      if (mounted) {
        const filtered = fastOnly
          ? scheduleList.filter((r) => r.trainType === 'FAST' || r.trainType === 'AC_FAST')
          : scheduleList;
        setRakes(filtered);
        setIsLoadingRakes(false);
      }
    };
    loadSchedules();
    return () => {
      mounted = false;
    };
  }, [origin.code, destination.code, activeLine, fastOnly]);

  // 3. Recalculate Attendance Risk & Delay Token when selected rake changes
  useEffect(() => {
    let mounted = true;
    const updateRiskAndToken = async () => {
      const risk = await calculateAttendanceRisk(
        currentUser?.prn || 'COMMUTER_98401',
        selectedRakeId,
        '09:30 AM'
      );

      const selectedTrain = rakes.find((r) => r.id === selectedRakeId) || rakes[0];

      const token = await generateDelayToken(
        {
          name: currentUser?.name || 'Commuter Passenger',
          rollNumber: currentUser?.prn || 'UTS-PASS-98401',
          college: currentUser?.org || 'Mumbai Suburban Commuter Network',
        },
        {
          trainNumber: selectedTrain?.trainNumber || '#95201 SLOW',
          corridor: activeLine.replace('-', ' ').toUpperCase(),
          delayMinutes: selectedTrain?.delayMinutes || 6,
          failurePoint: 'Sig Track Circuit Drop',
        }
      );

      if (mounted) {
        setRiskData(risk);
        setTokenData(token);
      }
    };
    updateRiskAndToken();
    return () => {
      mounted = false;
    };
  }, [selectedRakeId, rakes, currentUser, activeLine]);

  // Handle Swap Corridor Route
  const handleSwapCorridor = () => {
    const nextReversed = !isReversed;
    setIsReversed(nextReversed);
    setDirection(nextReversed ? 'UP' : 'DOWN');

    const tempOrigin = {
      code: destination.code,
      name: destination.name,
      platform: nextReversed ? '01' : '04',
      activeGate: nextReversed ? 'Return Platform Gate' : '08:42 AM Active Gate',
    };
    const tempDest = {
      code: origin.code,
      name: origin.name,
      campus: nextReversed ? 'Origin Terminal' : 'Destination Hub',
    };
    setOrigin(tempOrigin);
    setDestination(tempDest);
  };

  // Station Pickers
  const handleSelectOrigin = (st: { code: string; name: string }) => {
    setOrigin({
      code: st.code,
      name: st.name,
      platform: '02',
      activeGate: 'Platform Gate Ingress',
    });
  };

  const handleSelectDestination = (st: { code: string; name: string }) => {
    setDestination({
      code: st.code,
      name: st.name,
      campus: `${st.name} Transit Junction`,
    });
  };

  // Logout Handler
  const handleLogout = () => {
    setCurrentUser(null);
    setPersona('COMMUTER');
  };

  // Fast Rakes Filter
  const handleToggleFastOnly = () => {
    setFastOnly((prev) => !prev);
  };

  const handleSearchRakes = () => {
    setIsLoadingRakes(true);
    setTimeout(() => {
      setIsLoadingRakes(false);
    }, 500);
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
        currentPersona={persona}
        onSelectPersona={setPersona}
        onOpenAuth={() => setAuthModalOpen(true)}
        onOpenEditProfile={() => setAuthModalOpen(true)}
        onLogout={handleLogout}
      />

      {/* Main Content Dashboard */}
      <main className="relative z-10 w-full pt-24 min-h-[calc(100vh-5rem)] pb-12">
        <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 py-4 flex flex-col gap-6">
          {/* Corridor & Station Selector */}
          <CorridorSelector
            origin={origin}
            destination={destination}
            isReversed={isReversed}
            fastOnly={fastOnly}
            onSwap={handleSwapCorridor}
            onSelectOrigin={handleSelectOrigin}
            onSelectDestination={handleSelectDestination}
            onToggleFastOnly={handleToggleFastOnly}
            onSearch={handleSearchRakes}
            isLoadingRakes={isLoadingRakes}
          />

          {/* Block Clearance Topology Map */}
          <BlockClearanceMap
            sectionTitle={corridorTelemetry.sectionTitle}
            activeRake={corridorTelemetry.activeRake}
            stations={corridorTelemetry.stations}
          />

          {/* Two-Column Editorial Layout */}
          <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Column 1: Live Upcoming Schedules (8 Cols) */}
            <div className="lg:col-span-8 flex flex-col gap-6">
              <LiveRakeList
                rakes={rakes}
                selectedRakeId={selectedRakeId}
                onSelectRake={setSelectedRakeId}
                isLoading={isLoadingRakes}
              />
            </div>

            {/* Column 2: Commute AI & Academic Attendance Radar (4 Cols) */}
            <aside className="lg:col-span-4 flex flex-col gap-6">
              <AttendanceRadar riskData={riskData} tokenData={tokenData} />
              <CoreTelemetry />
              <DispatchStream />
            </aside>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />

      {/* Developer Bidirectional Gap Analysis Drawer */}
      <GapAnalysisDrawer />

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onLoginSuccess={(user) => {
          setCurrentUser(user);
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
