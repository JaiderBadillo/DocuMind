// ==========================================================================
// DOCUMIND API CLIENT - FETCH WRAPPER & JWT AUTH MANAGEMENT
// ==========================================================================

const API_BASE = '/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('documind_token') || null;
    this.user = JSON.parse(localStorage.getItem('documind_user') || 'null');
  }

  setSession(token, user) {
    this.token = token;
    this.user = user;
    localStorage.setItem('documind_token', token);
    localStorage.setItem('documind_user', JSON.stringify(user));
  }

  clearSession() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('documind_token');
    localStorage.removeItem('documind_user');
  }

  isAuthenticated() {
    return !!this.token;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = options.headers || {};

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    // If body is not FormData, default to JSON
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401) {
        this.clearSession();
        window.dispatchEvent(new CustomEvent('auth:expired'));
        throw new Error('Sesión expirada o no autorizada');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error en la petición (${response.status})`);
      }

      // If downloading file, handle blob
      const contentType = response.headers.get('content-type');
      if (contentType && (contentType.includes('application/pdf') || contentType.includes('application/octet-stream') || contentType.includes('application/vnd.openxmlformats'))) {
        return await response.blob();
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error on [${url}]:`, err);
      throw err;
    }
  }

  // --- Auth Endpoints ---
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  async register(email, fullName, password) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, full_name: fullName, password })
    });
    this.setSession(data.access_token, data.user);
    return data;
  }

  async getProfile() {
    return await this.request('/auth/me');
  }

  async getGeminiKeyStatus() {
    return await this.request('/auth/gemini-key');
  }

  async setGeminiKey(apiKey) {
    return await this.request('/auth/gemini-key', {
      method: 'POST',
      body: JSON.stringify({ api_key: apiKey })
    });
  }

  // --- Repository Endpoints ---
  async getRepositories() {
    return await this.request('/repositories');
  }

  async createRepository(name, description = '') {
    return await this.request('/repositories', {
      method: 'POST',
      body: JSON.stringify({ name, description })
    });
  }

  async deleteRepository(repoId) {
    return await this.request(`/repositories/${repoId}`, {
      method: 'DELETE'
    });
  }

  // --- Document Endpoints ---
  async getDocuments(params = {}) {
    const query = new URLSearchParams();
    if (params.repository_id) query.append('repository_id', params.repository_id);
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    
    const qs = query.toString() ? `?${query.toString()}` : '';
    return await this.request(`/documents${qs}`);
  }

  async uploadDocuments(repositoryId, files) {
    const formData = new FormData();
    formData.append('repository_id', repositoryId);
    for (const file of files) {
      formData.append('files', file);
    }

    return await this.request('/documents/upload', {
      method: 'POST',
      body: formData
    });
  }

  async getDocumentDetail(docId) {
    return await this.request(`/documents/${docId}`);
  }

  async deleteDocument(docId) {
    return await this.request(`/documents/${docId}`, {
      method: 'DELETE'
    });
  }

  async reprocessDocument(docId) {
    return await this.request(`/documents/${docId}/reprocess`, {
      method: 'POST'
    });
  }

  downloadDocumentUrl(docId) {
    return `${API_BASE}/documents/${docId}/download`;
  }

  // --- Search & RAG ---
  async search(query, repositoryId = null, category = null, format = null) {
    const qs = new URLSearchParams({ q: query });
    if (repositoryId) qs.append('repository_id', repositoryId);
    if (category) qs.append('category', category);
    if (format) qs.append('format', format);
    return await this.request(`/search?${qs.toString()}`);
  }

  async ragChat(query, repositoryId = null) {
    return await this.request('/rag/chat', {
      method: 'POST',
      body: JSON.stringify({ query, repository_id: repositoryId })
    });
  }

  // --- Dashboard & Metrics ---
  async getDashboardStats() {
    return await this.request('/dashboard/stats');
  }

  async getAuditLogs(limit = 20) {
    return await this.request(`/dashboard/logs?limit=${limit}`);
  }

  // --- NotebookLM Studio ---
  async getNotebookSources(repositoryId = null) {
    const qs = repositoryId ? `?repository_id=${repositoryId}` : '';
    return await this.request(`/notebook/sources${qs}`);
  }

  async queryNotebook(documentIds, query = '', mode = 'chat') {
    return await this.request('/notebook/chat', {
      method: 'POST',
      body: JSON.stringify({
        document_ids: documentIds,
        query: query,
        mode: mode
      })
    });
  }
}

export const api = new ApiClient();
