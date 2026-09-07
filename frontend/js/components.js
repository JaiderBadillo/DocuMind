// ==========================================================================
// DOCUMIND COMPONENTS - UI RENDERERS, MODALS & TOAST NOTIFICATIONS
// ==========================================================================

export const CATEGORY_NAMES = {
  'LEGAL_CONTRACTS': 'Legal y Contratos',
  'FINANCE_INVOICES': 'Finanzas y Facturas',
  'HR_PROFILES': 'Talento Humano / CV',
  'TECH_REPORTS': 'Informes Técnicos',
  'SIN_CLASIFICAR': 'Sin Clasificar'
};

export const CATEGORY_CLASSES = {
  'LEGAL_CONTRACTS': 'cat-legal',
  'FINANCE_INVOICES': 'cat-finance',
  'HR_PROFILES': 'cat-hr',
  'TECH_REPORTS': 'cat-tech',
  'SIN_CLASIFICAR': 'cat-tech'
};

export function formatBytes(bytes, decimals = 1) {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Toast notification helper
export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `glass-card toast toast-${type}`;
  toast.style.cssText = `
    padding: 0.85rem 1.25rem;
    margin-top: 0.5rem;
    border-radius: 8px;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    animation: slideIn 0.3s ease;
    border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#6366f1'};
    background: var(--bg-secondary);
    color: var(--text-primary);
  `;
  
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.id = 'toast-container';
  div.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column;';
  document.body.appendChild(div);
  return div;
}

export function renderMarkdown(text) {
  if (!text) return '';
  
  let html = text;

  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, '<pre style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px; overflow-x: auto; font-size: 0.82rem; margin: 0.5rem 0;"><code>$1</code></pre>');
  html = html.replace(/`([^`]+)`/g, '<code style="background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px; font-size: 0.85em; font-family: monospace;">$1</code>');

  // Headers
  html = html.replace(/^#### (.*$)/gim, '<h5 style="color: var(--accent-secondary); margin-top: 0.6rem; margin-bottom: 0.25rem; font-size: 0.9rem; font-weight: 700;">$1</h5>');
  html = html.replace(/^### (.*$)/gim, '<h4 style="color: var(--accent-secondary); margin-top: 0.75rem; margin-bottom: 0.35rem; font-size: 0.98rem; font-weight: 700;">$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3 style="color: var(--text-primary); margin-top: 0.9rem; margin-bottom: 0.45rem; font-size: 1.1rem; font-weight: 700;">$1</h3>');
  html = html.replace(/^# (.*$)/gim, '<h2 style="color: var(--text-primary); margin-top: 1rem; margin-bottom: 0.5rem; font-size: 1.25rem; font-weight: 700;">$1</h2>');

  // Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Blockquotes
  html = html.replace(/^> (.*$)/gim, '<blockquote style="border-left: 3px solid var(--accent-primary); margin: 0.5rem 0; color: var(--text-secondary); font-style: italic; background: rgba(99, 102, 241, 0.05); padding: 0.5rem 0.8rem; border-radius: 0 6px 6px 0;">$1</blockquote>');

  // Citations [Fuente: ...] or [1]
  html = html.replace(/\[(Fuente: [^\]]+)\]/g, '<span class="citation-pill" style="font-size:0.7rem; padding: 2px 6px; vertical-align: middle;">📑 $1</span>');
  html = html.replace(/\[(\d+)\]/g, '<span class="citation-pill" style="font-size:0.7rem; padding: 1px 5px; vertical-align: middle;">[$1]</span>');

  // Simple Markdown Table support
  const tableRegex = /((?:\|[^\n]+\|\r?\n)+)/g;
  html = html.replace(tableRegex, (match) => {
    const lines = match.trim().split(/\r?\n/).filter(l => l.trim().length > 0);
    if (lines.length < 2) return match;
    let tableHtml = '<div style="overflow-x: auto; margin: 0.75rem 0;"><table style="width:100%; border-collapse: collapse; font-size: 0.82rem;">';
    lines.forEach((line, idx) => {
      if (line.includes('---')) return;
      const cols = line.split('|').map(c => c.trim()).filter((_, i, arr) => i > 0 && i < arr.length - 1);
      if (idx === 0) {
        tableHtml += '<tr style="background: var(--bg-tertiary); font-weight: 600;">' + cols.map(c => `<th style="border: 1px solid var(--border-color); padding: 0.45rem 0.65rem; text-align: left;">${c}</th>`).join('') + '</tr>';
      } else {
        tableHtml += '<tr>' + cols.map(c => `<td style="border: 1px solid var(--border-color); padding: 0.45rem 0.65rem;">${c}</td>`).join('') + '</tr>';
      }
    });
    tableHtml += '</table></div>';
    return tableHtml;
  });

  // Bullets
  html = html.replace(/^[\*\-•] (.*$)/gim, '<div style="margin-left: 0.8rem; margin-bottom: 0.3rem;">• $1</div>');
  html = html.replace(/\n\n/g, '<div style="height: 0.45rem;"></div>');
  html = html.replace(/\n/g, '<br>');

  return html;
}

// Render Document Card
export function renderDocumentCard(doc, onSelect, onDelete) {
  const ext = doc.file_extension ? doc.file_extension.replace('.', '').toLowerCase() : 'txt';
  const iconClass = ext === 'pdf' ? 'pdf' : ext === 'docx' ? 'docx' : 'txt';
  const catLabel = CATEGORY_NAMES[doc.category] || 'En análisis';
  const catClass = CATEGORY_CLASSES[doc.category] || 'cat-tech';

  let statusBadge = '';
  if (doc.processing_status === 'COMPLETED') {
    statusBadge = '<span class="badge badge-success">✓ IA Listo</span>';
  } else if (doc.processing_status === 'PROCESSING') {
    statusBadge = '<span class="badge badge-warning"><span class="badge-pulse"></span> Procesando</span>';
  } else if (doc.processing_status === 'FAILED') {
    statusBadge = '<span class="badge badge-error">⚠ Fallido</span>';
  } else {
    statusBadge = '<span class="badge badge-info">⏳ Pendiente</span>';
  }

  // Highlighted snippet or summary display
  let bodyContent = '';
  if (doc.search_snippet) {
    bodyContent = `
      <div style="font-size: 0.8rem; background: rgba(99, 102, 241, 0.08); padding: 0.5rem 0.65rem; border-radius: 6px; border-left: 3px solid var(--accent-primary); line-height: 1.45;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
          <strong style="color: var(--accent-secondary); font-size: 0.75rem;">Coincidencia en contenido:</strong>
          <span style="font-size: 0.72rem; color: var(--accent-primary); font-weight: 600;">${Math.round((doc.relevance || 0.9) * 100)}% Relevancia</span>
        </div>
        <span style="color: var(--text-primary);">${doc.search_snippet}</span>
      </div>
    `;
  } else {
    const cleanSummary = doc.summary ? doc.summary.replace(/###.*?\n/g, '').replace(/\*\*/g, '').replace(/•/g, '• ') : 'Extrayendo contenido semántico con IA...';
    bodyContent = `
      <div class="doc-summary-snippet">
        ${cleanSummary}
      </div>
    `;
  }

  const card = document.createElement('div');
  card.className = 'doc-card';
  card.innerHTML = `
    <div class="doc-card-header">
      <div class="file-icon ${iconClass}">${ext.toUpperCase()}</div>
      <div class="doc-meta">
        <div class="doc-title" title="${doc.original_filename}">${doc.original_filename}</div>
        <div class="doc-sub">${formatBytes(doc.file_size_bytes)} • ${doc.created_at}</div>
      </div>
    </div>
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <span class="cat-tag ${catClass}">${catLabel}</span>
      ${statusBadge}
    </div>
    ${bodyContent}
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 0.5rem; border-top: 1px solid var(--border-color);">
      <button class="btn-secondary btn-view" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">🔍 Ver Análisis</button>
      <button class="btn-icon btn-delete" title="Eliminar documento" style="color: var(--error);">🗑️</button>
    </div>
  `;

  card.querySelector('.btn-view').addEventListener('click', (e) => {
    e.stopPropagation();
    onSelect(doc.id);
  });

  card.querySelector('.btn-delete').addEventListener('click', (e) => {
    e.stopPropagation();
    if (confirm(`¿Está seguro de eliminar "${doc.original_filename}"?`)) {
      onDelete(doc.id);
    }
  });

  card.addEventListener('click', () => onSelect(doc.id));
  return card;
}

// Render Document Detail Modal (Split View)
export function renderDocumentModal(doc, onReprocess, downloadUrl) {
  const meta = doc.metadata || {};
  const entities = meta.extracted_entities || {};
  const catLabel = CATEGORY_NAMES[meta.category] || doc.category || 'Sin Clasificar';
  const catClass = CATEGORY_CLASSES[meta.category] || 'cat-tech';

  let entitiesRows = '';
  if (Object.keys(entities).length > 0) {
    entitiesRows = Object.entries(entities).map(([k, v]) => {
      const val = Array.isArray(v) ? v.join(', ') : (typeof v === 'object' ? JSON.stringify(v) : v);
      return `
        <tr>
          <td style="font-weight: 600; text-transform: capitalize; color: var(--text-secondary); width: 35%;">${k.replace(/_/g, ' ')}</td>
          <td style="color: var(--text-primary); font-family: monospace;">${val}</td>
        </tr>
      `;
    }).join('');
  } else {
    entitiesRows = '<tr><td colspan="2" style="text-align: center; color: var(--text-muted);">No se detectaron entidades específicas.</td></tr>';
  }

  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <div>
          <h3 style="font-size: 1.15rem; margin-bottom: 0.2rem;">${doc.original_filename}</h3>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Tamaño: ${formatBytes(doc.file_size_bytes)} | Formato: ${doc.file_extension}</span>
        </div>
        <button class="btn-icon btn-close" style="font-size: 1.2rem;">✕</button>
      </div>
      <div class="modal-body">
        <div class="viewer-split">
          <!-- Columna Izquierda: Vista Previa y Datos Generales -->
          <div>
            <div class="viewer-section-title">📄 Contenido Extraído</div>
            <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-sm); max-height: 380px; overflow-y: auto; font-family: monospace; font-size: 0.8rem; white-space: pre-wrap; line-height: 1.5; color: var(--text-secondary); border: 1px solid var(--border-color);">
              ${doc.raw_text || 'Sin texto extraído.'}
            </div>
          </div>

          <!-- Columna Derecha: Inteligencia Artificial y Entidades -->
          <div>
            <div class="viewer-section-title">🤖 Análisis de Inteligencia Artificial</div>
            
            <div style="margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between;">
              <span class="cat-tag ${catClass}" style="font-size: 0.85rem; padding: 0.35rem 0.85rem;">
                ${catLabel} (${Math.round((meta.category_confidence || 0.95) * 100)}% Confianza)
              </span>
              <span style="font-size: 0.78rem; color: var(--text-muted);">${meta.word_count || 0} palabras analizadas</span>
            </div>

            <div style="margin-bottom: 1.25rem;">
              <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.4rem;">Resumen Ejecutivo:</div>
              <div style="background: rgba(99, 102, 241, 0.06); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: var(--radius-sm); padding: 0.85rem; font-size: 0.85rem; line-height: 1.6;">
                ${renderMarkdown(meta.executive_summary || 'Generando síntesis con IA...')}
              </div>
            </div>

            <div>
              <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.4rem;">Entidades Estructuradas Extraídas:</div>
              <table class="entities-table">
                <tbody>
                  ${entitiesRows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <a href="${downloadUrl}" target="_blank" class="btn-secondary" style="display: inline-flex; align-items: center; gap: 0.4rem;">📥 Descargar Original</a>
        <button class="btn-secondary btn-reprocess">🔄 Reprocesar con IA</button>
        <button class="btn-primary btn-close" style="width: auto;">Aceptar</button>
      </div>
    </div>
  `;

  modal.querySelectorAll('.btn-close').forEach(btn => {
    btn.addEventListener('click', () => modal.remove());
  });

  modal.querySelector('.btn-reprocess').addEventListener('click', () => {
    onReprocess(doc.id);
    modal.remove();
  });

  return modal;
}

// Render RAG Chat Message
export function renderChatMessage(msg) {
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${msg.sender}`;

  if (msg.sender === 'user') {
    bubble.textContent = msg.text;
  } else {
    let sourcesHtml = '';
    if (msg.sources && msg.sources.length > 0) {
      sourcesHtml = `
        <div class="sources-card">
          <div style="font-weight: 600; margin-bottom: 0.25rem; font-size: 0.78rem;">📚 Fuentes Consultadas:</div>
          ${msg.sources.map(s => `
            <div style="margin-bottom: 0.35rem;">
              <strong>${s.document_name}</strong> (${Math.round(s.relevance_score * 100)}% relevancia)
              <div style="font-style: italic; color: var(--text-secondary); margin-top: 0.15rem;">"${s.excerpt}"</div>
            </div>
          `).join('')}
        </div>
      `;
    }

    bubble.innerHTML = `
      <div>${msg.text.replace(/\n/g, '<br>')}</div>
      ${sourcesHtml}
      <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.4rem; text-align: right;">
        Modelo: ${msg.model || 'DocuMind RAG Engine'}
      </div>
    `;
  }

  return bubble;
}
