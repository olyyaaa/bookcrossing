const API = 'http://127.0.0.1:8000/api/v1';

function getToken() {
  return localStorage.getItem('token');
}

function setToken(token) {
  localStorage.setItem('token', token);
}

function removeToken() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

function getUser() {
  const u = localStorage.getItem('user');
  return u ? JSON.parse(u) : null;
}

function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

function isLoggedIn() {
  return !!getToken();
}

async function apiRequest(method, endpoint, body = null, auth = true) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(API + endpoint, options);

  if (res.status === 401) {
    removeToken();
    window.location.href = '/login';
    return;
  }
  return res;
}

async function apiGet(endpoint, auth = true) {
  return apiRequest('GET', endpoint, null, auth);
}

async function apiPost(endpoint, body, auth = true) {
  return apiRequest('POST', endpoint, body, auth);
}

async function apiPut(endpoint, body) {
  return apiRequest('PUT', endpoint, body);
}

async function apiPatch(endpoint, body = null) {
  return apiRequest('PATCH', endpoint, body);
}

async function apiDelete(endpoint) {
  return apiRequest('DELETE', endpoint);
}

function updateNavbar() {
  const navAuth = document.getElementById('nav-auth');
  const navUser = document.getElementById('nav-user');
  if (!navAuth || !navUser) return;

  if (isLoggedIn()) {
    const user = getUser();
    navAuth.style.display = 'none';
    navUser.style.display = 'flex';
    const nameEl = document.getElementById('nav-username');
    if (nameEl && user) nameEl.textContent = user.name;
    loadNotifCount();
  } else {
    navAuth.style.display = 'flex';
    navUser.style.display = 'none';
  }
}

async function loadNotifCount() {
  if (!isLoggedIn()) return;
  try {
    const res = await apiGet('/notifications/');
    if (res && res.ok) {
      const data = await res.json();
      const unread = data.filter(n => !n.is_read).length;
      const badge = document.getElementById('notif-badge');
      if (badge) {
        badge.textContent = unread;
        badge.style.display = unread > 0 ? 'inline-flex' : 'none';
      }
    }
  } catch (e) {}
}

function showAlert(containerId, message, type = 'danger') {
  const el = document.getElementById(containerId);
  if (el) {
    el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => { el.innerHTML = ''; }, 4000);
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function getStatusBadge(status) {
  const map = {
    available: '<span class="badge badge-success">Доступна</span>',
    reserved:  '<span class="badge badge-warning">Зарезервована</span>',
    exchanged: '<span class="badge badge-secondary">Обміняна</span>',
    pending:   '<span class="badge badge-warning">Очікує</span>',
    approved:  '<span class="badge badge-success">Схвалено</span>',
    rejected:  '<span class="badge badge-secondary">Відхилено</span>',
    completed: '<span class="badge badge-success">Завершено</span>',
  };
  return map[status] || status;
}