/* professionals.js */

let allProfs = [];
let editingId = null;

const DAY_NAMES = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

window.addEventListener('DOMContentLoaded', async () => {
  requireAuth();
  await loadUserDisplay();
  await loadProfessionals();
});

async function loadProfessionals() {
  try {
    allProfs = await apiFetch('/api/professionals');
    renderGrid();
  } catch (e) {
    showAlert('Error cargando profesionales: ' + e.message, 'error');
  }
}

function renderGrid() {
  const grid = document.getElementById('prof-grid');
  if (!allProfs.length) {
    grid.innerHTML = '<p class="loading">No hay profesionales registrados.</p>';
    return;
  }
  grid.innerHTML = allProfs.map(p => {
    const initials = p.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    const days = (p.working_days || '').split(',').filter(Boolean)
      .map(d => DAY_NAMES[parseInt(d)] || d).join(', ');
    return `
      <div class="prof-card">
        <div style="display:flex;align-items:center;gap:.85rem">
          <div class="prof-avatar">${initials}</div>
          <div>
            <div class="prof-name">${esc(p.name)}</div>
            <div class="prof-specialty">${esc(p.specialty || '')}</div>
          </div>
          <span class="badge badge-${p.is_active ? 'active' : 'inactive'}" style="margin-left:auto">
            ${p.is_active ? 'Activo' : 'Inactivo'}
          </span>
        </div>
        ${p.email ? `<div class="prof-meta">✉️ ${esc(p.email)}</div>` : ''}
        ${p.phone ? `<div class="prof-meta">📞 ${esc(p.phone)}</div>` : ''}
        <div class="prof-meta">🕐 ${p.work_start} – ${p.work_end}</div>
        <div class="prof-meta">📅 ${days || 'Sin días configurados'}</div>
        ${p.bio ? `<p style="font-size:.82rem;color:var(--gray-600)">${esc(p.bio)}</p>` : ''}
        <div class="prof-actions">
          <button class="btn btn-sm btn-outline" onclick="openEdit(${p.id})">Editar</button>
          <button class="btn btn-sm btn-danger" onclick="deleteProfessional(${p.id})">Eliminar</button>
        </div>
      </div>
    `;
  }).join('');
}

function openModal() {
  editingId = null;
  document.getElementById('modal-title').textContent = 'Nuevo profesional';
  document.getElementById('prof-id').value = '';
  document.getElementById('f-name').value = '';
  document.getElementById('f-specialty').value = '';
  document.getElementById('f-email').value = '';
  document.getElementById('f-phone').value = '';
  document.getElementById('f-bio').value = '';
  document.getElementById('f-work-start').value = '09:00';
  document.getElementById('f-work-end').value = '18:00';
  document.getElementById('f-active').checked = true;
  // Reset days: 0-4 checked, 5-6 unchecked
  document.querySelectorAll('#days-picker input[type="checkbox"]').forEach(cb => {
    cb.checked = ['0','1','2','3','4'].includes(cb.value);
  });
  document.getElementById('modal-overlay').classList.add('open');
}

function openEdit(id) {
  const p = allProfs.find(x => x.id === id);
  if (!p) return;
  editingId = id;
  document.getElementById('modal-title').textContent = 'Editar profesional';
  document.getElementById('prof-id').value = p.id;
  document.getElementById('f-name').value = p.name;
  document.getElementById('f-specialty').value = p.specialty || '';
  document.getElementById('f-email').value = p.email || '';
  document.getElementById('f-phone').value = p.phone || '';
  document.getElementById('f-bio').value = p.bio || '';
  document.getElementById('f-work-start').value = p.work_start || '09:00';
  document.getElementById('f-work-end').value = p.work_end || '18:00';
  document.getElementById('f-active').checked = p.is_active;
  const activeDays = (p.working_days || '').split(',').map(d => d.trim());
  document.querySelectorAll('#days-picker input[type="checkbox"]').forEach(cb => {
    cb.checked = activeDays.includes(cb.value);
  });
  document.getElementById('modal-overlay').classList.add('open');
}

function closeModal(e) {
  if (!e || e.target === document.getElementById('modal-overlay')) {
    document.getElementById('modal-overlay').classList.remove('open');
  }
}

async function saveProfessional() {
  const name = document.getElementById('f-name').value.trim();
  if (!name) return showAlert('El nombre es obligatorio', 'error');

  const checkedDays = [...document.querySelectorAll('#days-picker input:checked')]
    .map(cb => cb.value).join(',');

  const body = {
    name,
    specialty:    document.getElementById('f-specialty').value.trim(),
    email:        document.getElementById('f-email').value.trim(),
    phone:        document.getElementById('f-phone').value.trim(),
    bio:          document.getElementById('f-bio').value.trim(),
    work_start:   document.getElementById('f-work-start').value,
    work_end:     document.getElementById('f-work-end').value,
    is_active:    document.getElementById('f-active').checked,
    working_days: checkedDays,
  };

  try {
    if (editingId) {
      await apiFetch(`/api/professionals/${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
      showAlert('Profesional actualizado', 'success');
    } else {
      await apiFetch('/api/professionals', { method: 'POST', body: JSON.stringify(body) });
      showAlert('Profesional creado', 'success');
    }
    closeModal();
    await loadProfessionals();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

async function deleteProfessional(id) {
  if (!confirm('¿Eliminar este profesional? Esta acción no se puede deshacer.')) return;
  try {
    await apiFetch(`/api/professionals/${id}`, { method: 'DELETE' });
    showAlert('Profesional eliminado', 'success');
    await loadProfessionals();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

function showAlert(msg, type) {
  const el = document.getElementById('alert-box');
  el.textContent = msg;
  el.className = `alert alert-${type}`;
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 4000);
}

function esc(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str || ''));
  return d.innerHTML;
}
