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

export interface TrainRecord {
  train_number: string;
  line: "CR" | "WR";
  train_type: "SLOW" | "FAST";
  departure_from_source: string;
  arrival_at_destination: string;
  travel_time_minutes: number;
}

export interface TrainQueryResponse {
  source: string;
  destination: string;
  queried_at: string;
  count: number;
  trains: TrainRecord[];
}

export interface ApiErrorResponse {
  error: string;
  detail: string;
  stale?: boolean;
}
