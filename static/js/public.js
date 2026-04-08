/* public.js — Formulario de reserva pública */

let selectedServiceId  = null;
let selectedProfId     = null;
let selectedSlot       = null;
let allServices        = [];
let allProfessionals   = [];

document.addEventListener('DOMContentLoaded', async () => {
  // Fecha mínima = hoy
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('sel-date').min = today;

  await Promise.all([loadBusiness(), loadPublicData()]);
});

async function loadBusiness() {
  try {
    const biz = await fetch('/api/business').then(r => r.ok ? r.json() : null);
    if (!biz) return;
    if (biz.name) document.getElementById('biz-name').textContent = biz.name;
    if (biz.description) document.getElementById('biz-desc').textContent = biz.description;
  } catch {}
}

async function loadPublicData() {
  try {
    const [services, profs] = await Promise.all([
      fetch('/api/public/services').then(r => r.json()),
      fetch('/api/public/professionals').then(r => r.json()),
    ]);
    allServices      = services;
    allProfessionals = profs;
    renderServices();
    renderProfessionals();
  } catch (e) {
    document.getElementById('service-list').innerHTML = '<p style="color:var(--red)">Error cargando datos. Recarga la página.</p>';
  }
}

/* ── Servicios ───────────────────────────────── */
function renderServices() {
  const el = document.getElementById('service-list');
  if (!allServices.length) {
    el.innerHTML = '<p style="color:var(--gray-400)">No hay servicios disponibles.</p>';
    return;
  }
  el.innerHTML = allServices.map(s => `
    <button class="service-chip" data-id="${s.id}" onclick="selectService(${s.id}, this)">
      <strong>${esc(s.name)}</strong>
      <span class="chip-price">$${s.price.toLocaleString('es-CL')}</span>
      <span class="chip-dur">${s.duration_minutes} min</span>
    </button>
  `).join('');
}

function selectService(id, btn) {
  selectedServiceId = id;
  document.querySelectorAll('.service-chip').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  document.getElementById('sel-service').value = id;
  clearSlots();
  tryLoadSlots();
}

/* ── Profesionales ───────────────────────────── */
function renderProfessionals() {
  const el = document.getElementById('prof-list');
  if (!allProfessionals.length) {
    el.innerHTML = '<p style="color:var(--gray-400)">No hay profesionales disponibles.</p>';
    return;
  }
  el.innerHTML = allProfessionals.map(p => {
    const initials = p.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    return `
      <button class="prof-chip" data-id="${p.id}" onclick="selectProfessional(${p.id}, this)">
        <span style="font-weight:700;font-size:1.1rem;margin-right:.4rem">${initials}</span>
        <span>
          <strong>${esc(p.name)}</strong><br>
          <small style="color:var(--gray-400)">${esc(p.specialty || '')}</small>
        </span>
      </button>
    `;
  }).join('');
}

function selectProfessional(id, btn) {
  selectedProfId = id;
  document.querySelectorAll('.prof-chip').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  document.getElementById('sel-prof').value = id;
  clearSlots();
  tryLoadSlots();
}

/* ── Disponibilidad ──────────────────────────── */
function tryLoadSlots() {
  if (selectedServiceId && selectedProfId && document.getElementById('sel-date').value) {
    loadPublicSlots();
  }
}

async function loadPublicSlots() {
  const date    = document.getElementById('sel-date').value;
  const slotsEl = document.getElementById('public-slots');

  if (!selectedServiceId || !selectedProfId || !date) return;

  const wrapper = document.getElementById('slots-wrapper');
  wrapper.style.display = 'block';
  slotsEl.innerHTML = '<p class="slots-hint">Cargando horarios...</p>';
  selectedSlot = null;
  document.getElementById('sel-slot').value = '';
  updateStep2Btn();

  try {
    const res = await fetch(`/api/appointments/availability?professional_id=${selectedProfId}&service_id=${selectedServiceId}&date=${date}`);
    const data = await res.json();

    if (data.reason) {
      slotsEl.innerHTML = `<p class="slots-hint">${esc(data.reason)}</p>`;
      return;
    }

    const available = (data.slots || []).filter(s => s.available);
    const taken     = (data.slots || []).filter(s => !s.available);

    if (!data.slots || !data.slots.length) {
      slotsEl.innerHTML = '<p class="slots-hint">No hay horarios para esta fecha.</p>';
      return;
    }

    slotsEl.innerHTML = data.slots.map(slot => {
      const t = new Date(slot.start).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
      if (!slot.available) {
        return `<button class="slot-btn taken" disabled>${t}</button>`;
      }
      return `<button class="slot-btn" onclick="selectPublicSlot('${slot.start}', this)">${t}</button>`;
    }).join('');

    if (!available.length) {
      slotsEl.innerHTML += '<p class="slots-hint" style="margin-top:.5rem">No quedan horarios disponibles este día.</p>';
    }

  } catch (e) {
    slotsEl.innerHTML = `<p class="slots-hint" style="color:var(--red)">Error: ${esc(e.message)}</p>`;
  }
}

function selectPublicSlot(isoStr, btn) {
  document.querySelectorAll('.slot-btn.selected').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  selectedSlot = isoStr;
  document.getElementById('sel-slot').value = isoStr;
  updateStep2Btn();
}

function clearSlots() {
  selectedSlot = null;
  document.getElementById('sel-slot').value = '';
  document.getElementById('slots-wrapper').style.display = 'none';
  document.getElementById('public-slots').innerHTML = '';
  updateStep2Btn();
}

function updateStep2Btn() {
  const ready = selectedServiceId && selectedProfId && selectedSlot;
  document.getElementById('btn-step2').disabled = !ready;
}

/* ── Pasos ───────────────────────────────────── */
function goStep2() {
  if (!selectedServiceId || !selectedProfId || !selectedSlot) return;

  const service = allServices.find(s => s.id == selectedServiceId);
  const prof    = allProfessionals.find(p => p.id == selectedProfId);
  const dt      = new Date(selectedSlot);
  const dateStr = dt.toLocaleDateString('es-CL', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const timeStr = dt.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });

  document.getElementById('booking-summary').innerHTML = `
    <strong>📋 Resumen de tu reserva</strong><br>
    🔧 Servicio: <strong>${esc(service?.name)}</strong> — $${service?.price?.toLocaleString('es-CL')}<br>
    👤 Profesional: <strong>${esc(prof?.name)}</strong><br>
    📅 Fecha: <strong>${dateStr}</strong> a las <strong>${timeStr}</strong>
  `;

  document.getElementById('step-1').style.display = 'none';
  document.getElementById('step-2').style.display = 'block';
}

function goStep1() {
  document.getElementById('step-2').style.display = 'none';
  document.getElementById('step-1').style.display = 'block';
  hidePublicAlert();
}

/* ── Envío ───────────────────────────────────── */
async function submitBooking() {
  const name  = document.getElementById('f-client-name').value.trim();
  const email = document.getElementById('f-client-email').value.trim();
  const phone = document.getElementById('f-client-phone').value.trim();
  const notes = document.getElementById('f-notes').value.trim();

  if (!name) return showPublicAlert('Por favor ingresa tu nombre completo.', 'error');

  const body = {
    client_name:     name,
    client_email:    email || null,
    client_phone:    phone || null,
    professional_id: parseInt(selectedProfId),
    service_id:      parseInt(selectedServiceId),
    start_datetime:  selectedSlot,
    notes:           notes || null,
  };

  try {
    const res = await fetch('/api/public/book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      showPublicAlert(data.detail || 'Error al registrar la reserva. Intenta nuevamente.', 'error');
      return;
    }

    document.getElementById('step-2').style.display = 'none';
    document.getElementById('confirm-msg').textContent = data.detail || '¡Tu reserva fue registrada!';
    document.getElementById('step-confirm').style.display = 'block';

  } catch (e) {
    showPublicAlert('Error de conexión. Intenta nuevamente.', 'error');
  }
}

function resetBooking() {
  selectedServiceId = null;
  selectedProfId    = null;
  selectedSlot      = null;

  document.querySelectorAll('.service-chip, .prof-chip, .slot-btn').forEach(b => b.classList.remove('selected'));
  document.getElementById('sel-service').value = '';
  document.getElementById('sel-prof').value    = '';
  document.getElementById('sel-slot').value    = '';
  document.getElementById('sel-date').value    = '';
  document.getElementById('f-client-name').value  = '';
  document.getElementById('f-client-email').value = '';
  document.getElementById('f-client-phone').value = '';
  document.getElementById('f-notes').value         = '';
  document.getElementById('slots-wrapper').style.display = 'none';
  document.getElementById('btn-step2').disabled = true;

  document.getElementById('step-confirm').style.display = 'none';
  document.getElementById('step-1').style.display       = 'block';
  document.getElementById('step-2').style.display       = 'none';
  hidePublicAlert();
}

/* ── Alert ───────────────────────────────────── */
function showPublicAlert(msg, type) {
  const el = document.getElementById('public-alert');
  el.textContent = msg;
  el.className = `alert alert-${type}`;
  el.style.display = 'block';
}

function hidePublicAlert() {
  const el = document.getElementById('public-alert');
  if (el) el.style.display = 'none';
}

function esc(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str || ''));
  return d.innerHTML;
}
