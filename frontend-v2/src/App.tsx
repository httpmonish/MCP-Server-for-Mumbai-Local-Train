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
  const [persona, setPersona] = useState<PersonaType>('STUDENT');
  const [selectedRakeId, setSelectedRakeId] = useState<string>('95401');
  const [isLoadingRakes, setIsLoadingRakes] = useState(false);

  // User Profile
  const [currentUser, setCurrentUser] = useState<{
    name: string;
    org: string;
    role: string;
    token: string;
    prn?: string;
    semester?: string;
    utsPassId?: string;
  } | null>({
    name: 'Aditya Sharma',
    org: 'Veermata Jijabai Technological Institute (VJTI)',
    role: 'STUDENT',
    token: 'tp_demo_token_vjti',
    prn: 'PRN: 211080042',
    semester: 'Sem VI • B.Tech CS',
    utsPassId: 'UTS-II-CR-98401',
  });

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
    sectionTitle: 'Section: TNA-DR Quad-Track (Down Through)',
    activeRake: {
      trainNumber: '#95401 FAST',
      speed: '92 km/h',
      signal: 'Sig S-44 Clear (Proceed Aspect)',
      headway: 'Headway 3m 40s',
    },
    stations: [],
  });

  // Schedule Rakes
  const [rakes, setRakes] = useState<TrainRakeTelemetry[]>([]);

  // Origin & Destination
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

  // Attendance Risk State
  const [riskData, setRiskData] = useState<AttendanceRiskResult>({
    studentId: 'VJTI_211080042',
    studentName: 'Aditya Sharma',
    college: 'VJTI Mumbai • Sem VI',
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
    studentName: 'Aditya Sharma',
    rollNumber: '211080042',
    collegeName: 'VJTI Mumbai',
    trainRakeId: '#95201 SLOW',
    lineCorridor: 'Central Main Line',
    delayMinutes: 6,
    incidentLocation: 'Kurla Jcn Platform 1 Up Through',
    tmsSignalFailurePoint: 'Sig S-44 Track Circuit Fault (Kurla-Vidyavihar)',
    motormanRemarks: 'Delayed due to precedence given to 12138 Punjab Mail and track circuit drop.',
    issuedAt: '08:45 AM',
    validUntil: '15 Oct 2026',
    hodEmail: 'hod.computers@vjti.ac.in',
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
        currentUser?.prn || 'VJTI_211080042',
        selectedRakeId,
        '09:30 AM'
      );

      const selectedTrain = rakes.find((r) => r.id === selectedRakeId) || rakes[0];

      const token = await generateDelayToken(
        {
          name: currentUser?.name || 'Aditya Sharma',
          rollNumber: currentUser?.prn || '211080042',
          college: currentUser?.org || 'VJTI Mumbai',
        },
        {
          trainNumber: selectedTrain?.trainNumber || '#95201 SLOW',
          corridor: activeLine === 'western-line' ? 'Western Line' : 'Central Main Line',
          delayMinutes: selectedTrain?.delayMinutes || 6,
          failurePoint: 'Sig S-44 Track Circuit Fault (Kurla-Vidyavihar)',
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
      platform: nextReversed ? '01' : '05',
      activeGate: nextReversed ? 'Platform Gate East' : '08:42 AM Active Gate',
    };
    const tempDest = {
      code: origin.code,
      name: origin.name,
      campus: nextReversed ? 'Thane Central Junction' : 'VJTI Academic Campus',
    };
    setOrigin(tempOrigin);
    setDestination(tempDest);
  };

  // Handle Fast Rakes Filter
  const handleToggleFastOnly = () => {
    setFastOnly((prev) => !prev);
  };

  const handleSearchRakes = () => {
    setIsLoadingRakes(true);
    setTimeout(() => {
      setIsLoadingRakes(false);
    }, 600);
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
      />

      {/* Main Content Dashboard */}
      <main className="relative z-10 w-full pt-24 min-h-[calc(100vh-5rem)] pb-12">
        <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 py-4 flex flex-col gap-6">
          {/* Corridor Selector */}
          <CorridorSelector
            origin={origin}
            destination={destination}
            isReversed={isReversed}
            fastOnly={fastOnly}
            onSwap={handleSwapCorridor}
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
