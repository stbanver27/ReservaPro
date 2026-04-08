/* appointments.js */

let allAppointments = [];
let editingApptId   = null;

const STATUS_LABELS = {
  pending:   'Pendiente',
  confirmed: 'Confirmada',
  completed: 'Completada',
  cancelled: 'Cancelada',
};

window.addEventListener('DOMContentLoaded', async () => {
  requireAuth();
  await loadUserDisplay();
  await Promise.all([loadSelects(), loadAppointments()]);
});

/* ── Selects para el modal nuevo ─────────────── */
async function loadSelects() {
  try {
    const [clients, services, profs] = await Promise.all([
      apiFetch('/api/clients'),
      apiFetch('/api/services'),
      apiFetch('/api/professionals'),
    ]);

    fillSelect('f-client', clients, c => ({ value: c.id, label: c.name + (c.phone ? ` (${c.phone})` : '') }));
    fillSelect('f-service', services.filter(s => s.is_active), s => ({ value: s.id, label: `${s.name} (${s.duration_minutes} min)` }));
    fillSelect('f-professional', profs.filter(p => p.is_active), p => ({ value: p.id, label: p.name }));

    // Fecha mínima = hoy
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('f-date').min = today;
    document.getElementById('f-date').value = today;
  } catch (e) {
    console.error('Error cargando selects:', e);
  }
}

function fillSelect(id, items, mapper) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = '<option value="">— Selecciona —</option>' +
    items.map(i => {
      const { value, label } = mapper(i);
      return `<option value="${value}">${esc(label)}</option>`;
    }).join('');
}

/* ── Lista principal ─────────────────────────── */
async function loadAppointments() {
  const date   = document.getElementById('filter-date')?.value;
  const status = document.getElementById('filter-status')?.value;

  let url = '/api/appointments?';
  if (date)   url += `date=${date}&`;
  if (status) url += `status=${status}&`;

  try {
    allAppointments = await apiFetch(url);
    renderTable();
  } catch (e) {
    showAlert('Error cargando reservas: ' + e.message, 'error');
  }
}

function renderTable() {
  const tbody = document.getElementById('appt-tbody');
  if (!allAppointments.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="color:var(--gray-400)">No hay reservas con estos filtros.</td></tr>';
    return;
  }
  tbody.innerHTML = allAppointments.map(a => {
    const dt   = new Date(a.start_datetime);
    const date = dt.toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit', year: 'numeric' });
    const time = dt.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
    return `
      <tr>
        <td style="color:var(--gray-400)">#${a.id}</td>
        <td><strong>${esc(a.client?.name || '—')}</strong>
            ${a.client?.phone ? `<br><small>${esc(a.client.phone)}</small>` : ''}</td>
        <td>${esc(a.service?.name || '—')}
            ${a.price_charged ? `<br><small style="color:var(--gold)">$${a.price_charged.toLocaleString('es-CL')}</small>` : ''}</td>
        <td>${esc(a.professional?.name || '—')}</td>
        <td>${date}<br><strong>${time}</strong></td>
        <td><span class="badge badge-${a.status}">${STATUS_LABELS[a.status] || a.status}</span></td>
        <td>
          <button class="btn btn-sm btn-outline" onclick="openEditModal(${a.id})">Editar</button>
          <button class="btn btn-sm btn-danger" onclick="deleteAppt(${a.id})" style="margin-left:.4rem">✕</button>
        </td>
      </tr>
    `;
  }).join('');
}

function clearFilters() {
  document.getElementById('filter-date').value = '';
  document.getElementById('filter-status').value = '';
  loadAppointments();
}

/* ── Modal nueva reserva ─────────────────────── */
function openNewModal() {
  document.getElementById('f-slot').value = '';
  document.getElementById('f-notes').value = '';
  document.getElementById('slots-container').innerHTML = '<p class="slots-hint">Selecciona servicio, profesional y fecha</p>';
  document.getElementById('modal-new').classList.add('open');
}

function closeNewModal(e) {
  if (!e || e.target === document.getElementById('modal-new')) {
    document.getElementById('modal-new').classList.remove('open');
  }
}

async function loadAvailability() {
  const serviceId = document.getElementById('f-service').value;
  const profId    = document.getElementById('f-professional').value;
  const date      = document.getElementById('f-date').value;

  const container = document.getElementById('slots-container');

  if (!serviceId || !profId || !date) {
    container.innerHTML = '<p class="slots-hint">Selecciona servicio, profesional y fecha</p>';
    return;
  }

  container.innerHTML = '<p class="slots-hint">Cargando horarios...</p>';

  try {
    const data = await apiFetch(`/api/appointments/availability?professional_id=${profId}&service_id=${serviceId}&date=${date}`);

    if (data.reason) {
      container.innerHTML = `<p class="slots-hint">${esc(data.reason)}</p>`;
      return;
    }

    if (!data.slots || !data.slots.length) {
      container.innerHTML = '<p class="slots-hint">No hay horarios disponibles para esta fecha.</p>';
      return;
    }

    container.innerHTML = data.slots.map(slot => {
      const t = new Date(slot.start).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
      if (!slot.available) {
        return `<button class="slot-btn taken" disabled>${t}</button>`;
      }
      return `<button class="slot-btn" onclick="selectSlot('${slot.start}', this)">${t}</button>`;
    }).join('');

  } catch (e) {
    container.innerHTML = `<p class="slots-hint" style="color:var(--red)">${esc(e.message)}</p>`;
  }
}

function selectSlot(isoStr, btn) {
  document.querySelectorAll('.slot-btn.selected').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  document.getElementById('f-slot').value = isoStr;
}

async function createAppointment() {
  const clientId  = document.getElementById('f-client').value;
  const serviceId = document.getElementById('f-service').value;
  const profId    = document.getElementById('f-professional').value;
  const slot      = document.getElementById('f-slot').value;
  const notes     = document.getElementById('f-notes').value.trim();

  if (!clientId)  return showAlert('Selecciona un cliente', 'error');
  if (!serviceId) return showAlert('Selecciona un servicio', 'error');
  if (!profId)    return showAlert('Selecciona un profesional', 'error');
  if (!slot)      return showAlert('Selecciona un horario disponible', 'error');

  const body = {
    client_id:       parseInt(clientId),
    service_id:      parseInt(serviceId),
    professional_id: parseInt(profId),
    start_datetime:  slot,
    notes:           notes || null,
  };

  try {
    await apiFetch('/api/appointments', { method: 'POST', body: JSON.stringify(body) });
    showAlert('Reserva creada exitosamente', 'success');
    closeNewModal();
    await loadAppointments();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

/* ── Modal editar estado ─────────────────────── */
function openEditModal(id) {
  const a = allAppointments.find(x => x.id === id);
  if (!a) return;
  editingApptId = id;
  document.getElementById('edit-appt-id').textContent = id;
  document.getElementById('edit-status').value = a.status;
  document.getElementById('edit-notes').value  = a.notes || '';
  document.getElementById('modal-edit').classList.add('open');
}

function closeEditModal(e) {
  if (!e || e.target === document.getElementById('modal-edit')) {
    document.getElementById('modal-edit').classList.remove('open');
  }
}

async function updateAppointment() {
  if (!editingApptId) return;
  const body = {
    status: document.getElementById('edit-status').value,
    notes:  document.getElementById('edit-notes').value.trim() || null,
  };
  try {
    await apiFetch(`/api/appointments/${editingApptId}`, { method: 'PUT', body: JSON.stringify(body) });
    showAlert('Reserva actualizada', 'success');
    closeEditModal();
    await loadAppointments();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

async function deleteAppt(id) {
  if (!confirm('¿Eliminar esta reserva definitivamente?')) return;
  try {
    await apiFetch(`/api/appointments/${id}`, { method: 'DELETE' });
    showAlert('Reserva eliminada', 'success');
    await loadAppointments();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

/* ── Helpers ─────────────────────────────────── */
function showAlert(msg, type) {
  const el = document.getElementById('alert-box');
  el.textContent = msg;
  el.className = `alert alert-${type}`;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 5000);
}

function esc(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str || ''));
  return d.innerHTML;
}
