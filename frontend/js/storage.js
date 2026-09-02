const KEY_STUDENT_ID = "campus_student_id";
const KEY_PORTAL_USER = "campus_portal_user";
const KEY_FROM_STN = "commute_from_station";
const KEY_TO_STN = "commute_to_station";

export function getStoredStudentId() {
  return localStorage.getItem(KEY_STUDENT_ID);
}

export function setStoredStudentId(id) {
  localStorage.setItem(KEY_STUDENT_ID, id);
}

export function getStoredCredentials() {
  return {
    username: sessionStorage.getItem(KEY_PORTAL_USER),
    password: sessionStorage.getItem("campus_portal_password"),
  };
}

export function setStoredCredentials(username, password) {
  sessionStorage.setItem(KEY_PORTAL_USER, username);
  sessionStorage.setItem("campus_portal_password", password);
}

export function getStoredRoute() {
  return {
    fromStation: localStorage.getItem(KEY_FROM_STN),
    toStation: localStorage.getItem(KEY_TO_STN),
  };
}

export function setStoredRoute(fromStn, toStn) {
  localStorage.setItem(KEY_FROM_STN, fromStn);
  localStorage.setItem(KEY_TO_STN, toStn);
}
