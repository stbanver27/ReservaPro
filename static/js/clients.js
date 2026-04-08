/* clients.js */

let allClients = [];
let editingId  = null;

window.addEventListener('DOMContentLoaded', async () => {
  requireAuth();
  await loadUserDisplay();
  await loadClients();
});

async function loadClients() {
  try {
    allClients = await apiFetch('/api/clients');
    renderTable(allClients);
  } catch (e) {
    showAlert('Error cargando clientes: ' + e.message, 'error');
  }
}

function renderTable(list) {
  const tbody = document.getElementById('clients-tbody');
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="color:var(--gray-400)">No hay clientes registrados.</td></tr>';
    return;
  }
  tbody.innerHTML = list.map(c => `
    <tr>
      <td><strong>${esc(c.name)}</strong></td>
      <td>${c.email ? `<a href="mailto:${esc(c.email)}">${esc(c.email)}</a>` : '—'}</td>
      <td>${c.phone ? esc(c.phone) : '—'}</td>
      <td style="color:var(--gray-400);font-size:.82rem">${c.notes ? esc(c.notes) : '—'}</td>
      <td>
        <button class="btn btn-sm btn-outline" onclick="openEdit(${c.id})">Editar</button>
        <button class="btn btn-sm btn-danger" onclick="deleteClient(${c.id})" style="margin-left:.4rem">Eliminar</button>
      </td>
    </tr>
  `).join('');
}

function filterClients() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const filtered = allClients.filter(c =>
    c.name.toLowerCase().includes(q) ||
    (c.email || '').toLowerCase().includes(q) ||
    (c.phone || '').includes(q)
  );
  renderTable(filtered);
}

function openModal() {
  editingId = null;
  document.getElementById('modal-title').textContent = 'Nuevo cliente';
  document.getElementById('client-id').value = '';
  document.getElementById('f-name').value = '';
  document.getElementById('f-email').value = '';
  document.getElementById('f-phone').value = '';
  document.getElementById('f-notes').value = '';
  document.getElementById('modal-overlay').classList.add('open');
}

function openEdit(id) {
  const c = allClients.find(x => x.id === id);
  if (!c) return;
  editingId = id;
  document.getElementById('modal-title').textContent = 'Editar cliente';
  document.getElementById('client-id').value = c.id;
  document.getElementById('f-name').value = c.name;
  document.getElementById('f-email').value = c.email || '';
  document.getElementById('f-phone').value = c.phone || '';
  document.getElementById('f-notes').value = c.notes || '';
  document.getElementById('modal-overlay').classList.add('open');
}

function closeModal(e) {
  if (!e || e.target === document.getElementById('modal-overlay')) {
    document.getElementById('modal-overlay').classList.remove('open');
  }
}

async function saveClient() {
  const name = document.getElementById('f-name').value.trim();
  if (!name) return showAlert('El nombre es obligatorio', 'error');

  const body = {
    name,
    email: document.getElementById('f-email').value.trim() || null,
    phone: document.getElementById('f-phone').value.trim() || null,
    notes: document.getElementById('f-notes').value.trim() || null,
  };

  try {
    if (editingId) {
      await apiFetch(`/api/clients/${editingId}`, { method: 'PUT', body: JSON.stringify(body) });
      showAlert('Cliente actualizado', 'success');
    } else {
      await apiFetch('/api/clients', { method: 'POST', body: JSON.stringify(body) });
      showAlert('Cliente creado', 'success');
    }
    closeModal();
    await loadClients();
  } catch (e) {
    showAlert('Error: ' + e.message, 'error');
  }
}

async function deleteClient(id) {
  if (!confirm('¿Eliminar este cliente? Esta acción no se puede deshacer.')) return;
  try {
    await apiFetch(`/api/clients/${id}`, { method: 'DELETE' });
    showAlert('Cliente eliminado', 'success');
    await loadClients();
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
