/**
 * मुंबईTeleport - Model Context Protocol (MCP) & Suburban Flow Telemetry Service Layer
 */

export type CorridorId = 'central-main' | 'western-line' | 'harbour' | 'trans-harbour';
export type Direction = 'DOWN' | 'UP';

export interface StationStopSchedule {
  stationCode: string;
  stationName: string;
  distanceKm: number;
  arrivalTime: string;
  departureTime: string;
  dwellSeconds: number;
  platform: string;
  status: 'PASSED' | 'CURRENT' | 'UPCOMING';
  fobCongestion?: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
}

export interface StationTelemetry {
  code: string;
  name: string;
  distanceKm: number;
  arrivalTime?: string;
  departureTime?: string;
  platform?: string;
  dwellSeconds?: number;
  status?: 'PASSED' | 'CURRENT' | 'UPCOMING';
  platforms: {
    number: string;
    occupancyPercent: number;
    fobCongestion: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
    crossoverSpeedKm: number;
  }[];
}

export interface TrainRakeTelemetry {
  id: string;
  trainNumber: string;
  trainType: 'FAST' | 'SLOW' | 'AC_FAST' | 'LADIES_SPECIAL';
  lineCode: string;
  originCode: string;
  originName?: string;
  destinationCode: string;
  destinationName?: string;
  departureTime: string;
  arrivalTime: string;
  durationMins: number;
  stopsCount: number;
  viaDescription: string;
  currentSpeedKm: number;
  signalAspect: string;
  headwayText: string;
  platform: string;
  totalLoadPercent: number;
  status: 'ON_TIME' | 'DELAYED' | 'CANCELLED';
  delayMinutes: number;
  coachMatrix: {
    coachNumber: number;
    coachType: 'GENERAL' | 'FIRST_CLASS' | 'LADIES' | 'DIVYANG' | 'AC';
    crowdPercent: number;
    fobAlignmentText: string;
    description: string;
  }[];
  stops: StationStopSchedule[];
  temperatureC?: number;
  targetDeltaMins: number;
  arrivalBufferText: string;
}

export interface AttendanceRiskResult {
  studentId: string;
  studentName: string;
  college: string;
  currentPercentage: number;
  simulatedPercentage: number;
  minRequiredPercentage: number;
  status: 'SAFE' | 'DEBARMENT_RISK' | 'CRITICAL_SHORTAGE';
  selectedTrainNumber: string;
  etaDadar: string;
  lectureStartTime: string;
  bufferMinutes: number;
  walkMinutes: number;
  willReachOnTime: boolean;
  contingencyProtocol: 'SPRINT_MATUNGA_WALK' | 'ISSUE_CR_DELAY_TOKEN';
}

export interface DelayTokenPayload {
  tokenUuid: string;
  verificationSha256: string;
  studentName: string;
  rollNumber: string;
  collegeName: string;
  trainRakeId: string;
  lineCorridor: string;
  delayMinutes: number;
  incidentLocation: string;
  tmsSignalFailurePoint: string;
  motormanRemarks: string;
  issuedAt: string;
  validUntil: string;
  hodEmail: string;
  digitalSignature: string;
  verificationUrl: string;
}

// In-memory simulation jitter state
let jitterSpeedOffset = 0;
setInterval(() => {
  jitterSpeedOffset = Math.floor(Math.random() * 7) - 3;
}, 3000);

/**
 * All Stations per Corridor for Dynamic Tracking & Selection
 */
export const CORRIDOR_STATIONS: Record<CorridorId, StationTelemetry[]> = {
  'central-main': [
    {
      code: 'CSMT',
      name: 'CSMT Terminus',
      distanceKm: 0.0,
      platforms: [
        { number: '01', occupancyPercent: 65, fobCongestion: 'LOW', crossoverSpeedKm: 25 },
        { number: '04', occupancyPercent: 78, fobCongestion: 'MODERATE', crossoverSpeedKm: 30 },
      ],
    },
    {
      code: 'DR',
      name: 'Dadar Central',
      distanceKm: 9.0,
      platforms: [
        { number: '03', occupancyPercent: 92, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
        { number: '04', occupancyPercent: 84, fobCongestion: 'HIGH', crossoverSpeedKm: 45 },
      ],
    },
    {
      code: 'CLA',
      name: 'Kurla Junction',
      distanceKm: 15.3,
      platforms: [
        { number: '01', occupancyPercent: 90, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
        { number: '05', occupancyPercent: 70, fobCongestion: 'MODERATE', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'GC',
      name: 'Ghatkopar',
      distanceKm: 19.8,
      platforms: [
        { number: '01', occupancyPercent: 94, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
        { number: '02', occupancyPercent: 82, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
      ],
    },
    {
      code: 'TNA',
      name: 'Thane',
      distanceKm: 34.0,
      platforms: [
        { number: '01', occupancyPercent: 88, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
        { number: '05', occupancyPercent: 78, fobCongestion: 'MODERATE', crossoverSpeedKm: 45 },
      ],
    },
    {
      code: 'KYN',
      name: 'Kalyan Junction',
      distanceKm: 54.0,
      platforms: [
        { number: '04', occupancyPercent: 85, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
        { number: '05', occupancyPercent: 72, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
  ],
  'western-line': [
    {
      code: 'CCG',
      name: 'Churchgate',
      distanceKm: 0.0,
      platforms: [
        { number: '01', occupancyPercent: 62, fobCongestion: 'LOW', crossoverSpeedKm: 25 },
        { number: '03', occupancyPercent: 74, fobCongestion: 'MODERATE', crossoverSpeedKm: 30 },
      ],
    },
    {
      code: 'BCT',
      name: 'Mumbai Central',
      distanceKm: 4.8,
      platforms: [
        { number: '01', occupancyPercent: 70, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'DDR',
      name: 'Dadar Western',
      distanceKm: 10.2,
      platforms: [
        { number: '01', occupancyPercent: 92, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
        { number: '02', occupancyPercent: 89, fobCongestion: 'HIGH', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'BA',
      name: 'Bandra',
      distanceKm: 14.9,
      platforms: [
        { number: '03', occupancyPercent: 82, fobCongestion: 'HIGH', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'ADH',
      name: 'Andheri',
      distanceKm: 21.8,
      platforms: [
        { number: '01', occupancyPercent: 95, fobCongestion: 'CRITICAL', crossoverSpeedKm: 30 },
        { number: '08', occupancyPercent: 78, fobCongestion: 'MODERATE', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'BVI',
      name: 'Borivali',
      distanceKm: 34.2,
      platforms: [
        { number: '03', occupancyPercent: 86, fobCongestion: 'HIGH', crossoverSpeedKm: 40 },
        { number: '05', occupancyPercent: 75, fobCongestion: 'MODERATE', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'VR',
      name: 'Virar',
      distanceKm: 60.0,
      platforms: [
        { number: '01', occupancyPercent: 80, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
      ],
    },
  ],
  'harbour': [
    {
      code: 'CSMT',
      name: 'CSMT Harbour',
      distanceKm: 0.0,
      platforms: [
        { number: '01', occupancyPercent: 68, fobCongestion: 'LOW', crossoverSpeedKm: 25 },
        { number: '02', occupancyPercent: 72, fobCongestion: 'MODERATE', crossoverSpeedKm: 25 },
      ],
    },
    {
      code: 'VDLR',
      name: 'Wadala Road',
      distanceKm: 9.2,
      platforms: [
        { number: '01', occupancyPercent: 84, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
        { number: '03', occupancyPercent: 78, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'CLA',
      name: 'Kurla Harbour',
      distanceKm: 15.1,
      platforms: [
        { number: '07', occupancyPercent: 88, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
      ],
    },
    {
      code: 'CMBR',
      name: 'Chembur',
      distanceKm: 17.5,
      platforms: [
        { number: '01', occupancyPercent: 76, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'VSH',
      name: 'Vashi',
      distanceKm: 28.5,
      platforms: [
        { number: '02', occupancyPercent: 80, fobCongestion: 'HIGH', crossoverSpeedKm: 35 },
        { number: '03', occupancyPercent: 70, fobCongestion: 'MODERATE', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'NEU',
      name: 'Nerul',
      distanceKm: 36.2,
      platforms: [
        { number: '01', occupancyPercent: 75, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'PNVL',
      name: 'Panvel',
      distanceKm: 49.3,
      platforms: [
        { number: '01', occupancyPercent: 70, fobCongestion: 'LOW', crossoverSpeedKm: 30 },
      ],
    },
  ],
  'trans-harbour': [
    {
      code: 'TNA',
      name: 'Thane Trans-Harbour',
      distanceKm: 0.0,
      platforms: [
        { number: '09', occupancyPercent: 82, fobCongestion: 'HIGH', crossoverSpeedKm: 30 },
        { number: '10', occupancyPercent: 75, fobCongestion: 'MODERATE', crossoverSpeedKm: 30 },
      ],
    },
    {
      code: 'AIRL',
      name: 'Airoli',
      distanceKm: 6.0,
      platforms: [
        { number: '01', occupancyPercent: 72, fobCongestion: 'MODERATE', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'KOPR',
      name: 'Kopar Khairane',
      distanceKm: 12.0,
      platforms: [
        { number: '01', occupancyPercent: 65, fobCongestion: 'LOW', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'TUH',
      name: 'Turbhe APMC',
      distanceKm: 16.0,
      platforms: [
        { number: '01', occupancyPercent: 70, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'JNJ',
      name: 'Juinagar',
      distanceKm: 21.0,
      platforms: [
        { number: '02', occupancyPercent: 68, fobCongestion: 'LOW', crossoverSpeedKm: 40 },
      ],
    },
    {
      code: 'VSH',
      name: 'Vashi',
      distanceKm: 24.0,
      platforms: [
        { number: '03', occupancyPercent: 74, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
    {
      code: 'PNVL',
      name: 'Panvel',
      distanceKm: 36.5,
      platforms: [
        { number: '03', occupancyPercent: 70, fobCongestion: 'MODERATE', crossoverSpeedKm: 35 },
      ],
    },
  ],
};

/**
 * Get all available stations across all corridors
 */
export const ALL_MUMBAI_STATIONS: { code: string; name: string; line: string }[] = [
  // Central
  { code: 'CSMT', name: 'CSMT Terminus', line: 'Central Main' },
  { code: 'DR', name: 'Dadar Central', line: 'Central Main' },
  { code: 'CLA', name: 'Kurla Junction', line: 'Central Main' },
  { code: 'GC', name: 'Ghatkopar', line: 'Central Main' },
  { code: 'TNA', name: 'Thane', line: 'Central Main' },
  { code: 'KYN', name: 'Kalyan Junction', line: 'Central Main' },
  // Western
  { code: 'CCG', name: 'Churchgate', line: 'Western Line' },
  { code: 'BCT', name: 'Mumbai Central', line: 'Western Line' },
  { code: 'DDR', name: 'Dadar Western', line: 'Western Line' },
  { code: 'BA', name: 'Bandra', line: 'Western Line' },
  { code: 'ADH', name: 'Andheri', line: 'Western Line' },
  { code: 'BVI', name: 'Borivali', line: 'Western Line' },
  { code: 'VR', name: 'Virar', line: 'Western Line' },
  // Harbour
  { code: 'VDLR', name: 'Wadala Road', line: 'Harbour Line' },
  { code: 'CMBR', name: 'Chembur', line: 'Harbour Line' },
  { code: 'VSH', name: 'Vashi', line: 'Harbour Line' },
  { code: 'NEU', name: 'Nerul', line: 'Harbour Line' },
  { code: 'PNVL', name: 'Panvel', line: 'Harbour Line' },
  // Trans-Harbour
  { code: 'AIRL', name: 'Airoli', line: 'Trans-Harbour' },
  { code: 'KOPR', name: 'Kopar Khairane', line: 'Trans-Harbour' },
  { code: 'TUH', name: 'Turbhe', line: 'Trans-Harbour' },
  { code: 'JNJ', name: 'Juinagar', line: 'Trans-Harbour' },
];

function createCoachMatrix(_trainNumber: string, isAC: boolean): TrainRakeTelemetry['coachMatrix'] {
  const coaches: TrainRakeTelemetry['coachMatrix'] = [];
  for (let i = 1; i <= 12; i++) {
    let type: 'GENERAL' | 'FIRST_CLASS' | 'LADIES' | 'DIVYANG' | 'AC' = 'GENERAL';
    let crowd = 75;
    let fobText = `Aligns with Mid-Bridge FOB stairs`;
    let desc = `Standard suburban ingress & egress`;

    if (isAC) {
      type = 'AC';
      crowd = Math.floor(45 + (i * 3.5) % 25);
      fobText = `Medha plug-doors align with North Escalator`;
      desc = `Climate controlled at 21.5°C`;
    } else if (i === 4 || i === 9) {
      type = 'FIRST_CLASS';
      crowd = Math.floor(40 + (i * 5) % 20);
      fobText = `Direct alignment with main exit overbridge`;
      desc = `Fast egress for regular commuters`;
    } else if (i === 5 || i === 11) {
      type = 'LADIES';
      crowd = Math.floor(55 + (i * 4) % 18);
      fobText = `Guarded ladies compartment • Emergency intercom active`;
      desc = `Dedicated priority coach`;
    } else if (i === 6) {
      type = 'DIVYANG';
      crowd = 38;
      fobText = `Ramp access at platform central concourse`;
      desc = `Unimpeded wheelchair access`;
    } else {
      crowd = Math.floor(70 + (i * 7) % 22);
      if (i <= 3) {
        fobText = `Aligns with north end staircase`;
        desc = `High boarding flow`;
      } else {
        fobText = `Aligns with south subway passage`;
        desc = `Smooth exit flow`;
      }
    }

    coaches.push({
      coachNumber: i,
      coachType: type,
      crowdPercent: crowd,
      fobAlignmentText: fobText,
      description: desc,
    });
  }
  return coaches;
}

/**
 * Time Math Utilities for Timetable Engine
 */
export function parseTimeToMinutes(timeStr: string): number {
  const match = timeStr.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (!match) return 8 * 60 + 47;
  let hours = parseInt(match[1], 10);
  const minutes = parseInt(match[2], 10);
  const ampm = match[3].toUpperCase();
  if (ampm === 'PM' && hours < 12) hours += 12;
  if (ampm === 'AM' && hours === 12) hours = 0;
  return hours * 60 + minutes;
}

export function formatMinutesToTime(totalMinutes: number): string {
  const norm = ((totalMinutes % 1440) + 1440) % 1440;
  let hours = Math.floor(norm / 60);
  const minutes = norm % 60;
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  if (hours === 0) hours = 12;
  const hh = hours < 10 ? `0${hours}` : `${hours}`;
  const mm = minutes < 10 ? `0${minutes}` : `${minutes}`;
  return `${hh}:${mm} ${ampm}`;
}

export function addMinutesToTime(timeStr: string, minutesToAdd: number): string {
  const total = parseTimeToMinutes(timeStr) + minutesToAdd;
  return formatMinutesToTime(total);
}

/**
 * Extract stations between origin and destination along a corridor route
 */
export function getRouteStations(
  originCode: string,
  destinationCode: string,
  corridor: CorridorId = 'central-main'
): StationTelemetry[] {
  const corridorList = CORRIDOR_STATIONS[corridor] || CORRIDOR_STATIONS['central-main'];
  const orgIdx = corridorList.findIndex((s) => s.code === originCode);
  const dstIdx = corridorList.findIndex((s) => s.code === destinationCode);

  if (orgIdx !== -1 && dstIdx !== -1) {
    if (orgIdx <= dstIdx) {
      const sliced = corridorList.slice(orgIdx, dstIdx + 1);
      const baseDist = sliced[0].distanceKm;
      return sliced.map((s) => ({
        ...s,
        distanceKm: Math.abs(s.distanceKm - baseDist),
      }));
    } else {
      const sliced = corridorList.slice(dstIdx, orgIdx + 1).reverse();
      const baseDist = sliced[0].distanceKm;
      return sliced.map((s) => ({
        ...s,
        distanceKm: Math.abs(s.distanceKm - baseDist),
      }));
    }
  }

  // Cross-line or arbitrary station lookup
  const orgStation = ALL_MUMBAI_STATIONS.find((s) => s.code === originCode);
  const dstStation = ALL_MUMBAI_STATIONS.find((s) => s.code === destinationCode);

  if (orgStation && dstStation) {
    for (const key of Object.keys(CORRIDOR_STATIONS) as CorridorId[]) {
      const list = CORRIDOR_STATIONS[key];
      const i1 = list.findIndex((s) => s.code === originCode);
      const i2 = list.findIndex((s) => s.code === destinationCode);
      if (i1 !== -1 && i2 !== -1) {
        return getRouteStations(originCode, destinationCode, key);
      }
    }
  }

  return [
    {
      code: originCode,
      name: orgStation?.name || originCode,
      distanceKm: 0.0,
      platforms: [{ number: '02', occupancyPercent: 68, fobCongestion: 'LOW', crossoverSpeedKm: 30 }],
    },
    {
      code: destinationCode,
      name: dstStation?.name || destinationCode,
      distanceKm: 34.0,
      platforms: [{ number: '01', occupancyPercent: 78, fobCongestion: 'MODERATE', crossoverSpeedKm: 30 }],
    },
  ];
}

/**
 * Calculate station-by-station sequential arrival and departure timings
 */
export function calculateStationTimetable(
  stations: StationTelemetry[],
  startTimeStr: string,
  trainType: 'FAST' | 'SLOW' | 'AC_FAST' | 'LADIES_SPECIAL' = 'FAST'
): StationStopSchedule[] {
  if (!stations || stations.length === 0) return [];

  let currentMinutes = parseTimeToMinutes(startTimeStr);
  const isSlow = trainType === 'SLOW';
  const pacePerKm = isSlow ? 1.45 : 1.05;

  return stations.map((st, idx) => {
    const isFirst = idx === 0;
    const isLast = idx === stations.length - 1;

    let arrivalTime: string;
    let departureTime: string;
    let dwellSeconds = 0;

    if (isFirst) {
      arrivalTime = formatMinutesToTime(currentMinutes);
      departureTime = formatMinutesToTime(currentMinutes);
      dwellSeconds = 0;
    } else {
      const prevStation = stations[idx - 1];
      const distDelta = Math.max(1.5, Math.abs(st.distanceKm - prevStation.distanceKm));
      const transitMins = Math.max(isSlow ? 4 : 3, Math.round(distDelta * pacePerKm));
      currentMinutes += transitMins;
      arrivalTime = formatMinutesToTime(currentMinutes);

      if (isLast) {
        departureTime = arrivalTime;
        dwellSeconds = 0;
      } else {
        const dwellMins = 1;
        dwellSeconds = 45;
        currentMinutes += dwellMins;
        departureTime = formatMinutesToTime(currentMinutes);
      }
    }

    const platformNum = st.platforms?.[0]?.number || `0${(idx % 4) + 1}`;
    const fob = st.platforms?.[0]?.fobCongestion || (idx % 2 === 0 ? 'LOW' : 'MODERATE');

    return {
      stationCode: st.code,
      stationName: st.name,
      distanceKm: st.distanceKm,
      arrivalTime,
      departureTime,
      dwellSeconds,
      platform: `Plat ${platformNum}`,
      status: isFirst ? 'CURRENT' : 'UPCOMING',
      fobCongestion: fob,
    };
  });
}

/**
 * Fetch Corridor Real-Time Telemetry dynamically
 */
export async function fetchCorridorTelemetry(
  corridor: CorridorId = 'central-main',
  direction: Direction = 'DOWN'
): Promise<{
  corridor: CorridorId;
  direction: Direction;
  sectionTitle: string;
  activeRake: {
    trainNumber: string;
    speed: string;
    signal: string;
    headway: string;
  };
  stations: StationTelemetry[];
}> {
  const stations = CORRIDOR_STATIONS[corridor] || CORRIDOR_STATIONS['central-main'];
  const baseOrdered = direction === 'UP' ? [...stations].reverse() : [...stations];
  const originDist = baseOrdered[0]?.distanceKm || 0;
  const orderedStations = baseOrdered.map((s) => ({
    ...s,
    distanceKm: Math.abs(s.distanceKm - originDist),
  }));

  const timetable = calculateStationTimetable(orderedStations, '08:47 AM', 'FAST');
  const enrichedStations: StationTelemetry[] = orderedStations.map((st, idx) => ({
    ...st,
    arrivalTime: timetable[idx]?.arrivalTime,
    departureTime: timetable[idx]?.departureTime,
    platform: timetable[idx]?.platform,
    dwellSeconds: timetable[idx]?.dwellSeconds,
    status: timetable[idx]?.status,
  }));

  const baseSpeed = corridor === 'western-line' ? 95 : corridor === 'harbour' ? 85 : 92;
  const liveSpeed = Math.max(68, baseSpeed + jitterSpeedOffset);

  const prefix =
    corridor === 'western-line'
      ? '#90125 FAST'
      : corridor === 'harbour'
      ? '#97021 LOCAL'
      : corridor === 'trans-harbour'
      ? '#99101 LOCAL'
      : '#95401 FAST';

  const firstCode = enrichedStations[0]?.code || 'ORG';
  const lastCode = enrichedStations[enrichedStations.length - 1]?.code || 'DST';

  return {
    corridor,
    direction,
    sectionTitle:
      direction === 'DOWN'
        ? `Section: ${firstCode} → ${lastCode} (${corridor.toUpperCase().replace('-', ' ')})`
        : `Section: ${firstCode} → ${lastCode} (${corridor.toUpperCase().replace('-', ' ')} UP)`,
    activeRake: {
      trainNumber: prefix,
      speed: `${liveSpeed} km/h`,
      signal: 'Sig Clear (Proceed Aspect)',
      headway: 'Headway 3m 40s',
    },
    stations: enrichedStations,
  };
}

/**
 * Fetch Upcoming Train Schedules dynamically for any Origin and Destination
 */
export async function fetchTrainSchedule(
  origin: string = 'CSMT',
  destination: string = 'KYN',
  corridor: CorridorId = 'central-main'
): Promise<TrainRakeTelemetry[]> {
  const routeStations = getRouteStations(origin, destination, corridor);
  const orgName = routeStations[0]?.name || origin;
  const dstName = routeStations[routeStations.length - 1]?.name || destination;
  const totalDistance = routeStations[routeStations.length - 1]?.distanceKm || 45;

  const isWestern = corridor === 'western-line';
  const isHarbour = corridor === 'harbour';
  const isTransHarbour = corridor === 'trans-harbour';

  const p1 = isWestern ? '#90125 FAST' : isHarbour ? '#97021 LOCAL' : isTransHarbour ? '#99101 LOCAL' : '#95401 FAST';
  const p2 = isWestern ? '#90103 SLOW' : isHarbour ? '#97003 LOCAL' : isTransHarbour ? '#99103 LOCAL' : '#95201 SLOW';
  const p3 = isWestern ? '#90201 AC FAST' : isHarbour ? '#97045 AC' : isTransHarbour ? '#99105 AC' : '#95403 AC FAST';

  // Rake 1: FAST / EXPRESS
  const stops1 = calculateStationTimetable(routeStations, '08:47 AM', 'FAST');
  const dep1 = stops1[0]?.departureTime || '08:47 AM';
  const arr1 = stops1[stops1.length - 1]?.arrivalTime || '09:23 AM';
  const dur1 = Math.max(15, parseTimeToMinutes(arr1) - parseTimeToMinutes(dep1));

  // Rake 2: SLOW / ALL STATIONS LOCAL (Starts 09:08 AM)
  const stops2 = calculateStationTimetable(routeStations, '09:08 AM', 'SLOW');
  const dep2 = stops2[0]?.departureTime || '09:08 AM';
  const arr2 = stops2[stops2.length - 1]?.arrivalTime || '10:07 AM';
  const dur2 = Math.max(25, parseTimeToMinutes(arr2) - parseTimeToMinutes(dep2));

  // Rake 3: AC FAST (Starts 09:15 AM)
  const stops3 = calculateStationTimetable(routeStations, '09:15 AM', 'AC_FAST');
  const dep3 = stops3[0]?.departureTime || '09:15 AM';
  const arr3 = stops3[stops3.length - 1]?.arrivalTime || '09:51 AM';
  const dur3 = Math.max(15, parseTimeToMinutes(arr3) - parseTimeToMinutes(dep3));

  const rakes: TrainRakeTelemetry[] = [
    {
      id: '95401',
      trainNumber: p1,
      trainType: 'FAST',
      lineCode: isWestern ? 'WR' : isHarbour ? 'HR' : isTransHarbour ? 'TR' : 'CR',
      originCode: origin,
      originName: orgName,
      destinationCode: destination,
      destinationName: dstName,
      departureTime: dep1,
      arrivalTime: arr1,
      durationMins: dur1,
      stopsCount: routeStations.length,
      viaDescription: `Direct Express Path: ${origin} → ${destination} (${totalDistance.toFixed(1)} km)`,
      currentSpeedKm: 92 + jitterSpeedOffset,
      signalAspect: 'Sig Clear',
      headwayText: 'Headway 3m 40s',
      platform: stops1[0]?.platform || `Plat 02 (${origin})`,
      totalLoadPercent: 78,
      status: 'ON_TIME',
      delayMinutes: 0,
      coachMatrix: createCoachMatrix('95401', false),
      stops: stops1,
      targetDeltaMins: 12,
      arrivalBufferText: '+12m Punctual Arrival Buffer',
    },
    {
      id: '95201',
      trainNumber: p2,
      trainType: 'SLOW',
      lineCode: isWestern ? 'WR' : isHarbour ? 'HR' : isTransHarbour ? 'TR' : 'CR',
      originCode: origin,
      originName: orgName,
      destinationCode: destination,
      destinationName: dstName,
      departureTime: dep2,
      arrivalTime: arr2,
      durationMins: dur2,
      stopsCount: routeStations.length,
      viaDescription: `All Stations Local: ${origin} → ${destination}`,
      currentSpeedKm: 48,
      signalAspect: 'Caution (Double Amber)',
      headwayText: 'Hold-up Junction',
      platform: stops2[0]?.platform || `Plat 01 (${origin})`,
      totalLoadPercent: 91,
      status: 'DELAYED',
      delayMinutes: 6,
      coachMatrix: createCoachMatrix('95201', false),
      stops: stops2,
      targetDeltaMins: -37,
      arrivalBufferText: 'Delayed +6m • High Dwell Time',
    },
    {
      id: '95403',
      trainNumber: p3,
      trainType: 'AC_FAST',
      lineCode: isWestern ? 'WR' : isHarbour ? 'HR' : isTransHarbour ? 'TR' : 'CR',
      originCode: origin,
      originName: orgName,
      destinationCode: destination,
      destinationName: dstName,
      departureTime: dep3,
      arrivalTime: arr3,
      durationMins: dur3,
      stopsCount: routeStations.length,
      viaDescription: 'Medha Automatic AC EMU • High Comfort',
      currentSpeedKm: 88,
      signalAspect: 'Sig Clear',
      headwayText: 'Headway 4m 10s',
      platform: stops3[0]?.platform || `Plat 03 (${origin})`,
      totalLoadPercent: 54,
      status: 'ON_TIME',
      delayMinutes: 0,
      coachMatrix: createCoachMatrix('95403', true),
      stops: stops3,
      temperatureC: 21.0,
      targetDeltaMins: 8,
      arrivalBufferText: 'On Schedule • Climate Controlled',
    },
  ];

  return rakes;
}

/**
 * Calculate Commute & Attendance Risk
 */
export async function calculateAttendanceRisk(
  studentId: string = 'COMMUTER_98401',
  selectedTrainId: string = '95401',
  lectureTime: string = '09:30 AM'
): Promise<AttendanceRiskResult> {
  const isDelayedTrain = selectedTrainId === '95201';

  if (isDelayedTrain) {
    return {
      studentId,
      studentName: 'Commuter Aditya',
      college: 'Mumbai Suburban Network',
      currentPercentage: 75.4,
      simulatedPercentage: 74.3,
      minRequiredPercentage: 75.0,
      status: 'DEBARMENT_RISK',
      selectedTrainNumber: '#95201 SLOW',
      etaDadar: '10:07 AM',
      lectureStartTime: lectureTime,
      bufferMinutes: -37,
      walkMinutes: 7,
      willReachOnTime: false,
      contingencyProtocol: 'ISSUE_CR_DELAY_TOKEN',
    };
  }

  return {
    studentId,
    studentName: 'Commuter Aditya',
    college: 'Mumbai Suburban Network',
    currentPercentage: 75.4,
    simulatedPercentage: 75.4,
    minRequiredPercentage: 75.0,
    status: 'SAFE',
    selectedTrainNumber: '#95401 FAST',
    etaDadar: '09:23 AM',
    lectureStartTime: lectureTime,
    bufferMinutes: 12,
    walkMinutes: 7,
    willReachOnTime: true,
    contingencyProtocol: 'SPRINT_MATUNGA_WALK',
  };
}

/**
 * Generate Official Central Railway Delay Token
 */
export async function generateDelayToken(
  studentData: {
    name: string;
    rollNumber: string;
    college: string;
    hodEmail?: string;
  },
  trainData: {
    trainNumber: string;
    corridor: string;
    delayMinutes: number;
    failurePoint: string;
  }
): Promise<DelayTokenPayload> {
  const tokenUuid = `CR-TMS-${Date.now().toString().slice(-6)}`;
  const now = new Date();
  const validUntil = new Date(now.getTime() + 24 * 60 * 60 * 1000);

  return {
    tokenUuid,
    verificationSha256: '9A8B7C6D5E4F3A2B1C0D9E8F7A6B5C4D',
    studentName: studentData.name,
    rollNumber: studentData.rollNumber,
    collegeName: studentData.college,
    trainRakeId: trainData.trainNumber,
    lineCorridor: trainData.corridor,
    delayMinutes: trainData.delayMinutes,
    incidentLocation: 'Track Circuit Drop & Signal Hold-up',
    tmsSignalFailurePoint: trainData.failurePoint || 'Sig Track Circuit Fault',
    motormanRemarks: 'Delayed due to precedence given to express movement.',
    issuedAt: now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    validUntil: validUntil.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }),
    hodEmail: studentData.hodEmail || 'commuter.support@transitpulse.app',
    digitalSignature: `CR/MUM/TMS/SIG/2026/${tokenUuid.slice(-6)}`,
    verificationUrl: `https://transitpulse.app/verify/delay/${tokenUuid}`,
  };
}
