/* ═══════════════════════════════════════════
   auth.js — Gestión de JWT y helpers globales
   ═══════════════════════════════════════════ */

const TOKEN_KEY = 'rp_token';
const USER_KEY  = 'rp_user';

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function getUser()  { try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; } }

function saveSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/login';
    throw new Error('No autenticado');
  }
}

function logout() {
  clearSession();
  window.location.href = '/login';
}

/**
 * apiFetch — wrapper sobre fetch con JWT automático.
 * Lanza un Error con el mensaje del servidor si la respuesta no es ok.
 */
async function apiFetch(url, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(url, { ...options, headers });

  if (res.status === 401) {
    clearSession();
    window.location.href = '/login';
    throw new Error('Sesión expirada');
  }

  if (!res.ok) {
    let msg = `Error ${res.status}`;
    try {
      const data = await res.json();
      msg = data.detail || JSON.stringify(data);
    } catch {}
    throw new Error(msg);
  }

  // 204 No Content
  if (res.status === 204) return null;

  return res.json();
}

/* ── Login ──────────────────────────────────── */
async function doLogin() {
  const email    = document.getElementById('email')?.value?.trim();
  const password = document.getElementById('password')?.value;
  const errorEl  = document.getElementById('login-error');
  const btn      = document.getElementById('login-btn');

  if (!email || !password) {
    showLoginError('Completa todos los campos');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Ingresando...';

  try {
    const data = await apiFetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // Guardar token antes de llamar /me para que apiFetch lo incluya
    localStorage.setItem(TOKEN_KEY, data.access_token);

    const user = await apiFetch('/api/auth/me');

    saveSession(data.access_token, user);
    window.location.href = '/dashboard';

  } catch (e) {
    showLoginError(e.message || 'Credenciales incorrectas');
    btn.disabled = false;
    btn.textContent = 'Iniciar sesión';
  }
}

function showLoginError(msg) {
  const el = document.getElementById('login-error');
  if (el) {
    el.textContent = msg;
    el.style.display = 'block';
    el.className = 'alert alert-error';
  }
}

/* ── Load user display name in sidebar ─────── */
async function loadUserDisplay() {
  const user = getUser();
  const el = document.getElementById('user-name-display');
  if (el && user) el.textContent = user.name;
}

/* ── Allow Enter key on login ───────────────── */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && document.getElementById('login-btn')) doLogin();
});

/* ── Auto-redirect if already logged in ─────── */
if (window.location.pathname === '/login' && getToken()) {
  window.location.href = '/dashboard';
}
