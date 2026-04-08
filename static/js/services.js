/* services.js */

let allServices = [];
let editingId = null;

window.addEventListener('DOMContentLoaded', async () => {
  requireAuth();
  await loadUserDisplay();
  await loadServices();
});

async function loadServices() {
  try {
    allServices = await apiFetch('/api/services');
    renderTable();
  } catch (e) {
    showAlert('Error cargando servicios: ' + e.message, 'error');
  }
}

function renderTable() {
  const tbody = document.getElementById('services-tbody');
  if (!allServices.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="color:var(--gray-400)">No hay servicios registrados.</td></tr>';
    return;
  }
  tbody.innerHTML = allServices.map(s => `
    <tr>
      <td>
        <strong>${esc(s.name)}</strong>
        ${s.description ? `<br><small style="color:var(--gray-400)">${esc(s.description)}</small>` : ''}
      </td>
      <td>${s.duration_minutes} min</td>
      <td>$${s.price.toLocaleString('es-CL')}</td>
      <td><span class="badge badge-${s.is_active ? 'active' : 'inactive'}">${s.is_active ? 'Activo' : 'Inactivo'}</span></td>
      <td>
        <button class="btn btn-sm btn-outline" onclick="openEdit(${s.id})">Editar</button>
        <button class="btn btn-sm btn-danger" onclick="deleteService(${s.id})" style="margin-left:.4rem">Eliminar</button>
      </td>
    </tr>
  `).join('');
}

function openModal() {
  editingId = null;
  document.getElementById('modal-title').textContent = 'Nuevo servicio';
  document.getElementById('service-id').value = '';
  document.getElementById('f-name').value = '';
  document.getElementById('f-description').value = '';
  document.getElementById('f-duration').value = 30;
  document.getElementById('f-price').value = 0;
  document.getElementById('f-active').checked = true;
  document.getElementById('modal-overlay').classList.add('open');
}

function openEdit(id) {
  const s = allServices.find(x => x.id === id);
  if (!s) return;
  editingId = id;
  document.getElementById('modal-title').textContent = 'Editar servicio';
  document.getElementById('service-id').value = s.id;
  document.getElementById('f-name').value = s.name;
  document.getElementById('f-description').value = s.description || '';
  document.getElementById('f-duration').value = s.duration_minutes;
  document.getElementById('f-price').value = s.price;
  document.getElementById('f-active').checked = s.is_active;
  document.getElementById('modal-overlay').classList.add('open');
}

function closeModal(e) {
  if (!e || e.target === document.getElementById('modal-overlay')) {
    document.getElementById('modal-overlay').classList.remove('open');
  }
}

async function saveService() {
  const name     = document.getElementById('f-name').value.trim();
  const desc     = document.getElementById('f-description').value.trim();
  const duration = parseInt(document.getElementById('f-duration').value);
  const price    = parseFloat(document.getElementById('f-price').value);
  const active   = document.getElementById('f-active').checked;

  if (!name) return showAlert('El nombre es obligatorio', 'error');
  if (!duration || duration < 15) return showAlert('La duración mínima es 15 minutos', 'error');

  const body = { name, description: desc, duration_minutes: duration, price, is_active: active };

  try {
    if (editingId) {
      await apiFetch(`/api/services/${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
      showAlert('Servicio actualizado', 'success');
    } else {
      await apiFetch('/api/services', { method: 'POST', body: JSON.stringify(body) });
      showAlert('Servicio creado', 'success');
    }
    closeModal();
    await loadServices();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

async function deleteService(id) {
  if (!confirm('¿Eliminar este servicio? Esta acción no se puede deshacer.')) return;
  try {
    await apiFetch(`/api/services/${id}`, { method: 'DELETE' });
    showAlert('Servicio eliminado', 'success');
    await loadServices();
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
