import { CONFIG } from './config.js';
import {
    getStoredStudentId, setStoredStudentId,
    getStoredCredentials, setStoredCredentials,
    getStoredRoute, setStoredRoute
} from './storage.js';
import {
    apiGetAttendance, apiGetExams,
    apiGetNextTrains, apiCheckHealth
} from './api.js';

const state = {
  studentId: "",
  username: "",
  password: "",
  fromStation: "",
  toStation: "",
  trainRefreshTimer: null,
  countdownSeconds: 60
};

// DOM Elements
const elements = {
  statusDot: document.getElementById('status-indicator'),
  btnSyncAll: document.getElementById('btn-sync-all'),
  syncSpinner: document.getElementById('sync-spinner'),
  staleAlert: document.getElementById('stale-alert'),
  staleText: document.getElementById('stale-text'),
  errorAlert: document.getElementById('error-alert'),
  errorText: document.getElementById('error-text'),
  formCredentials: document.getElementById('form-credentials'),
  inputStudentId: document.getElementById('input-student-id'),
  inputUsername: document.getElementById('input-username'),
  inputPassword: document.getElementById('input-password'),
  attendanceOverallPct: document.getElementById('attendance-overall-pct'),
  attendanceStatusBadge: document.getElementById('attendance-status-badge'),
  attendanceSkeleton: document.getElementById('attendance-skeleton'),
  attendanceTableBody: document.querySelector('#attendance-table tbody'),
  attendanceTableContainer: document.getElementById('attendance-table-container'),
  examsSkeleton: document.getElementById('exams-skeleton'),
  examsList: document.getElementById('exams-list'),
  examsEmpty: document.getElementById('exams-empty'),
  examCountBadge: document.getElementById('exam-count-badge'),
  selectFromStation: document.getElementById('select-from-station'),
  selectToStation: document.getElementById('select-to-station'),
  btnSwapStations: document.getElementById('btn-swap-stations'),
  trainsSkeleton: document.getElementById('trains-skeleton'),
  trainsList: document.getElementById('trains-list'),
  trainCountdown: document.getElementById('train-countdown'),
};

const STATIONS = [
  // Central Line (CR)
  "CSMT", "Byculla", "Dadar", "Kurla", "Ghatkopar", "Thane", "Dombivli", "Kalyan", "Titwala", "Asangaon", "Kasara",
  // Western Line (WR)
  "Churchgate", "Mumbai Central", "Bandra", "Andheri", "Goregaon", "Borivali", "Bhayandar", "Virar",
  // Harbour Line (HR)
  "Sandhurst Road", "Vadala Road", "Vashi", "Nerul", "Belapur", "Kharghar", "Panvel"
];


async function init() {
  // 1. Restore storage
  state.studentId = getStoredStudentId() || "";
  const creds = getStoredCredentials();
  state.username = creds.username || "";
  state.password = creds.password || "";
  const route = getStoredRoute();
  state.fromStation = route.fromStation || CONFIG.DEFAULT_FROM_STATION;
  state.toStation = route.toStation || CONFIG.DEFAULT_TO_STATION;

  // Populate Inputs
  elements.inputStudentId.value = state.studentId;
  elements.inputUsername.value = state.username;
  elements.inputPassword.value = state.password;

  // Populate Station Dropdowns
  STATIONS.forEach(stn => {
    const optFrom = new Option(stn, stn);
    const optTo = new Option(stn, stn);
    elements.selectFromStation.add(optFrom);
    elements.selectToStation.add(optTo);
  });
  elements.selectFromStation.value = state.fromStation;
  elements.selectToStation.value = state.toStation;

  // Event Listeners
  elements.formCredentials.addEventListener('submit', async (e) => {
    e.preventDefault();
    state.studentId = elements.inputStudentId.value;
    state.username = elements.inputUsername.value;
    state.password = elements.inputPassword.value;
    setStoredStudentId(state.studentId);
    setStoredCredentials(state.username, state.password);
    await syncAll();
  });

  elements.selectFromStation.addEventListener('change', (e) => {
    state.fromStation = e.target.value;
    setStoredRoute(state.fromStation, state.toStation);
    loadTrainData();
  });

  elements.selectToStation.addEventListener('change', (e) => {
    state.toStation = e.target.value;
    setStoredRoute(state.fromStation, state.toStation);
    loadTrainData();
  });

  elements.btnSwapStations.addEventListener('click', () => {
    const temp = state.fromStation;
    state.fromStation = state.toStation;
    state.toStation = temp;
    elements.selectFromStation.value = state.fromStation;
    elements.selectToStation.value = state.toStation;
    setStoredRoute(state.fromStation, state.toStation);
    loadTrainData();
  });

  elements.btnSyncAll.addEventListener('click', syncAll);

  // Health Check
  try {
    await apiCheckHealth();
    elements.statusDot.className = "w-3 h-3 rounded-full bg-emerald-500";
  } catch {
    elements.statusDot.className = "w-3 h-3 rounded-full bg-rose-500";
  }

  // Polling
  startTrainPolling();

  // Initial Load
  if (state.studentId && state.username && state.password) {
    loadAcademicData();
  }
  loadTrainData();
}

async function syncAll() {
  elements.syncSpinner.classList.remove('hidden');
  elements.errorAlert.classList.add('hidden');
  try {
    await Promise.all([loadAcademicData(), loadTrainData()]);
  } catch (e) {
    showError(e.message);
  } finally {
    elements.syncSpinner.classList.add('hidden');
  }
}

async function loadAcademicData() {
  setLoadingState('attendance', true);
  setLoadingState('exams', true);

  try {
    const [attData, examData] = await Promise.all([
      apiGetAttendance(state.studentId, { username: state.username, password: state.password }),
      apiGetExams(state.studentId, { username: state.username, password: state.password })
    ]);

    renderAttendance(attData);
    renderExams(examData);
  } catch (e) {
    showError(e.message);
  } finally {
    setLoadingState('attendance', false);
    setLoadingState('exams', false);
  }
}

async function loadTrainData() {
  setLoadingState('trains', true);
  try {
    const data = await apiGetNextTrains(state.fromStation, state.toStation);
    renderTrains(data.data);
  } catch (e) {
    showError(e.message);
  } finally {
    setLoadingState('trains', false);
  }
}

function renderAttendance(data) {
  const records = data.data;
  const isStale = data.stale;
  const timestamp = data.last_synced_at;

  if (isStale) {
    elements.staleAlert.classList.remove('hidden');
    elements.staleText.innerText = `⚠️ Showing cached records from ${timestamp}. Upstream portal is currently unreachable.`;
  } else {
    elements.staleAlert.classList.add('hidden');
  }

  let totalCond = 0, totalAtt = 0;
  elements.attendanceTableBody.innerHTML = "";

  records.forEach(rec => {
    totalCond += rec.total_conducted;
    totalAtt += rec.total_attended;
    const perc = rec.percentage;
    const status = perc >= 75 ?
      '<span class="text-emerald-600 font-bold">GOOD</span>' :
      '<span class="text-rose-600 font-bold">CRITICAL WARNING (<75%)</span>';

    elements.attendanceTableBody.innerHTML += `
      <tr class="hover:bg-slate-50 transition-colors">
        <td class="py-3 font-medium">${rec.subject_name}</td>
        <td class="py-3 text-center">${rec.total_attended}/${rec.total_conducted}</td>
        <td class="py-3 text-center font-mono">${perc}%</td>
        <td class="py-3 text-right">${status}</td>
      </tr>
    `;
  });

  const overall = totalCond > 0 ? (totalAtt / totalCond * 100).toFixed(1) : "0.0";
  elements.attendanceOverallPct.innerText = `${overall}%`;
  elements.attendanceStatusBadge.innerText = overall >= 75 ? "Good Standing" : "Critical Warning";
  elements.attendanceStatusBadge.className = `px-2 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${overall >= 75 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`;
}

function renderExams(data) {
  const exams = data.data;
  elements.examCountBadge.innerText = exams.length;
  elements.examsList.innerHTML = "";

  if (exams.length === 0) {
    elements.examsEmpty.classList.remove('hidden');
    return;
  }
  elements.examsEmpty.classList.add('hidden');

  exams.sort((a, b) => a.exam_date.localeCompare(b.exam_date)).forEach(exam => {
    elements.examsList.innerHTML += `
      <div class="p-3 bg-slate-50 border border-slate-100 rounded-lg hover:border-indigo-200 transition-all">
        <h3 class="font-bold text-slate-800">${exam.subject_name}</h3>
        <div class="flex flex-wrap gap-2 mt-2">
          <span class="text-xs bg-white px-2 py-1 rounded border border-slate-200 text-slate-600">📅 ${exam.exam_date}</span>
          <span class="text-xs bg-indigo-50 px-2 py-1 rounded border border-indigo-100 text-indigo-700 font-medium">🕒 ${exam.time_slot}</span>
          <span class="text-xs bg-white px-2 py-1 rounded border border-slate-200 text-slate-600">📍 ${exam.classroom || 'TBD'}</span>
        </div>
      </div>
    `;
  });
}

function renderTrains(trains) {
  elements.trainsList.innerHTML = "";
  if (trains.length === 0) {
    elements.trainsList.innerHTML = `<div class="text-center py-8 text-slate-400 italic text-sm">No upcoming trains scheduled for this corridor.</div>`;
    return;
  }

  trains.forEach(t => {
    const now = new Date();
    const depTime = datetimeFromStr(t.departure_from_source);
    const diffMins = Math.round((depTime - now) / 60000);
    const countdownText = diffMins <= 0 ? "Departed" : `Departing in ${diffMins} mins`;

    const typeColor = t.train_type === 'FAST' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700';

    const lineBg = t.line === 'WR' ? 'bg-blue-600 text-white' : (t.line === 'HR' ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white');

    elements.trainsList.innerHTML += `
      <div class="p-3 bg-slate-50 border border-slate-100 rounded-lg flex justify-between items-center hover:bg-white transition-all shadow-sm">
        <div class="flex flex-col">
          <span class="text-xs font-bold text-slate-500">#${t.train_number}</span>
          <div class="flex gap-1 mt-1">
            <span class="text-[10px] font-black px-1.5 py-0.5 rounded ${lineBg}">${t.line}</span>
            <span class="text-[10px] font-black px-1.5 py-0.5 rounded ${typeColor}">${t.train_type}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="text-sm font-bold text-slate-800">${t.departure_from_source} → ${t.arrival_at_destination}</div>
          <div class="text-[10px] font-medium text-indigo-600 uppercase tracking-tighter">${countdownText} • ${t.travel_time_minutes}m</div>
        </div>
      </div>
    `;

  });
}

function datetimeFromStr(timeStr) {
  const [h, m, s = 0] = timeStr.split(':').map(Number);
  const d = new Date();
  d.setHours(h, m, s, 0);
  return d;
}

function setLoadingState(card, isLoading) {
  const skeletonId = `${card}-skeleton`;
  const containerId = `${card}-table-container` || `${card}-list`; // simplified

  const skeleton = document.getElementById(skeletonId);
  const container = document.getElementById(containerId) || document.getElementById(card === 'exams' ? 'exams-list' : (card === 'trains' ? 'trains-list' : 'attendance-table-container'));

  if (isLoading) {
    skeleton.classList.remove('hidden');
    container.classList.add('hidden');
  } else {
    skeleton.classList.add('hidden');
    container.classList.remove('hidden');
  }
}

function showError(msg) {
  elements.errorText.innerText = msg;
  elements.errorAlert.classList.remove('hidden');
}

function startTrainPolling() {
  state.countdownSeconds = 60;
  state.trainRefreshTimer = setInterval(() => {
    state.countdownSeconds--;
    elements.trainCountdown.innerText = `Auto-refreshing in ${state.countdownSeconds}s`;
    if (state.countdownSeconds <= 0) {
      state.countdownSeconds = 60;
      loadTrainData();
    }
  }, 1000);
}

window.addEventListener('DOMContentLoaded', init);
