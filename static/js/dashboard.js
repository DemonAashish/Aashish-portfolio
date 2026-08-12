(function () {
  'use strict';

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $all(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  function esc(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  // -----------------------------------------------------------------
  // Entity config: describes each CRUD tab's API path, table columns,
  // and edit-form fields. Add a new tab by adding an entry here plus
  // its markup in dashboard.html.
  // -----------------------------------------------------------------
  const ENTITIES = {
    projects: {
      label: 'Project',
      api: '/api/admin/projects',
      columns: [
        { key: 'title', label: 'Title' },
        { key: 'tech_stack_raw', label: 'Tech' },
        { key: 'featured', label: 'Featured', render: (v) => (v ? 'Yes' : 'No') },
        { key: 'order', label: 'Order' },
      ],
      fields: [
        { key: 'title', label: 'Title', type: 'text', required: true },
        { key: 'description', label: 'Description', type: 'textarea' },
        { key: 'highlights', label: 'Highlights (one per line)', type: 'textarea', rawKey: 'highlights_raw' },
        { key: 'tech_stack', label: 'Tech stack (comma-separated)', type: 'text', rawKey: 'tech_stack_raw' },
        { key: 'github_url', label: 'GitHub URL', type: 'text' },
        { key: 'live_url', label: 'Live URL', type: 'text' },
        { key: 'featured', label: 'Featured on homepage', type: 'checkbox' },
        { key: 'order', label: 'Sort order', type: 'number' },
      ],
    },
    skills: {
      label: 'Skill',
      api: '/api/admin/skills',
      columns: [
        { key: 'name', label: 'Name' },
        { key: 'category', label: 'Category' },
        { key: 'order', label: 'Order' },
      ],
      fields: [
        { key: 'name', label: 'Name', type: 'text', required: true },
        { key: 'category', label: 'Category', type: 'text', required: true },
        { key: 'order', label: 'Sort order', type: 'number' },
      ],
    },
    experience: {
      label: 'Experience',
      api: '/api/admin/experience',
      columns: [
        { key: 'role', label: 'Role' },
        { key: 'company', label: 'Company' },
        { key: 'date_range', label: 'Dates' },
        { key: 'order', label: 'Order' },
      ],
      fields: [
        { key: 'role', label: 'Role', type: 'text', required: true },
        { key: 'company', label: 'Company', type: 'text', required: true },
        { key: 'date_range', label: 'Date range', type: 'text' },
        { key: 'description', label: 'Highlights (one per line)', type: 'textarea' },
        { key: 'order', label: 'Sort order', type: 'number' },
      ],
    },
    education: {
      label: 'Education',
      api: '/api/admin/education',
      columns: [
        { key: 'degree', label: 'Degree' },
        { key: 'institution', label: 'Institution' },
        { key: 'date_range', label: 'Dates' },
      ],
      fields: [
        { key: 'degree', label: 'Degree', type: 'text', required: true },
        { key: 'institution', label: 'Institution', type: 'text', required: true },
        { key: 'date_range', label: 'Date range', type: 'text' },
        { key: 'order', label: 'Sort order', type: 'number' },
      ],
    },
    certifications: {
      label: 'Certification',
      api: '/api/admin/certifications',
      columns: [
        { key: 'name', label: 'Name' },
        { key: 'issuer', label: 'Issuer' },
      ],
      fields: [
        { key: 'name', label: 'Name', type: 'text', required: true },
        { key: 'issuer', label: 'Issuer', type: 'text' },
        { key: 'description', label: 'Description', type: 'textarea' },
        { key: 'order', label: 'Sort order', type: 'number' },
      ],
    },
  };

  const state = { data: {} };

  // -----------------------------------------------------------------
  // API + toast helpers
  // -----------------------------------------------------------------
  async function api(path, options) {
    const res = await fetch(path, Object.assign({ headers: { 'Content-Type': 'application/json' } }, options));
    if (res.status === 401) {
      window.location.href = '/dashboard/login';
      throw new Error('Not authenticated');
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Request failed.');
    return data;
  }

  let toastTimer = null;
  function showToast(message, isError) {
    const toast = $('#toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = 'toast is-visible' + (isError ? ' toast--error' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.className = 'toast'; }, 3200);
  }

  // -----------------------------------------------------------------
  // Tabs
  // -----------------------------------------------------------------
  function activateTab(tab) {
    $all('.dash-nav__item').forEach((btn) => btn.classList.toggle('is-active', btn.dataset.tab === tab));
    $all('.dash-panel').forEach((panel) => panel.classList.toggle('is-active', panel.id === 'panel-' + tab));
    const mobileNav = $('#dashMobileNav');
    if (mobileNav) mobileNav.value = tab;

    if (tab === 'overview') loadStats();
    else if (ENTITIES[tab]) loadEntity(tab);
    else if (tab === 'messages') loadMessages();
    else if (tab === 'chatlogs') loadChatLogs();
  }

  $all('.dash-nav__item').forEach((btn) => btn.addEventListener('click', () => activateTab(btn.dataset.tab)));
  const mobileNavEl = $('#dashMobileNav');
  if (mobileNavEl) mobileNavEl.addEventListener('change', (e) => activateTab(e.target.value));

  // -----------------------------------------------------------------
  // Overview
  // -----------------------------------------------------------------
  async function loadStats() {
    try {
      const stats = await api('/api/admin/stats');
      const grid = $('#statGrid');
      const cards = [
        { label: 'Projects', value: stats.projects },
        { label: 'Skills', value: stats.skills },
        { label: 'Messages', value: stats.messages },
        { label: 'Unread messages', value: stats.unread_messages },
        { label: 'Chat conversations', value: stats.chat_conversations },
      ];
      grid.innerHTML = cards
        .map((c) => `
          <div class="stat-card">
            <div class="stat-card__value">${esc(c.value)}</div>
            <div class="stat-card__label">${esc(c.label)}</div>
          </div>`)
        .join('');

      const badge = $('#unreadBadge');
      if (badge) {
        if (stats.unread_messages > 0) {
          badge.hidden = false;
          badge.textContent = stats.unread_messages;
        } else {
          badge.hidden = true;
        }
      }
    } catch (e) {
      showToast(e.message, true);
    }
  }

  // -----------------------------------------------------------------
  // Generic entity CRUD (projects / skills / experience / education / certifications)
  // -----------------------------------------------------------------
  async function loadEntity(tab) {
    const config = ENTITIES[tab];
    try {
      const rows = await api(config.api);
      state.data[tab] = rows;
      renderTable(tab);
    } catch (e) {
      showToast(e.message, true);
    }
  }

  function renderTable(tab) {
    const config = ENTITIES[tab];
    const rows = state.data[tab] || [];
    const table = $('#table-' + tab);
    if (!table) return;

    if (!rows.length) {
      table.innerHTML = `<tbody><tr><td class="empty-state">No ${esc(config.label.toLowerCase())}s yet — click "+ Add" above to create one.</td></tr></tbody>`;
      return;
    }

    const head = `<thead><tr>${config.columns.map((c) => `<th>${esc(c.label)}</th>`).join('')}<th class="dash-table__actions">Actions</th></tr></thead>`;
    const body = rows
      .map((row) => {
        const cells = config.columns
          .map((c) => {
            const raw = row[c.key];
            const value = c.render ? c.render(raw) : raw;
            return `<td>${esc(value)}</td>`;
          })
          .join('');
        return `<tr>
          ${cells}
          <td class="dash-table__actions">
            <button class="btn-icon" data-edit="${tab}" data-id="${row.id}" type="button">Edit</button>
            <button class="btn-icon btn-icon--danger" data-delete="${tab}" data-id="${row.id}" type="button">Delete</button>
          </td>
        </tr>`;
      })
      .join('');

    table.innerHTML = head + '<tbody>' + body + '</tbody>';
  }

  // -----------------------------------------------------------------
  // Modal (shared add/edit form for every entity)
  // -----------------------------------------------------------------
  const backdrop = $('#modalBackdrop');
  const modalForm = $('#modalForm');
  const modalTitle = $('#modalTitle');
  let modalContext = null;

  function openModal(tab, id) {
    const config = ENTITIES[tab];
    const record = id ? (state.data[tab] || []).find((r) => r.id === id) : null;
    modalContext = { tab: tab, id: id };
    modalTitle.textContent = (id ? 'Edit ' : 'Add ') + config.label;

    modalForm.innerHTML = config.fields
      .map((f) => {
        const rawKey = f.rawKey || f.key;
        const value = record ? record[rawKey] ?? '' : '';

        if (f.type === 'textarea') {
          return `<div class="field"><label for="mf-${f.key}">${esc(f.label)}</label><textarea id="mf-${f.key}" name="${f.key}">${esc(value)}</textarea></div>`;
        }
        if (f.type === 'checkbox') {
          const checked = record ? !!record[f.key] : true;
          return `<div class="field field--checkbox"><label><input type="checkbox" id="mf-${f.key}" name="${f.key}" ${checked ? 'checked' : ''}> ${esc(f.label)}</label></div>`;
        }
        if (f.type === 'number') {
          return `<div class="field"><label for="mf-${f.key}">${esc(f.label)}</label><input type="number" id="mf-${f.key}" name="${f.key}" value="${esc(value || 0)}"></div>`;
        }
        return `<div class="field"><label for="mf-${f.key}">${esc(f.label)}</label><input type="text" id="mf-${f.key}" name="${f.key}" value="${esc(value)}" ${f.required ? 'required' : ''}></div>`;
      })
      .join('');

    backdrop.classList.add('is-open');
    const firstInput = modalForm.querySelector('input, textarea');
    if (firstInput) firstInput.focus();
  }

  function closeModal() {
    backdrop.classList.remove('is-open');
    modalContext = null;
    modalForm.innerHTML = '';
  }

  $('#modalClose').addEventListener('click', closeModal);
  $('#modalCancel').addEventListener('click', closeModal);
  backdrop.addEventListener('click', (e) => { if (e.target === backdrop) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && backdrop.classList.contains('is-open')) closeModal(); });

  modalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!modalContext) return;
    const tab = modalContext.tab;
    const id = modalContext.id;
    const config = ENTITIES[tab];
    const formData = new FormData(modalForm);
    const payload = {};

    config.fields.forEach((f) => {
      if (f.type === 'checkbox') payload[f.key] = !!modalForm.querySelector(`[name="${f.key}"]`).checked;
      else if (f.type === 'number') payload[f.key] = Number(formData.get(f.key) || 0);
      else payload[f.key] = formData.get(f.key) || '';
    });

    const saveBtn = $('#modalSave');
    saveBtn.disabled = true;
    try {
      if (id) await api(`${config.api}/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      else await api(config.api, { method: 'POST', body: JSON.stringify(payload) });
      closeModal();
      showToast('Saved.');
      loadEntity(tab);
    } catch (err) {
      showToast(err.message, true);
    } finally {
      saveBtn.disabled = false;
    }
  });

  document.addEventListener('click', async (e) => {
    const addBtn = e.target.closest('[data-add]');
    if (addBtn) { openModal(addBtn.dataset.add, null); return; }

    const editBtn = e.target.closest('[data-edit]');
    if (editBtn) { openModal(editBtn.dataset.edit, Number(editBtn.dataset.id)); return; }

    const delBtn = e.target.closest('[data-delete]');
    if (delBtn) {
      const tab = delBtn.dataset.delete;
      const id = Number(delBtn.dataset.id);
      const config = ENTITIES[tab];
      if (!window.confirm(`Delete this ${config.label.toLowerCase()}? This can't be undone.`)) return;
      try {
        await api(`${config.api}/${id}`, { method: 'DELETE' });
        showToast('Deleted.');
        loadEntity(tab);
        loadStats();
      } catch (err) {
        showToast(err.message, true);
      }
    }
  });

  // -----------------------------------------------------------------
  // Messages
  // -----------------------------------------------------------------
  async function loadMessages() {
    try {
      const messages = await api('/api/admin/messages');
      const list = $('#msgList');
      if (!messages.length) { list.innerHTML = '<p class="empty-state">No messages yet.</p>'; return; }

      list.innerHTML = messages
        .map((m) => `
          <div class="msg-card ${m.is_read ? '' : 'msg-card--unread'}">
            <div class="msg-card__head">
              <div>
                <strong>${esc(m.name)}</strong> <span class="msg-card__email">&lt;${esc(m.email)}&gt;</span>
                ${m.subject ? `<div class="msg-card__subject">${esc(m.subject)}</div>` : ''}
              </div>
              <div class="msg-card__meta">
                <span>${esc(m.created_at)}</span>
                <button class="btn-icon" data-toggle-read="${m.id}" data-read="${m.is_read}" type="button">${m.is_read ? 'Mark unread' : 'Mark read'}</button>
                <button class="btn-icon btn-icon--danger" data-delete-msg="${m.id}" type="button">Delete</button>
              </div>
            </div>
            <p class="msg-card__body">${esc(m.body)}</p>
          </div>`)
        .join('');
    } catch (e) {
      showToast(e.message, true);
    }
  }

  const messagesPanel = $('#panel-messages');
  if (messagesPanel) {
    messagesPanel.addEventListener('click', async (e) => {
      const toggleBtn = e.target.closest('[data-toggle-read]');
      if (toggleBtn) {
        const id = Number(toggleBtn.dataset.toggleRead);
        const isRead = toggleBtn.dataset.read === 'true';
        try {
          await api(`/api/admin/messages/${id}`, { method: 'PATCH', body: JSON.stringify({ is_read: !isRead }) });
          loadMessages();
          loadStats();
        } catch (err) {
          showToast(err.message, true);
        }
        return;
      }

      const delBtn = e.target.closest('[data-delete-msg]');
      if (delBtn) {
        if (!window.confirm('Delete this message?')) return;
        const id = Number(delBtn.dataset.deleteMsg);
        try {
          await api(`/api/admin/messages/${id}`, { method: 'DELETE' });
          loadMessages();
          loadStats();
        } catch (err) {
          showToast(err.message, true);
        }
      }
    });
  }

  // -----------------------------------------------------------------
  // Chat logs (read-only)
  // -----------------------------------------------------------------
  async function loadChatLogs() {
    try {
      const logs = await api('/api/admin/chatlogs');
      const list = $('#chatLogList');
      if (!logs.length) { list.innerHTML = '<p class="empty-state">No conversations yet.</p>'; return; }

      list.innerHTML = logs
        .map((l) => `
          <div class="msg-card">
            <div class="msg-card__head"><span class="msg-card__meta">${esc(l.created_at)}</span></div>
            <p class="msg-card__body"><strong>Visitor:</strong> ${esc(l.user_message)}</p>
            <p class="msg-card__body"><strong>AI:</strong> ${esc(l.ai_response)}</p>
          </div>`)
        .join('');
    } catch (e) {
      showToast(e.message, true);
    }
  }

  // -----------------------------------------------------------------
  // Account / password
  // -----------------------------------------------------------------
  const passwordForm = $('#passwordForm');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const status = $('#passwordStatus');
      const current_password = $('#curPass').value;
      const new_password = $('#newPass').value;
      status.textContent = '';
      status.className = 'form-status';
      try {
        const res = await api('/api/admin/account/password', {
          method: 'PATCH',
          body: JSON.stringify({ current_password: current_password, new_password: new_password }),
        });
        status.textContent = res.message || 'Password updated.';
        status.className = 'form-status form-status--ok';
        passwordForm.reset();
      } catch (err) {
        status.textContent = err.message;
        status.className = 'form-status form-status--error';
      }
    });
  }

  // -----------------------------------------------------------------
  // Init
  // -----------------------------------------------------------------
  loadStats();
})();
