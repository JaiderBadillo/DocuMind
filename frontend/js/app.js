// ==========================================================================
// DOCUMIND APP CONTROLLER - EVENT BINDINGS & VIEW STATE
// ==========================================================================

import { api } from './api.js?v=2.1';
import { 
  renderDocumentCard, 
  renderDocumentModal, 
  renderChatMessage, 
  renderMarkdown,
  showToast, 
  formatBytes,
  CATEGORY_NAMES,
  CATEGORY_CLASSES
} from './components.js?v=2.1';

class DocuMindApp {
  constructor() {
    this.currentView = 'docs'; // 'docs', 'chat', 'notebook', 'dashboard'
    this.currentRepoId = null;
    this.currentCategory = null;
    this.currentStatus = null;
    this.repositories = [];
    this.documents = [];
    this.pollingTimer = null;
    this.selectedNotebookSources = new Set();
    this.notebookSources = [];
    
    this.init();
  }

  async init() {
    this.bindGlobalEvents();
    if (api.isAuthenticated()) {
      this.showApp();
    } else {
      this.showAuth();
    }
  }

  bindGlobalEvents() {
    // Auth expired event
    window.addEventListener('auth:expired', () => {
      showToast('Su sesión ha expirado. Inicie sesión nuevamente.', 'error');
      this.showAuth();
    });

    // Theme toggle
    const themeBtn = document.getElementById('btn-toggle-theme');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('documind_theme', newTheme);
        themeBtn.textContent = newTheme === 'light' ? '🌙' : '☀️';
      });

      // Restore saved theme
      const savedTheme = localStorage.getItem('documind_theme') || 'dark';
      document.documentElement.setAttribute('data-theme', savedTheme);
      themeBtn.textContent = savedTheme === 'light' ? '🌙' : '☀️';
    }

    // Auth Forms
    this.bindAuthEvents();
  }

  // ================= AUTHENTICATION =================
  bindAuthEvents() {
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const btnDemo = document.getElementById('btn-demo-login');

    if (tabLogin && tabRegister) {
      tabLogin.addEventListener('click', () => {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        formLogin.classList.remove('hidden');
        formRegister.classList.add('hidden');
      });

      tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        formRegister.classList.remove('hidden');
        formLogin.classList.add('hidden');
      });
    }

    if (formLogin) {
      formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        try {
          await api.login(email, password);
          showToast('Bienvenido a DocuMind Enterprise', 'success');
          this.showApp();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    if (formRegister) {
      formRegister.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        try {
          await api.register(email, name, password);
          showToast('Cuenta creada y autenticada con éxito', 'success');
          this.showApp();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    if (btnDemo) {
      btnDemo.addEventListener('click', async () => {
        try {
          document.getElementById('login-email').value = 'admin@documind.com';
          document.getElementById('login-password').value = 'Admin123!';
          await api.login('admin@documind.com', 'Admin123!');
          showToast('Acceso con credenciales de Administrador demo', 'success');
          this.showApp();
        } catch (err) {
          showToast('Iniciando base de datos...', 'info');
        }
      });
    }

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        api.clearSession();
        showToast('Sesión cerrada correctamente', 'info');
        this.showAuth();
      });
    }
  }

  showAuth() {
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('app-section').classList.add('hidden');
    if (this.pollingTimer) clearInterval(this.pollingTimer);
  }

  async showApp() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('app-section').classList.remove('hidden');

    // Display user profile info
    const user = api.user || {};
    document.getElementById('user-display-name').textContent = user.full_name || 'Usuario';
    document.getElementById('user-display-role').textContent = user.role === 'ADMIN' ? 'Administrador' : 'Analista';
    document.getElementById('user-avatar').textContent = (user.full_name || 'U').charAt(0).toUpperCase();

    this.bindAppEvents();
    await this.loadRepositories();
    this.switchView('docs');
    this.startStatusPolling();
  }

  // ================= MAIN APP EVENTS =================
  bindAppEvents() {
    // Navigation items
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
      item.addEventListener('click', () => {
        const view = item.getAttribute('data-view');
        this.switchView(view);
      });
    });

    // New folder button
    const btnNewFolder = document.getElementById('btn-new-folder');
    if (btnNewFolder) {
      btnNewFolder.addEventListener('click', () => this.promptCreateFolder());
    }

    // Drag and drop upload zone
    this.setupDropzone();

    // Filters (Categories & Status)
    document.querySelectorAll('.pill-category').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.pill-category').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentCategory = btn.getAttribute('data-category') || null;
        this.renderDocumentList();
      });
    });

    document.querySelectorAll('.pill-status').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.pill-status').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentStatus = btn.getAttribute('data-status') || null;
        this.renderDocumentList();
      });
    });

    // Topbar Search with Filters
    const searchInput = document.getElementById('global-search-input');
    const searchCat = document.getElementById('search-filter-category');
    const searchFmt = document.getElementById('search-filter-format');
    const btnClearSearch = document.getElementById('btn-clear-search');

    const triggerSearch = () => {
      this.handleSearch(searchInput?.value || '');
    };

    if (searchInput) {
      let timeout = null;
      searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(triggerSearch, 250);
      });
    }

    if (searchCat) searchCat.addEventListener('change', triggerSearch);
    if (searchFmt) searchFmt.addEventListener('change', triggerSearch);

    if (btnClearSearch) {
      btnClearSearch.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (searchCat) searchCat.value = '';
        if (searchFmt) searchFmt.value = '';
        btnClearSearch.classList.add('hidden');
        this.renderDocumentList();
      });
    }

    // AI Configuration Modal
    const btnConfigAi = document.getElementById('btn-config-ai');
    const modalConfigAi = document.getElementById('modal-config-ai');
    const btnCloseAiModal = document.getElementById('btn-close-ai-modal');
    const btnSaveGeminiKey = document.getElementById('btn-save-gemini-key');
    const inputGeminiKey = document.getElementById('input-gemini-key');
    const geminiStatus = document.getElementById('gemini-status-indicator');

    const updateAiStatus = async () => {
      try {
        const res = await api.getGeminiKeyStatus();
        if (res.active) {
          geminiStatus.innerHTML = `<span style="color: var(--success); font-weight: 600;">✓ Google Gemini 1.5 Flash ACTIVO (${res.masked_key})</span>`;
        } else {
          geminiStatus.innerHTML = `<span style="color: var(--warning); font-weight: 600;">⚡ Motor Local Semántico Activo (Sin API Key)</span>`;
        }
      } catch (err) {
        geminiStatus.textContent = 'Estado: No disponible';
      }
    };

    if (btnConfigAi) {
      btnConfigAi.addEventListener('click', () => {
        modalConfigAi.classList.remove('hidden');
        updateAiStatus();
      });
    }

    if (btnCloseAiModal) {
      btnCloseAiModal.addEventListener('click', () => {
        modalConfigAi.classList.add('hidden');
      });
    }

    if (btnSaveGeminiKey) {
      btnSaveGeminiKey.addEventListener('click', async () => {
        const key = inputGeminiKey.value.trim();
        try {
          await api.setGeminiKey(key);
          showToast('Clave de IA configurada correctamente', 'success');
          inputGeminiKey.value = '';
          await updateAiStatus();
          modalConfigAi.classList.add('hidden');
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    }

    // Chat Events
    this.bindChatEvents();

    // NotebookLM Studio Events
    this.bindNotebookEvents();
  }

  // ================= VIEW SWITCHER =================
  switchView(viewName) {
    this.currentView = viewName;

    // Update navigation active class
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
      if (item.getAttribute('data-view') === viewName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Toggle views
    document.getElementById('view-docs').classList.toggle('hidden', viewName !== 'docs');
    document.getElementById('view-chat').classList.toggle('hidden', viewName !== 'chat');
    document.getElementById('view-notebook').classList.toggle('hidden', viewName !== 'notebook');
    document.getElementById('view-dashboard').classList.toggle('hidden', viewName !== 'dashboard');

    if (viewName === 'docs') {
      this.loadDocuments();
    } else if (viewName === 'notebook') {
      this.loadNotebookStudio();
    } else if (viewName === 'dashboard') {
      this.loadDashboard();
    }
  }

  // ================= REPOSITORIES =================
  async loadRepositories() {
    try {
      this.repositories = await api.getRepositories();
      const container = document.getElementById('sidebar-repos-list');
      container.innerHTML = '';

      // "All Repositories" Item
      const allItem = document.createElement('div');
      allItem.className = `repo-item ${this.currentRepoId === null ? 'active' : ''}`;
      allItem.innerHTML = `<span>📁</span> <span>Todos los Repositorios</span>`;
      allItem.addEventListener('click', () => {
        this.currentRepoId = null;
        this.updateRepoSelectionUI();
        this.loadDocuments();
      });
      container.appendChild(allItem);

      this.repositories.forEach(repo => {
        const item = document.createElement('div');
        item.className = `repo-item ${this.currentRepoId === repo.id ? 'active' : ''}`;
        item.innerHTML = `
          <span>📂</span> 
          <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-grow: 1;">${repo.name}</span>
          <span style="font-size: 0.72rem; opacity: 0.7; margin-right: 4px;">${repo.document_count || 0}</span>
          <button class="btn-delete-repo" title="Eliminar repositorio '${repo.name}'">🗑️</button>
        `;
        item.addEventListener('click', () => {
          this.currentRepoId = repo.id;
          this.updateRepoSelectionUI();
          this.loadDocuments();
        });

        const btnDel = item.querySelector('.btn-delete-repo');
        if (btnDel) {
          btnDel.addEventListener('click', (e) => {
            e.stopPropagation();
            this.confirmAndDeleteRepository(repo.id, repo.name);
          });
        }

        container.appendChild(item);
      });

      // Update folder dropdown in upload zone if present
      this.populateUploadFolderSelect();
      this.populateChatScopeSelect();
    } catch (err) {
      console.error('Error cargando repositorios:', err);
    }
  }

  updateRepoSelectionUI() {
    const items = document.querySelectorAll('#sidebar-repos-list .repo-item');
    items.forEach((item, idx) => {
      if (idx === 0 && this.currentRepoId === null) {
        item.classList.add('active');
      } else if (idx > 0 && this.repositories[idx - 1]?.id === this.currentRepoId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    const activeRepoName = this.currentRepoId 
      ? this.repositories.find(r => r.id === this.currentRepoId)?.name 
      : 'Todos los Repositorios';
    const folderTitle = document.getElementById('current-folder-title');
    if (folderTitle) folderTitle.textContent = activeRepoName;

    // Toggle topbar delete button for active repository
    const btnDeleteActive = document.getElementById('btn-delete-active-repo');
    if (btnDeleteActive) {
      if (this.currentRepoId !== null) {
        btnDeleteActive.classList.remove('hidden');
        btnDeleteActive.onclick = () => {
          const currentRepo = this.repositories.find(r => r.id === this.currentRepoId);
          if (currentRepo) {
            this.confirmAndDeleteRepository(currentRepo.id, currentRepo.name);
          }
        };
      } else {
        btnDeleteActive.classList.add('hidden');
      }
    }
  }

  async confirmAndDeleteRepository(repoId, repoName) {
    const confirmed = confirm(
      `⚠️ ¿Está seguro de eliminar el repositorio "${repoName}"?\n\n` +
      `ADVERTENCIA: Esta acción eliminará permanentemente la carpeta y todos los documentos indexados en ella.\n\n` +
      `¿Desea continuar con la eliminación?`
    );
    if (!confirmed) return;

    try {
      await api.deleteRepository(repoId);
      showToast(`Repositorio "${repoName}" eliminado exitosamente`, 'success');
      if (this.currentRepoId === repoId) {
        this.currentRepoId = null;
      }
      await this.loadRepositories();
      this.updateRepoSelectionUI();
      await this.loadDocuments();
    } catch (err) {
      showToast(`Error al eliminar repositorio: ${err.message}`, 'error');
    }
  }

  async promptCreateFolder() {
    const name = prompt('Ingrese el nombre del nuevo repositorio o carpeta:');
    if (!name || !name.strip?.() && !name.trim()) return;

    try {
      const newRepo = await api.createRepository(name.trim());
      showToast(`Repositorio "${newRepo.name}" creado con éxito`, 'success');
      await this.loadRepositories();
      this.currentRepoId = newRepo.id;
      this.updateRepoSelectionUI();
      this.loadDocuments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  populateUploadFolderSelect() {
    const select = document.getElementById('upload-repo-select');
    if (!select) return;
    select.innerHTML = '';
    this.repositories.forEach(repo => {
      const opt = document.createElement('option');
      opt.value = repo.id;
      opt.textContent = repo.name;
      if (repo.id === this.currentRepoId) opt.selected = true;
      select.appendChild(opt);
    });
  }

  populateChatScopeSelect() {
    const select = document.getElementById('chat-repo-scope');
    if (!select) return;
    const currentVal = select.value;
    select.innerHTML = '<option value="all">🌐 Todos los Repositorios</option>';
    this.repositories.forEach(repo => {
      const opt = document.createElement('option');
      opt.value = repo.id;
      opt.textContent = `📁 ${repo.name}`;
      select.appendChild(opt);
    });
    if (currentVal && Array.from(select.options).some(o => o.value === currentVal)) {
      select.value = currentVal;
    }
  }

  // ================= DOCUMENTS & DRAG AND DROP =================
  setupDropzone() {
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-upload-input');
    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) this.handleFileUpload(files);
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.handleFileUpload(e.target.files);
        fileInput.value = '';
      }
    });
  }

  async handleFileUpload(files) {
    if (this.repositories.length === 0) {
      showToast('Cree una carpeta o repositorio antes de subir archivos', 'warning');
      return;
    }

    const select = document.getElementById('upload-repo-select');
    const targetRepoId = select?.value || this.currentRepoId || this.repositories[0].id;

    showToast(`Subiendo y analizando ${files.length} archivo(s) con IA...`, 'info');

    try {
      await api.uploadDocuments(targetRepoId, Array.from(files));
      showToast('Archivos recibidos. Procesamiento de IA en segundo plano activo.', 'success');
      await this.loadRepositories();
      await this.loadDocuments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async loadDocuments() {
    try {
      const params = {};
      if (this.currentRepoId) params.repository_id = this.currentRepoId;
      this.documents = await api.getDocuments(params);
      this.renderDocumentList();
    } catch (err) {
      console.error('Error cargando documentos:', err);
    }
  }

  async handleSearch(query) {
    const q = (query || '').trim();
    const btnClear = document.getElementById('btn-clear-search');
    const catFilter = document.getElementById('search-filter-category')?.value || null;
    const fmtFilter = document.getElementById('search-filter-format')?.value || null;

    if (btnClear) {
      btnClear.classList.toggle('hidden', q.length === 0 && !catFilter && !fmtFilter);
    }

    if (q.length < 2 && !catFilter && !fmtFilter) {
      this.renderDocumentList();
      return;
    }

    const grid = document.getElementById('documents-grid');
    if (!grid) return;

    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 2.5rem 1rem; color: var(--text-muted);">
        <div class="spinner" style="margin: 0 auto 0.8rem auto;"></div>
        <div style="font-size: 0.95rem;">Buscando dentro del contenido íntegro de los documentos...</div>
      </div>
    `;

    try {
      const res = await api.search(q || '*', this.currentRepoId, catFilter, fmtFilter);
      const searchResults = res.results || [];

      grid.innerHTML = '';

      if (searchResults.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔍</div>
            <div style="font-size: 1.1rem; font-weight: 500;">No se encontraron documentos con esa coincidencia</div>
            <p style="font-size: 0.85rem; margin-top: 0.35rem;">Intenta con otras palabras clave (ej: "cláusula", "total", "IVA", "penalidad", "Python") o elimina los filtros.</p>
          </div>
        `;
        return;
      }

      // Banner de resultados de búsqueda
      const searchBanner = document.createElement('div');
      searchBanner.style.cssText = 'grid-column: 1 / -1; background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: var(--radius-sm); padding: 0.65rem 1rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;';
      searchBanner.innerHTML = `
        <span style="font-size: 0.88rem; color: var(--text-primary);">
          🔍 Se encontraron <strong>${searchResults.length}</strong> documento(s) con coincidencias para <em>"${q || 'filtro aplicado'}"</em>
        </span>
        <button id="btn-exit-search" class="btn-secondary" style="font-size: 0.78rem; padding: 0.25rem 0.6rem;">Volver a vista general</button>
      `;
      grid.appendChild(searchBanner);

      searchBanner.querySelector('#btn-exit-search').addEventListener('click', () => {
        const sInput = document.getElementById('global-search-input');
        if (sInput) sInput.value = '';
        const sCat = document.getElementById('search-filter-category');
        if (sCat) sCat.value = '';
        const sFmt = document.getElementById('search-filter-format');
        if (sFmt) sFmt.value = '';
        if (btnClear) btnClear.classList.add('hidden');
        this.renderDocumentList();
      });

      searchResults.forEach(hit => {
        const existingDoc = this.documents.find(d => d.id === hit.document_id);
        const doc = existingDoc ? { ...existingDoc } : {
          id: hit.document_id,
          original_filename: hit.document_name,
          file_extension: hit.document_name.substring(hit.document_name.lastIndexOf('.')),
          file_size_bytes: 0,
          category: hit.category,
          processing_status: 'COMPLETED',
          created_at: 'Indexado'
        };

        // Resaltar términos encontrados dentro del snippet
        let snippetText = hit.snippet || '';
        if (q && q !== '*') {
          const escapedQ = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const regex = new RegExp(`(${escapedQ})`, 'gi');
          snippetText = snippetText.replace(regex, '<mark class="doc-match">$1</mark>');
        }
        doc.search_snippet = snippetText;
        doc.relevance = hit.relevance;

        const card = renderDocumentCard(
          doc,
          (id) => this.openDocumentDetail(id),
          (id) => this.deleteDocument(id)
        );
        grid.appendChild(card);
      });
    } catch (err) {
      showToast(`Error en la búsqueda: ${err.message}`, 'error');
      this.renderDocumentList();
    }
  }

  renderDocumentList() {
    const grid = document.getElementById('documents-grid');
    if (!grid) return;

    let filtered = [...this.documents];

    if (this.currentCategory) {
      filtered = filtered.filter(d => d.category === this.currentCategory);
    }

    if (this.currentStatus) {
      filtered = filtered.filter(d => d.processing_status === this.currentStatus);
    }

    grid.innerHTML = '';

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
          <div style="font-size: 1.1rem; font-weight: 500;">No hay documentos en este filtro o repositorio</div>
          <p style="font-size: 0.85rem; margin-top: 0.25rem;">Arrastra y suelta archivos en la zona superior o prueba cambiando los filtros.</p>
        </div>
      `;
      return;
    }

    filtered.forEach(doc => {
      const card = renderDocumentCard(
        doc,
        (id) => this.openDocumentDetail(id),
        (id) => this.deleteDocument(id)
      );
      grid.appendChild(card);
    });

    // Update document badge count in sidebar
    const badge = document.getElementById('nav-docs-count');
    if (badge) badge.textContent = this.documents.length;
  }

  async openDocumentDetail(docId) {
    try {
      const doc = await api.getDocumentDetail(docId);
      const downloadUrl = api.downloadDocumentUrl(docId);
      const modal = renderDocumentModal(
        doc, 
        (id) => this.reprocessDocument(id),
        downloadUrl
      );
      document.body.appendChild(modal);
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async deleteDocument(docId) {
    try {
      await api.deleteDocument(docId);
      showToast('Documento eliminado correctamente', 'info');
      await this.loadRepositories();
      await this.loadDocuments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async reprocessDocument(docId) {
    try {
      await api.reprocessDocument(docId);
      showToast('Reprocesamiento con IA solicitado', 'info');
      await this.loadDocuments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  startStatusPolling() {
    if (this.pollingTimer) clearInterval(this.pollingTimer);
    // Poll every 4 seconds to check if pending/processing docs have completed
    this.pollingTimer = setInterval(() => {
      const hasProcessing = this.documents.some(d => d.processing_status === 'PROCESSING' || d.processing_status === 'PENDING');
      if (hasProcessing && this.currentView === 'docs') {
        this.loadDocuments();
      }
    }, 4000);
  }

  async handleSearch(query) {
    const searchInput = document.getElementById('global-search-input');
    const searchCat = document.getElementById('search-filter-category');
    const searchFmt = document.getElementById('search-filter-format');
    const btnClearSearch = document.getElementById('btn-clear-search');

    const q = (query !== undefined ? query : (searchInput?.value || '')).trim();
    const cat = searchCat?.value || null;
    const fmt = searchFmt?.value || null;

    if (!q && !cat && !fmt) {
      if (btnClearSearch) btnClearSearch.classList.add('hidden');
      this.renderDocumentList();
      return;
    }

    if (btnClearSearch) btnClearSearch.classList.remove('hidden');

    try {
      if (q.length >= 2) {
        const res = await api.search(q, this.currentRepoId, cat, fmt);
        const grid = document.getElementById('documents-grid');
        grid.innerHTML = '';

        if (res.results.length === 0) {
          grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
              <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
              <div style="font-size: 1.1rem; font-weight: 500;">No se encontraron coincidencias para "${q}"</div>
              <p style="font-size: 0.85rem; margin-top: 0.35rem;">Prueba con otros términos o ajusta los filtros de categoría y formato.</p>
            </div>
          `;
          return;
        }

        // Header showing results count and active filters
        const header = document.createElement('div');
        header.style.cssText = 'grid-column: 1 / -1; display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);';
        header.innerHTML = `
          <span style="font-size: 0.9rem; font-weight: 600; color: var(--accent-secondary);">
            🔍 ${res.results.length} documento(s) encontrado(s) para "${q}"
          </span>
          <span style="font-size: 0.78rem; color: var(--text-muted);">Búsqueda Híbrida: Texto Completo + Similitud Semántica</span>
        `;
        grid.appendChild(header);

        for (const r of res.results) {
          const baseDoc = this.documents.find(d => d.id === r.document_id) || {
            id: r.document_id,
            original_filename: r.document_name,
            file_extension: (r.document_name.split('.').pop() || 'txt'),
            file_size_bytes: 0,
            category: r.category,
            processing_status: 'COMPLETED',
            created_at: 'Indexado'
          };

          const docWithSnippet = {
            ...baseDoc,
            search_snippet: r.snippet,
            relevance: r.relevance
          };

          grid.appendChild(renderDocumentCard(
            docWithSnippet,
            (id) => this.openDocumentDetail(id),
            (id) => this.deleteDocument(id)
          ));
        }
      } else {
        // Filter by category or format without query string
        let filtered = [...this.documents];
        if (cat) filtered = filtered.filter(d => d.category === cat);
        if (fmt) filtered = filtered.filter(d => (d.file_extension || '').toLowerCase() === fmt.toLowerCase());

        const grid = document.getElementById('documents-grid');
        grid.innerHTML = '';

        if (filtered.length === 0) {
          grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-muted);">No hay documentos que coincidan con los filtros seleccionados.</div>`;
          return;
        }

        filtered.forEach(doc => {
          grid.appendChild(renderDocumentCard(doc, (id) => this.openDocumentDetail(id), (id) => this.deleteDocument(id)));
        });
      }
    } catch (err) {
      console.error('Error buscando:', err);
    }
  }

  // ================= CONVERSATIONAL RAG CHAT =================
  bindChatEvents() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messagesContainer = document.getElementById('chat-messages');

    if (!form || !input || !messagesContainer) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      input.value = '';

      // Append user bubble
      messagesContainer.appendChild(renderChatMessage({ sender: 'user', text }));
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      // Append loading bubble
      const loadingBubble = document.createElement('div');
      loadingBubble.className = 'chat-bubble bot';
      loadingBubble.innerHTML = `<span>Analizando repositorios y generando respuesta con RAG... 🔍</span>`;
      messagesContainer.appendChild(loadingBubble);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      try {
        const scopeSelect = document.getElementById('chat-repo-scope');
        const selectedScope = scopeSelect ? scopeSelect.value : 'all';
        const repoIdToSend = (selectedScope && selectedScope !== 'all') ? parseInt(selectedScope) : null;
        const resp = await api.ragChat(text, repoIdToSend);
        loadingBubble.remove();
        messagesContainer.appendChild(renderChatMessage({
          sender: 'bot',
          text: resp.answer,
          sources: resp.sources,
          model: resp.model_used
        }));
      } catch (err) {
        loadingBubble.innerHTML = `<span style="color: var(--error);">Error procesando consulta: ${err.message}</span>`;
      }

      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });

    // Quick suggestion buttons
    document.querySelectorAll('.chat-suggestion-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        input.value = btn.textContent.replace(/^"|"$/g, '').trim();
        form.dispatchEvent(new Event('submit'));
      });
    });
  }

  // ================= DASHBOARD & KPIS =================
  async loadDashboard() {
    try {
      const stats = await api.getDashboardStats();
      const logs = await api.getAuditLogs(15);

      document.getElementById('stat-total-docs').textContent = stats.total_documents;
      document.getElementById('stat-total-repos').textContent = stats.total_repositories;
      document.getElementById('stat-total-storage').textContent = formatBytes(stats.total_storage_bytes);

      const completed = stats.status_counts['COMPLETED'] || 0;
      const total = stats.total_documents || 1;
      const rate = Math.round((completed / total) * 100);
      document.getElementById('stat-success-rate').textContent = `${rate}%`;

      // Render category progress bars
      const catContainer = document.getElementById('dashboard-categories-list');
      catContainer.innerHTML = '';

      stats.categories.forEach(cat => {
        const catName = CATEGORY_NAMES[cat.category] || cat.category;
        const row = document.createElement('div');
        row.style.marginBottom = '1rem';
        row.innerHTML = `
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.25rem;">
            <span>${catName}</span>
            <span style="font-weight: 600;">${cat.count} (${cat.percentage}%)</span>
          </div>
          <div class="progress-meter">
            <div class="progress-fill" style="width: ${cat.percentage}%;"></div>
          </div>
        `;
        catContainer.appendChild(row);
      });

      // Render format chips
      const fmtContainer = document.getElementById('dashboard-formats-list');
      fmtContainer.innerHTML = '';
      stats.formats.forEach(f => {
        const chip = document.createElement('div');
        chip.className = 'glass-card';
        chip.style.cssText = 'padding: 0.8rem 1.25rem; display: flex; align-items: center; justify-content: space-between;';
        chip.innerHTML = `
          <span style="font-weight: 600;">${f.extension}</span>
          <span class="badge badge-info">${f.count} archivos</span>
        `;
        fmtContainer.appendChild(chip);
      });

      // Render Audit Log table
      const logBody = document.getElementById('dashboard-logs-body');
      logBody.innerHTML = '';
      logs.forEach(l => {
        const tr = document.createElement('tr');
        const statusBadge = l.status === 'SUCCESS' 
          ? '<span class="badge badge-success">OK</span>' 
          : l.status === 'WARNING' ? '<span class="badge badge-warning">WARN</span>' 
          : '<span class="badge badge-error">ERR</span>';

        tr.innerHTML = `
          <td style="padding: 0.6rem; border-bottom: 1px solid var(--border-color); font-size: 0.8rem; color: var(--text-muted);">${l.timestamp}</td>
          <td style="padding: 0.6rem; border-bottom: 1px solid var(--border-color); font-weight: 600; font-size: 0.85rem;">${l.action}</td>
          <td style="padding: 0.6rem; border-bottom: 1px solid var(--border-color);">${statusBadge}</td>
          <td style="padding: 0.6rem; border-bottom: 1px solid var(--border-color); font-size: 0.82rem; color: var(--text-secondary);">${l.details || ''}</td>
        `;
        logBody.appendChild(tr);
      });

    } catch (err) {
      console.error('Error cargando dashboard:', err);
    }
  }

  // ================= NOTEBOOKLM STUDIO =================
  bindNotebookEvents() {
    // Select all sources
    const btnSelectAll = document.getElementById('btn-notebook-select-all');
    if (btnSelectAll) {
      btnSelectAll.addEventListener('click', () => {
        this.notebookSources.forEach(s => this.selectedNotebookSources.add(s.id));
        this.renderNotebookSources();
      });
    }

    // Clear all sources
    const btnClearAll = document.getElementById('btn-notebook-clear-all');
    if (btnClearAll) {
      btnClearAll.addEventListener('click', () => {
        this.selectedNotebookSources.clear();
        this.renderNotebookSources();
      });
    }

    // Clear chat session
    const btnClearChat = document.getElementById('btn-clear-notebook-chat');
    if (btnClearChat) {
      btnClearChat.addEventListener('click', () => {
        const msgContainer = document.getElementById('notebook-messages');
        if (msgContainer) {
          msgContainer.innerHTML = `
            <div class="notebook-welcome-banner">
              <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📓</div>
              <h3 style="font-size: 1.1rem; margin-bottom: 0.4rem;">Nueva Sesión de NotebookLM Studio</h3>
              <p style="font-size: 0.85rem; color: var(--text-muted); max-width: 580px; margin: 0 auto 1rem auto; line-height: 1.5;">
                Selecciona tus fuentes en el panel izquierdo y escribe una consulta o genera una guía de estudio con citas verificadas.
              </p>
              <div style="font-size: 0.78rem; color: var(--accent-primary); display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <span>⚡ Grounding Estricto</span>
                <span>•</span>
                <span>📑 Citas Interactivas</span>
                <span>•</span>
                <span>🧠 Contexto Masivo 1M Tokens</span>
              </div>
            </div>
          `;
        }
      });
    }

    // Action Pills (Study Guide, FAQ, Comparison, Briefing, Timeline)
    document.querySelectorAll('.notebook-action-btn[data-mode]').forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-mode');
        this.executeNotebookQuery(mode, '');
      });
    });

    // Chat Form Submit
    const formChat = document.getElementById('notebook-chat-form');
    const inputQuery = document.getElementById('notebook-query-input');
    if (formChat && inputQuery) {
      formChat.addEventListener('submit', (e) => {
        e.preventDefault();
        const q = inputQuery.value.trim();
        if (!q) return;
        inputQuery.value = '';
        this.executeNotebookQuery('chat', q);
      });
    }
  }

  async loadNotebookStudio() {
    try {
      let sources = await api.getNotebookSources(this.currentRepoId);
      // If current repo has no documents, fallback to all documents in the workspace
      if ((!sources || sources.length === 0) && this.currentRepoId) {
        sources = await api.getNotebookSources(null);
      }
      this.notebookSources = sources || [];

      // By default, if nothing is selected yet, select first 4 sources for immediate delight
      if (this.selectedNotebookSources.size === 0 && this.notebookSources.length > 0) {
        this.notebookSources.slice(0, 4).forEach(s => this.selectedNotebookSources.add(s.id));
      }

      this.renderNotebookSources();
    } catch (err) {
      console.error('Error cargando fuentes de NotebookLM:', err);
      const container = document.getElementById('notebook-sources-list');
      if (container) {
        container.innerHTML = `
          <div style="text-align: center; padding: 2rem 1rem; color: var(--error); font-size: 0.8rem;">
            ⚠️ No se pudieron cargar las fuentes.<br>
            <span style="font-size: 0.72rem; color: var(--text-muted);">${err.message}</span><br>
            <button type="button" class="btn-secondary" style="margin-top: 0.6rem; font-size: 0.75rem; padding: 0.3rem 0.8rem;" onclick="window.docuMind.loadNotebookStudio()">Reintentar</button>
          </div>
        `;
      }
      showToast('Error cargando fuentes para NotebookLM Studio: ' + err.message, 'error');
    }
  }

  renderNotebookSources() {
    const container = document.getElementById('notebook-sources-list');
    if (!container) return;

    container.innerHTML = '';
    if (this.notebookSources.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 2rem 1rem; color: var(--text-muted); font-size: 0.8rem;">
          No hay documentos procesados en este repositorio.<br>Sube archivos primero.
        </div>
      `;
      this.updateNotebookContextStats();
      return;
    }

    this.notebookSources.forEach(s => {
      const isSelected = this.selectedNotebookSources.has(s.id);
      const catClass = CATEGORY_CLASSES[s.category] || 'cat-tech';
      const catName = CATEGORY_NAMES[s.category] || s.category;

      const item = document.createElement('div');
      item.className = `notebook-source-item ${isSelected ? 'selected' : ''}`;
      item.innerHTML = `
        <input type="checkbox" id="nb-src-${s.id}" ${isSelected ? 'checked' : ''}>
        <div class="notebook-source-info">
          <div class="notebook-source-title" title="${s.original_filename}">${s.original_filename}</div>
          <div class="notebook-source-meta">
            <span class="cat-tag ${catClass}" style="font-size: 0.65rem; padding: 1px 5px;">${catName}</span>
            <span>•</span>
            <span>${(s.word_count || 0).toLocaleString()} palabras</span>
          </div>
          <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.2rem; line-height: 1.35;">
            ${s.summary_snippet}
          </div>
        </div>
      `;

      const chk = item.querySelector('input[type="checkbox"]');
      chk.addEventListener('change', (e) => {
        e.stopPropagation();
        if (chk.checked) {
          this.selectedNotebookSources.add(s.id);
          item.classList.add('selected');
        } else {
          this.selectedNotebookSources.delete(s.id);
          item.classList.remove('selected');
        }
        this.updateNotebookContextStats();
      });

      item.addEventListener('click', (e) => {
        if (e.target !== chk) {
          chk.checked = !chk.checked;
          chk.dispatchEvent(new Event('change'));
        }
      });

      container.appendChild(item);
    });

    this.updateNotebookContextStats();
  }

  updateNotebookContextStats() {
    let totalWords = 0;
    this.notebookSources.forEach(s => {
      if (this.selectedNotebookSources.has(s.id)) {
        totalWords += (s.word_count || 0);
      }
    });

    const count = this.selectedNotebookSources.size;
    const countBadge = document.getElementById('notebook-selected-count-badge');
    const wordsDisplay = document.getElementById('notebook-total-words-display');
    const statusDisplay = document.getElementById('notebook-context-status');

    if (countBadge) countBadge.textContent = `${count} activa${count === 1 ? '' : 's'}`;
    if (wordsDisplay) wordsDisplay.textContent = `~${totalWords.toLocaleString()} palabras`;
    if (statusDisplay) {
      statusDisplay.textContent = count > 0 
        ? `${count} fuente${count === 1 ? '' : 's'} activa${count === 1 ? '' : 's'} (~${totalWords.toLocaleString()} palabras analizadas)`
        : '0 fuentes seleccionadas (selecciona documentos a la izquierda)';
    }
  }

  async executeNotebookQuery(mode, query) {
    if (this.selectedNotebookSources.size === 0) {
      showToast('Por favor selecciona al menos una fuente documental en el panel izquierdo.', 'warning');
      return;
    }

    const messagesArea = document.getElementById('notebook-messages');
    const submitBtn = document.getElementById('btn-submit-notebook');
    const queryInput = document.getElementById('notebook-query-input');

    // Remove welcome banner if present
    const banner = messagesArea.querySelector('.notebook-welcome-banner');
    if (banner) banner.remove();

    // Append User message or Action badge
    const modeTitles = {
      'study_guide': '📑 Generar Guía de Estudio Completa',
      'faq': '❓ Preguntas Frecuentes (FAQ) de las Fuentes',
      'comparison': '📋 Matriz Comparativa de Fuentes',
      'briefing': '🎙️ Briefing Ejecutivo (Audio Script)',
      'timeline': '⏱️ Cronología e Hitos Principales',
      'chat': query
    };

    const userBubble = document.createElement('div');
    userBubble.className = 'notebook-user-query';
    userBubble.textContent = modeTitles[mode] || query;
    messagesArea.appendChild(userBubble);

    // Append Loading State Card
    const loadingCard = document.createElement('div');
    loadingCard.id = 'notebook-loading-card';
    loadingCard.className = 'notebook-response-card';
    loadingCard.style.cssText = 'border-color: var(--accent-primary); display: flex; align-items: center; gap: 0.8rem;';
    loadingCard.innerHTML = `
      <span class="badge-pulse" style="width: 14px; height: 14px; background: var(--accent-primary); display: inline-block; border-radius: 50%;"></span>
      <span style="font-size: 0.88rem; color: var(--text-primary);">
        Analizando <strong>${this.selectedNotebookSources.size} fuentes</strong> con <strong>Google Gemini 1.5 Flash</strong> (Grounding estricto)...
      </span>
    `;
    messagesArea.appendChild(loadingCard);
    messagesArea.scrollTop = messagesArea.scrollHeight;

    if (submitBtn) submitBtn.disabled = true;
    if (queryInput) queryInput.disabled = true;

    try {
      const docIds = Array.from(this.selectedNotebookSources);
      const res = await api.queryNotebook(docIds, query, mode);

      loadingCard.remove();

      // Render Response Card
      const respCard = document.createElement('div');
      respCard.className = 'notebook-response-card';

      const modeHeader = mode === 'chat' 
        ? `Consulta Grounded (${res.sources_used.length} fuentes)`
        : (modeTitles[mode] || mode.toUpperCase());

      let citationsHtml = '';
      if (res.citations && res.citations.length > 0) {
        citationsHtml = `
          <div class="notebook-citations-tray">
            <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted);">Fuentes Vinculadas:</span>
            ${res.citations.map(c => `
              <button type="button" class="citation-pill" title="Clic para ver fragmento fuente: ${c.quote}">
                <span>📄</span> ${c.document_name}
              </button>
            `).join('')}
          </div>
        `;
      }

      respCard.innerHTML = `
        <div class="notebook-response-header">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <strong style="color: var(--text-primary); font-size: 0.86rem;">${modeHeader}</strong>
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="badge" style="background: rgba(99, 102, 241, 0.15); color: var(--accent-primary); font-size: 0.68rem; font-weight: 700;">
              ${res.model_used}
            </span>
            <span style="font-size: 0.72rem; color: var(--text-muted);">
              ~${res.total_words_analyzed.toLocaleString()} palabras
            </span>
          </div>
        </div>

        <div class="notebook-response-content">
          ${renderMarkdown(res.answer)}
        </div>

        ${citationsHtml}
      `;

      // Interactive click on citation pill to show quote preview
      if (res.citations && res.citations.length > 0) {
        respCard.querySelectorAll('.citation-pill').forEach((btn, idx) => {
          btn.addEventListener('click', () => {
            const cit = res.citations[idx];
            showToast(`Cita de ${cit.document_name}: "${cit.quote}"`, 'info');
          });
        });
      }

      messagesArea.appendChild(respCard);
      messagesArea.scrollTop = messagesArea.scrollHeight;

    } catch (err) {
      loadingCard.remove();
      const errCard = document.createElement('div');
      errCard.className = 'notebook-response-card';
      errCard.style.borderColor = 'var(--error)';
      errCard.innerHTML = `
        <div style="color: var(--error); font-weight: 600; margin-bottom: 0.3rem;">❌ Error en el procesamiento del cuaderno:</div>
        <div style="font-size: 0.85rem; color: var(--text-secondary);">${err.message}</div>
      `;
      messagesArea.appendChild(errCard);
      showToast(err.message, 'error');
    } finally {
      if (submitBtn) submitBtn.disabled = false;
      if (queryInput) {
        queryInput.disabled = false;
        queryInput.focus();
      }
    }
  }
}

// Instantiate App on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.docuMind = new DocuMindApp();
});
