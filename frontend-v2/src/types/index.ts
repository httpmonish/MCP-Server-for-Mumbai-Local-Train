export interface AttendanceRecord {
  id?: string;
  subject_name: string;
  total_conducted: number;
  total_attended: number;
  percentage: number;
  last_synced_at?: string;
}

export interface AttendanceResponse {
  data: AttendanceRecord[];
  source: "live" | "cache" | "database";
  stale: boolean;
  last_synced_at?: string;
}

export interface ExamSchedule {
  id?: string;
  subject_name: string;
  exam_date: string;
  time_slot: string;
  classroom: string | null;
}

export interface ExamResponse {
  data: ExamSchedule[];
  source: "live" | "cache" | "database";
  stale: boolean;
}

export interface TrainStop {
  station_code: string;
  station_name: string;
  time: string;
  seq: number;
}

export type SuburbanLineCode = "CR" | "WR" | "HR" | "ALL";

export interface TrainRecord {
  train_number: string;
  line: "CR" | "WR" | "HR";
  line_name?: string;
  train_type: "SLOW" | "FAST" | "AC FAST" | "AC SLOW" | string;
  departure_from_source: string;
  arrival_at_destination: string;
  travel_time_minutes: number;
  platform?: string;
  crowd_level?: "Low" | "Moderate" | "Heavy Rush" | "Normal" | string;
  source_terminal?: string;
  dest_terminal?: string;
}

export interface TrainQueryResponse {
  source: string;
  destination: string;
  line?: string;
  queried_at: string;
  count: number;
  trains: TrainRecord[];
}

export interface LineInfo {
  code: "CR" | "WR" | "HR";
  name: string;
  color: string;
  accent: string;
  description: string;
  status: string;
  punctuality: string;
  avg_headway_mins: number;
  station_count: number;
  start_station: string;
  end_station: string;
}

export interface StationItem {
  code: string;
  name: string;
  fast?: boolean;
  junction?: boolean;
  metro?: boolean;
  interchange?: string[];
  line?: string;
  line_name?: string;
}

export interface NetworkHealth {
  status: string;
  updated_at: string;
  lines: Record<string, {
    name: string;
    status: string;
    punctuality: string;
    delay_avg: string;
    active_rakes: number;
  }>;
}

export interface ApiErrorResponse {
  error: string;
  detail: string;
  stale?: boolean;
}

export interface CollegeInfo {
  id: string;
  name: string;
  shortCode: string;
  location: string;
  nearestStation: string;
  defaultLine: SuburbanLineCode;
  portalUrl: string;
  campusCode: string;
}

export interface DemoStudentProfile {
  id: string;
  name: string;
  rollNo: string;
  collegeId: string;
  department: string;
  standingCategory: "borderline" | "critical" | "safe";
  homeStation: string;
  attendanceData: AttendanceRecord[];
}

export interface AttendanceAnalytics {
  totalConducted: number;
  totalAttended: number;
  percentage: number;
  isAbove75: boolean;
  deficitPct: number;
  lecturesNeededTo75: number;
  safeBunkBuffer: number;
}

