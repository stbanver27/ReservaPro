/* dashboard.js */

window.addEventListener('DOMContentLoaded', async () => {
  requireAuth();
  await loadUserDisplay();

  // Fecha en header
  const dateEl = document.getElementById('header-date');
  if (dateEl) {
    dateEl.textContent = new Date().toLocaleDateString('es-CL', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  // Nombre del negocio
  try {
    const biz = await apiFetch('/api/business');
    const h = document.getElementById('business-name-header');
    if (h) h.textContent = biz.name;
  } catch {}

  await loadDashboardData();
});

async function loadDashboardData() {
  try {
    const all = await apiFetch('/api/appointments');

    const now = new Date();
    const today = now.toISOString().split('T')[0];

    const pending   = all.filter(a => a.status === 'pending');
    const todayConf = all.filter(a => a.status === 'confirmed' && a.start_datetime.startsWith(today));

    const thisMonth = all.filter(a => {
      const d = new Date(a.start_datetime);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    });
    const completed = thisMonth.filter(a => a.status === 'completed');
    const revenue   = thisMonth
      .filter(a => a.status === 'completed')
      .reduce((sum, a) => sum + (a.price_charged || 0), 0);

    setText('kpi-pending',   pending.length);
    setText('kpi-confirmed', todayConf.length);
    setText('kpi-completed', completed.length);
    setText('kpi-revenue',   `$${revenue.toLocaleString('es-CL')}`);

    // Próximas reservas (confirmadas o pendientes, futuras)
    const upcoming = all
      .filter(a => ['confirmed','pending'].includes(a.status) && new Date(a.start_datetime) >= now)
      .sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))
      .slice(0, 10);

    renderUpcoming(upcoming);

  } catch (e) {
    console.error('Error cargando dashboard:', e);
  }
}

function renderUpcoming(items) {
  const el = document.getElementById('upcoming-list');
  if (!el) return;

  if (!items.length) {
    el.innerHTML = '<p class="loading">No hay reservas próximas.</p>';
    return;
  }

  el.innerHTML = items.map(a => {
    const dt = new Date(a.start_datetime);
    const date = dt.toLocaleDateString('es-CL', { weekday: 'short', month: 'short', day: 'numeric' });
    const time = dt.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
    return `
      <div class="appt-item">
        <div class="appt-time">${date}<br><strong>${time}</strong></div>
        <div class="appt-client">${a.client?.name || '—'}</div>
        <div class="appt-service">${a.service?.name || '—'}</div>
        <div class="appt-prof">${a.professional?.name || '—'}</div>
        <span class="badge badge-${a.status}">${statusLabel(a.status)}</span>
      </div>
    `;
  }).join('');
}

function statusLabel(s) {
  return { pending: 'Pendiente', confirmed: 'Confirmada', completed: 'Completada', cancelled: 'Cancelada' }[s] || s;
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
