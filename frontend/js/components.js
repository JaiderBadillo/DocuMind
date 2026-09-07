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

// Render Document Detail Modal (Word-like Rich WYSIWYG Editor & Gemini Copilot Studio)
export function renderDocumentModal(doc, onReprocess, downloadUrl, onSaveText, onAiEdit, onUploadImage) {
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

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Convert markdown tables and plain text lines into rich HTML
  function convertMarkdownOrTextToHtml(text) {
    if (!text) return '<p></p>';
    if (text.includes('<table') || text.includes('<p>') || text.includes('<h1>')) {
      return text;
    }
    const lines = text.split('\n');
    const out = [];
    let tableBuf = [];

    function flushTbl(buf) {
      if (!buf.length) return '';
      let res = '<table class="doc-table"><thead><tr>';
      const headers = buf[0].split('|').map(c => c.trim()).filter(Boolean);
      headers.forEach(h => { res += `<th>${escapeHtml(h)}</th>`; });
      res += '</tr></thead><tbody>';
      for (let i = 1; i < buf.length; i++) {
        if (/^\s*\|?[-:\s|]+\|?\s*$/.test(buf[i])) continue;
        const cells = buf[i].split('|').map(c => c.trim()).filter(Boolean);
        if (cells.length) {
          res += '<tr>' + cells.map(c => `<td>${escapeHtml(c)}</td>`).join('') + '</tr>';
        }
      }
      res += '</tbody></table>';
      return res;
    }

    for (const line of lines) {
      const s = line.trim();
      if (s.includes('|') && s.split('|').length >= 3) {
        tableBuf.push(s);
      } else {
        if (tableBuf.length) {
          out.push(flushTbl(tableBuf));
          tableBuf = [];
        }
        if (s.startsWith('# ')) {
          out.push(`<h1>${escapeHtml(s.slice(2).trim())}</h1>`);
        } else if (s.startsWith('## ')) {
          out.push(`<h2>${escapeHtml(s.slice(3).trim())}</h2>`);
        } else if (s.startsWith('### ')) {
          out.push(`<h3>${escapeHtml(s.slice(4).trim())}</h3>`);
        } else if (s.startsWith('• ') || s.startsWith('- ') || s.startsWith('* ')) {
          out.push(`<ul><li>${escapeHtml(s.slice(2).trim())}</li></ul>`);
        } else if (s) {
          out.push(`<p>${escapeHtml(s)}</p>`);
        }
      }
    }
    if (tableBuf.length) out.push(flushTbl(tableBuf));
    return out.join('\n');
  }

  const initialHtml = doc.content_html && doc.content_html.trim() 
    ? doc.content_html 
    : convertMarkdownOrTextToHtml(doc.raw_text || '');
  const undoStack = [initialHtml];

  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-content modal-editor-xl">
      <!-- Modal Header -->
      <div class="modal-header">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div>
            <h3 style="font-size: 1.15rem; margin-bottom: 0.2rem; display: flex; align-items: center; gap: 0.5rem;">
              <span>📄</span> ${escapeHtml(doc.original_filename)}
              <span id="unsaved-indicator" class="badge" style="background: rgba(239, 68, 68, 0.15); color: var(--error); font-size: 0.72rem; display: none;">● Cambios sin guardar</span>
            </h3>
            <span style="font-size: 0.78rem; color: var(--text-muted);">
              Formato: ${doc.file_extension} | Tamaño: ${formatBytes(doc.file_size_bytes)} | Categoría: ${catLabel}
            </span>
          </div>
        </div>

        <!-- Pestañas centrales -->
        <div class="editor-header-tabs">
          <button id="tab-btn-editor" class="editor-tab-btn active">
            <span>📝</span> Editor & Copilot IA
          </button>
          <button id="tab-btn-analysis" class="editor-tab-btn">
            <span>📊</span> Análisis & Entidades
          </button>
        </div>

        <button class="btn-icon btn-close" style="font-size: 1.2rem;">✕</button>
      </div>

      <!-- PESTAÑA 1: Editor de Texto Word-like & Gemini Copilot -->
      <div id="tab-content-editor" class="modal-body" style="padding: 0.75rem; height: calc(100% - 130px);">
        <div class="editor-workspace">
          
          <!-- Columna Izquierda: Lienzo Word-like -->
          <div class="editor-sheet-container">
            <!-- Barra de Herramientas -->
            <div class="editor-toolbar">
              <!-- Formato de Texto -->
              <div class="editor-tool-group">
                <button class="editor-tool-btn" data-tool="bold" title="Negrita (Ctrl+B)"><b>B</b></button>
                <button class="editor-tool-btn" data-tool="italic" title="Cursiva (Ctrl+I)"><i>I</i></button>
                <button class="editor-tool-btn" data-tool="h1" title="Encabezado H1">H1</button>
                <button class="editor-tool-btn" data-tool="h2" title="Subtítulo H2">H2</button>
                <button class="editor-tool-btn" data-tool="bullet" title="Lista con viñetas">• Lista</button>
              </div>

              <!-- Herramientas de Tablas e Imágenes -->
              <div class="editor-tool-group">
                <button id="btn-insert-table" class="editor-tool-btn" title="Insertar nueva tabla">📊 Tabla</button>
                <button id="btn-add-table-row" class="editor-tool-btn" title="Agregar fila a la tabla">+ Fila</button>
                <button id="btn-add-table-col" class="editor-tool-btn" title="Agregar columna a la tabla">+ Col</button>
                <button id="btn-insert-image" class="editor-tool-btn" title="Subir e insertar imagen">🖼️ Imagen</button>
                <input type="file" id="editor-image-file-input" accept="image/png,image/jpeg,image/webp,image/gif" style="display: none;">
              </div>

              <div class="editor-tool-group" style="flex-grow: 1; min-width: 120px;">
                <input type="text" id="editor-find-input" placeholder="🔍 Buscar en texto..." 
                       style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-primary); color: var(--text-primary); width: 100%;">
              </div>

              <div style="display: flex; gap: 0.35rem; align-items: center;">
                <button id="btn-undo-editor" class="editor-tool-btn" title="Deshacer último cambio">↩ Deshacer</button>
                <button id="btn-save-editor" class="btn-primary" style="padding: 0.35rem 0.85rem; font-size: 0.78rem; width: auto;">
                  💾 Guardar
                </button>
              </div>
            </div>

            <!-- Paper Sheet Canvas (WYSIWYG contenteditable) -->
            <div class="editor-paper-wrapper">
              <div id="doc-editor-sheet" class="doc-editor-sheet" contenteditable="true" spellcheck="true">${initialHtml}</div>
            </div>

            <!-- Statusbar -->
            <div class="editor-statusbar">
              <span id="editor-word-count">Palabras: 0 | Caracteres: 0</span>
              <span id="editor-save-status" style="color: var(--text-muted); font-size: 0.74rem;">Modo de Edición WYSIWYG Activo</span>
            </div>
          </div>

          <!-- Columna Derecha: Asistente Copilot con Google Gemini -->
          <div class="copilot-container">
            <div class="copilot-header">
              <div style="display: flex; align-items: center; gap: 0.45rem;">
                <span style="font-size: 1.15rem;">🤖</span>
                <div>
                  <strong style="font-size: 0.85rem;">Gemini Copilot de Documento</strong>
                  <div style="font-size: 0.7rem; color: var(--text-muted);">Asistente de redacción, tablas y análisis</div>
                </div>
              </div>
              <span class="badge" style="background: rgba(99, 102, 241, 0.15); color: var(--accent-secondary); font-size: 0.7rem;">Google Gemini</span>
            </div>

            <!-- Sugerencias Rápidas -->
            <div class="copilot-pills">
              <button class="copilot-pill" data-prompt="Crea una tabla con cronograma, etapas, responsables y plazos de entrega.">📊 Crear tabla cronograma</button>
              <button class="copilot-pill" data-prompt="Crea una tabla con desglose de costos, descripción, valor unitario y total en COP.">💰 Tabla de presupuesto</button>
              <button class="copilot-pill" data-prompt="Mejora la redacción, estilo formal y ortografía de este documento.">✍️ Mejorar redacción</button>
              <button class="copilot-pill" data-prompt="Redacta y agrega una cláusula penal por incumplimiento del 20% con términos comerciales estándar.">⚖️ Cláusula penal</button>
              <button class="copilot-pill" data-prompt="Redacta y agrega una cláusula de confidencialidad y reserva de información por 5 años.">🔒 Confidencialidad</button>
              <button class="copilot-pill" data-prompt="Genera una síntesis ejecutiva estructurada en viñetas para incluir al inicio del documento.">📑 Resumen</button>
            </div>

            <!-- Mensajes Copilot -->
            <div id="copilot-messages" class="copilot-messages">
              <div class="copilot-bubble bot">
                ¡Hola! Soy tu <strong>Gemini Copilot</strong> empotrado. Puedo redactar cláusulas, <strong>generar tablas estructuradas</strong>, mejorar redacciones o responder consultas. Lo que genere lo puedes insertar directamente en el documento con el botón <strong>⚡ Aplicar al Documento</strong>.
              </div>
            </div>

            <!-- Input Bar -->
            <form id="copilot-form" class="copilot-input-bar">
              <input type="text" id="copilot-input" class="form-control" 
                     placeholder="Pide un cambio o tabla a Gemini (ej: genera una tabla de costos)..." 
                     style="font-size: 0.8rem; padding: 0.45rem 0.75rem; border-radius: 6px;" required autocomplete="off">
              <button type="submit" class="btn-primary" style="width: auto; padding: 0.45rem 0.9rem; font-size: 0.8rem;">
                Enviar
              </button>
            </form>
          </div>

        </div>
      </div>

      <!-- PESTAÑA 2: Análisis de IA & Entidades Estructuradas (Vista clásica) -->
      <div id="tab-content-analysis" class="modal-body hidden" style="padding: 1.25rem;">
        <div class="viewer-split">
          <!-- Columna Izquierda: Vista Previa y Búsqueda -->
          <div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
              <div class="viewer-section-title" style="margin-bottom: 0;">📄 Contenido Extraído</div>
              <span id="doc-search-count" style="font-size: 0.75rem; color: var(--accent-secondary); font-weight: 600;"></span>
            </div>

            <!-- Buscador dentro del documento -->
            <div style="display: flex; gap: 0.35rem; margin-bottom: 0.5rem; align-items: center;">
              <input type="text" id="doc-keyword-search" class="form-control" 
                     placeholder="🔍 Buscar palabras clave dentro del texto..." 
                     style="font-size: 0.8rem; padding: 0.35rem 0.65rem; border-radius: var(--radius-sm); flex-grow: 1;">
              <button id="doc-search-prev" class="btn-secondary" title="Anterior coincidencia" style="padding: 0.35rem 0.55rem; font-size: 0.72rem; min-width: 28px;">▲</button>
              <button id="doc-search-next" class="btn-secondary" title="Siguiente coincidencia" style="padding: 0.35rem 0.55rem; font-size: 0.72rem; min-width: 28px;">▼</button>
              <button id="doc-search-clear" class="btn-icon" title="Limpiar búsqueda" style="font-size: 0.85rem; padding: 0.3rem;">✕</button>
            </div>

            <div id="doc-text-container" style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-sm); max-height: 480px; overflow-y: auto; font-family: monospace; font-size: 0.8rem; white-space: pre-wrap; line-height: 1.5; color: var(--text-secondary); border: 1px solid var(--border-color);">
              ${escapeHtml(doc.raw_text || '')}
            </div>
          </div>

          <!-- Columna Derecha: Análisis de IA -->
          <div>
            <div class="viewer-section-title">🤖 Análisis de Inteligencia Artificial</div>
            
            <div style="margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between;">
              <span class="cat-tag ${catClass}" style="font-size: 0.85rem; padding: 0.35rem 0.85rem;">
                ${catLabel} (${Math.round((meta.category_confidence || 0.95) * 100)}% Confianza)
              </span>
              <span id="analysis-word-count-badge" style="font-size: 0.78rem; color: var(--text-muted);">${meta.word_count || 0} palabras analizadas</span>
            </div>

            <div style="margin-bottom: 1.25rem;">
              <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.4rem;">Resumen Ejecutivo:</div>
              <div id="analysis-summary-box" style="background: rgba(99, 102, 241, 0.06); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: var(--radius-sm); padding: 0.85rem; font-size: 0.85rem; line-height: 1.6;">
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

      <!-- Modal Footer -->
      <div class="modal-footer">
        <a href="${downloadUrl}" target="_blank" class="btn-secondary" style="display: inline-flex; align-items: center; gap: 0.4rem;">📥 Descargar Original</a>
        <button class="btn-secondary btn-reprocess">🔄 Reprocesar con IA</button>
        <button class="btn-primary btn-close" style="width: auto;">Aceptar</button>
      </div>
    </div>
  `;

  // --- Element References ---
  const tabBtnEditor = modal.querySelector('#tab-btn-editor');
  const tabBtnAnalysis = modal.querySelector('#tab-btn-analysis');
  const tabContentEditor = modal.querySelector('#tab-content-editor');
  const tabContentAnalysis = modal.querySelector('#tab-content-analysis');

  const editorSheet = modal.querySelector('#doc-editor-sheet');
  const wordCountSpan = modal.querySelector('#editor-word-count');
  const unsavedIndicator = modal.querySelector('#unsaved-indicator');
  const btnSaveEditor = modal.querySelector('#btn-save-editor');
  const btnUndoEditor = modal.querySelector('#btn-undo-editor');
  const editorFindInput = modal.querySelector('#editor-find-input');
  const editorSaveStatus = modal.querySelector('#editor-save-status');

  const btnInsertTable = modal.querySelector('#btn-insert-table');
  const btnAddTableRow = modal.querySelector('#btn-add-table-row');
  const btnAddTableCol = modal.querySelector('#btn-add-table-col');
  const btnInsertImage = modal.querySelector('#btn-insert-image');
  const editorImageFileInput = modal.querySelector('#editor-image-file-input');

  const copilotMessages = modal.querySelector('#copilot-messages');
  const copilotForm = modal.querySelector('#copilot-form');
  const copilotInput = modal.querySelector('#copilot-input');
  const copilotPills = modal.querySelectorAll('.copilot-pill');

  let hasUnsavedChanges = false;

  // --- Tab Switching ---
  tabBtnEditor.addEventListener('click', () => {
    tabBtnEditor.classList.add('active');
    tabBtnAnalysis.classList.remove('active');
    tabContentEditor.classList.remove('hidden');
    tabContentAnalysis.classList.add('hidden');
  });

  tabBtnAnalysis.addEventListener('click', () => {
    tabBtnAnalysis.classList.add('active');
    tabBtnEditor.classList.remove('active');
    tabContentAnalysis.classList.remove('hidden');
    tabContentEditor.classList.add('hidden');
    const previewContainer = modal.querySelector('#doc-text-container');
    if (previewContainer) {
      previewContainer.textContent = editorSheet.innerText;
    }
  });

  // --- Word / Char Counting ---
  function updateCounters() {
    const text = editorSheet.innerText || '';
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    wordCountSpan.textContent = `Palabras: ${words} | Caracteres: ${chars}`;
  }
  updateCounters();

  // --- Editor Input Listener ---
  editorSheet.addEventListener('input', () => {
    hasUnsavedChanges = true;
    unsavedIndicator.style.display = 'inline-flex';
    editorSaveStatus.textContent = '● Cambios sin guardar';
    editorSaveStatus.style.color = 'var(--warning)';
    updateCounters();
  });

  // Save history on changes
  editorSheet.addEventListener('keyup', () => {
    if (undoStack.length === 0 || undoStack[undoStack.length - 1] !== editorSheet.innerHTML) {
      if (undoStack.length > 30) undoStack.shift();
      undoStack.push(editorSheet.innerHTML);
    }
  });

  // --- Basic Formatting Actions ---
  modal.querySelectorAll('.editor-tool-btn[data-tool]').forEach(btn => {
    btn.addEventListener('click', () => {
      const tool = btn.getAttribute('data-tool');
      editorSheet.focus();
      if (tool === 'bold') {
        document.execCommand('bold', false, null);
      } else if (tool === 'italic') {
        document.execCommand('italic', false, null);
      } else if (tool === 'h1') {
        document.execCommand('formatBlock', false, '<h1>');
      } else if (tool === 'h2') {
        document.execCommand('formatBlock', false, '<h2>');
      } else if (tool === 'bullet') {
        document.execCommand('insertUnorderedList', false, null);
      }
      editorSheet.dispatchEvent(new Event('input'));
    });
  });

  // --- Table Insertion Action ---
  if (btnInsertTable) {
    btnInsertTable.addEventListener('click', () => {
      editorSheet.focus();
      const rows = parseInt(prompt('¿Cuántas filas de datos tendrá la tabla?', '3')) || 3;
      const cols = parseInt(prompt('¿Cuántas columnas tendrá la tabla?', '3')) || 3;
      
      let tblHtml = '<table class="doc-table"><thead><tr>';
      for (let c = 1; c <= cols; c++) {
        tblHtml += `<th>Encabezado ${c}</th>`;
      }
      tblHtml += '</tr></thead><tbody>';
      for (let r = 1; r <= rows; r++) {
        tblHtml += '<tr>';
        for (let c = 1; c <= cols; c++) {
          tblHtml += `<td>Dato ${r}.${c}</td>`;
        }
        tblHtml += '</tr>';
      }
      tblHtml += '</tbody></table><p><br></p>';

      document.execCommand('insertHTML', false, tblHtml);
      editorSheet.dispatchEvent(new Event('input'));
    });
  }

  // --- Add Table Row Action ---
  if (btnAddTableRow) {
    btnAddTableRow.addEventListener('click', () => {
      // Find table currently focused or active
      let targetTable = null;
      const sel = window.getSelection();
      if (sel && sel.anchorNode) {
        let el = sel.anchorNode.nodeType === 3 ? sel.anchorNode.parentElement : sel.anchorNode;
        targetTable = el ? el.closest('table') : null;
      }
      if (!targetTable) {
        const allTables = editorSheet.querySelectorAll('table');
        if (allTables.length) targetTable = allTables[allTables.length - 1];
      }

      if (!targetTable) {
        alert('Coloca el cursor dentro de una tabla o inserta una primero con el botón 📊 Tabla.');
        return;
      }

      const tbody = targetTable.querySelector('tbody') || targetTable;
      const colCount = targetTable.querySelectorAll('tr')[0] ? targetTable.querySelectorAll('tr')[0].children.length : 3;
      const tr = document.createElement('tr');
      for (let i = 0; i < colCount; i++) {
        const td = document.createElement('td');
        td.textContent = 'Nueva celda';
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
      editorSheet.dispatchEvent(new Event('input'));
    });
  }

  // --- Add Table Column Action ---
  if (btnAddTableCol) {
    btnAddTableCol.addEventListener('click', () => {
      let targetTable = null;
      const sel = window.getSelection();
      if (sel && sel.anchorNode) {
        let el = sel.anchorNode.nodeType === 3 ? sel.anchorNode.parentElement : sel.anchorNode;
        targetTable = el ? el.closest('table') : null;
      }
      if (!targetTable) {
        const allTables = editorSheet.querySelectorAll('table');
        if (allTables.length) targetTable = allTables[allTables.length - 1];
      }

      if (!targetTable) {
        alert('Coloca el cursor dentro de una tabla para agregarle columnas.');
        return;
      }

      // Add th to thead
      const theadTr = targetTable.querySelector('thead tr');
      if (theadTr) {
        const th = document.createElement('th');
        th.textContent = `Col ${theadTr.children.length + 1}`;
        theadTr.appendChild(th);
      }

      // Add td to each tbody tr
      const tbodyTrs = targetTable.querySelectorAll('tbody tr');
      tbodyTrs.forEach(tr => {
        const td = document.createElement('td');
        td.textContent = 'Dato';
        tr.appendChild(td);
      });
      editorSheet.dispatchEvent(new Event('input'));
    });
  }

  // --- Image Insertion & Upload Action ---
  if (btnInsertImage && editorImageFileInput) {
    btnInsertImage.addEventListener('click', () => {
      editorImageFileInput.click();
    });

    editorImageFileInput.addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      btnInsertImage.disabled = true;
      btnInsertImage.textContent = '⏳ Subiendo...';
      try {
        if (typeof onUploadImage === 'function') {
          const res = await onUploadImage(doc.id, file);
          const imgHtml = `<div class="doc-img-wrapper"><img src="${res.url}" class="doc-img" alt="${escapeHtml(res.filename)}" /></div><p><br></p>`;
          editorSheet.focus();
          document.execCommand('insertHTML', false, imgHtml);
          editorSheet.dispatchEvent(new Event('input'));
        }
      } catch (err) {
        alert(`Error subiendo imagen: ${err.message}`);
      } finally {
        btnInsertImage.disabled = false;
        btnInsertImage.textContent = '🖼️ Imagen';
        editorImageFileInput.value = '';
      }
    });
  }

  // --- Undo Action ---
  if (btnUndoEditor) {
    btnUndoEditor.addEventListener('click', () => {
      if (undoStack.length > 1) {
        undoStack.pop(); // discard current
        const prev = undoStack[undoStack.length - 1];
        editorSheet.innerHTML = prev;
        editorSheet.dispatchEvent(new Event('input'));
      }
    });
  }

  // --- Find in Editor ---
  if (editorFindInput) {
    editorFindInput.addEventListener('input', () => {
      const query = editorFindInput.value.trim();
      if (!query) return;
      if (window.find) {
        window.find(query, false, false, true, false, false, false);
      }
    });
  }

  // --- Save Changes to Backend ---
  if (btnSaveEditor) {
    btnSaveEditor.addEventListener('click', async () => {
      const rawText = editorSheet.innerText || '';
      const contentHtml = editorSheet.innerHTML || '';
      btnSaveEditor.disabled = true;
      btnSaveEditor.textContent = '⏳ Guardando...';
      try {
        if (typeof onSaveText === 'function') {
          const updated = await onSaveText(doc.id, rawText, contentHtml);
          hasUnsavedChanges = false;
          unsavedIndicator.style.display = 'none';
          editorSaveStatus.textContent = '✓ Guardado y re-indexado con éxito';
          editorSaveStatus.style.color = 'var(--success)';
          btnSaveEditor.textContent = '✓ Guardado';
          
          if (updated && updated.metadata) {
            const summaryBox = modal.querySelector('#analysis-summary-box');
            if (summaryBox && updated.metadata.executive_summary) {
              summaryBox.innerHTML = renderMarkdown(updated.metadata.executive_summary);
            }
            const wordBadge = modal.querySelector('#analysis-word-count-badge');
            if (wordBadge) {
              wordBadge.textContent = `${updated.metadata.word_count || 0} palabras analizadas`;
            }
          }
          
          setTimeout(() => {
            btnSaveEditor.disabled = false;
            btnSaveEditor.textContent = '💾 Guardar';
          }, 1800);
        }
      } catch (err) {
        editorSaveStatus.textContent = `Error: ${err.message}`;
        editorSaveStatus.style.color = 'var(--error)';
        btnSaveEditor.disabled = false;
        btnSaveEditor.textContent = '💾 Guardar';
      }
    });
  }

  // --- Copilot Assistance ---
  async function sendCopilotPrompt(promptText) {
    if (!promptText.trim()) return;

    // Selected text from editor sheet
    const sel = window.getSelection();
    const selectedText = sel ? sel.toString().trim() : null;

    // Append User message
    const userBubble = document.createElement('div');
    userBubble.className = 'copilot-bubble user';
    userBubble.textContent = promptText;
    copilotMessages.appendChild(userBubble);
    copilotMessages.scrollTop = copilotMessages.scrollHeight;

    // Append Bot Loading message
    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'copilot-bubble bot';
    loadingBubble.innerHTML = `<span>Analizando documento y generando con Gemini Copilot... 🔍</span>`;
    copilotMessages.appendChild(loadingBubble);
    copilotMessages.scrollTop = copilotMessages.scrollHeight;

    try {
      if (typeof onAiEdit === 'function') {
        const res = await onAiEdit(doc.id, promptText, editorSheet.innerText, selectedText);
        loadingBubble.remove();

        const botBubble = document.createElement('div');
        botBubble.className = 'copilot-bubble bot';

        let proposalHtml = '';
        if (res.suggested_text) {
          const isTableOrHtml = res.suggested_text.includes('<table') || res.suggested_text.includes('<h');
          const previewContent = isTableOrHtml 
            ? `<div style="overflow-x: auto; max-height: 200px; padding: 0.5rem; background: var(--bg-primary); border-radius: 4px; border: 1px solid var(--border-color);">${res.suggested_text}</div>`
            : `<div class="copilot-proposal-text">${escapeHtml(res.suggested_text)}</div>`;

          proposalHtml = `
            <div class="copilot-proposal-box">
              <div style="font-size: 0.74rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.3rem;">
                <span>✨</span> Propuesta de Modificación / Tabla para el Documento:
              </div>
              ${previewContent}
              <div class="copilot-proposal-actions">
                <button type="button" class="btn-secondary btn-copy-proposal" style="padding: 0.3rem 0.6rem; font-size: 0.72rem;">📋 Copiar</button>
                <button type="button" class="btn-primary btn-apply-proposal" style="padding: 0.3rem 0.75rem; font-size: 0.74rem;">⚡ Aplicar al Documento</button>
              </div>
            </div>
          `;
        }

        botBubble.innerHTML = `
          <div>${renderMarkdown(res.reply || 'He procesado tu solicitud.')}</div>
          ${proposalHtml}
          <div style="font-size: 0.68rem; color: var(--text-muted); margin-top: 0.4rem; text-align: right;">
            ${res.model_used || 'Google Gemini Copilot'}
          </div>
        `;

        // Apply Proposal Button Handler
        const btnApply = botBubble.querySelector('.btn-apply-proposal');
        if (btnApply && res.suggested_text) {
          btnApply.addEventListener('click', () => {
            if (undoStack.length > 30) undoStack.shift();
            undoStack.push(editorSheet.innerHTML);

            editorSheet.focus();
            let insertSnippet = res.suggested_text;
            if (!insertSnippet.includes('<table') && !insertSnippet.includes('<p>') && !insertSnippet.includes('<h')) {
              insertSnippet = convertMarkdownOrTextToHtml(insertSnippet);
            }

            // If text is selected, replace selection; else append to bottom
            const sel = window.getSelection();
            if (sel && sel.rangeCount > 0 && sel.toString().trim()) {
              document.execCommand('insertHTML', false, insertSnippet);
            } else {
              editorSheet.innerHTML += `<div><br></div>${insertSnippet}<div><br></div>`;
            }

            editorSheet.dispatchEvent(new Event('input'));
            btnApply.textContent = '✓ Aplicado';
            btnApply.disabled = true;
            btnApply.style.background = 'var(--success)';
            
            // Switch to editor tab if not visible
            tabBtnEditor.click();
          });
        }

        // Copy Proposal Button Handler
        const btnCopy = botBubble.querySelector('.btn-copy-proposal');
        if (btnCopy && res.suggested_text) {
          btnCopy.addEventListener('click', () => {
            navigator.clipboard.writeText(res.suggested_text);
            btnCopy.textContent = '✓ Copiado';
            setTimeout(() => { btnCopy.textContent = '📋 Copiar'; }, 1500);
          });
        }

        copilotMessages.appendChild(botBubble);
        copilotMessages.scrollTop = copilotMessages.scrollHeight;
      }
    } catch (err) {
      loadingBubble.innerHTML = `<span style="color: var(--error);">Error en Copilot: ${escapeHtml(err.message)}</span>`;
    }
  }

  // --- Copilot Form Submit ---
  if (copilotForm) {
    copilotForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const prompt = copilotInput.value.trim();
      if (!prompt) return;
      copilotInput.value = '';
      sendCopilotPrompt(prompt);
    });
  }

  // --- Copilot Quick Pills ---
  copilotPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const prompt = pill.getAttribute('data-prompt');
      if (prompt) {
        sendCopilotPrompt(prompt);
      }
    });
  });

  // --- In-Document Keyword Search in Analysis Tab ---
  const searchInput = modal.querySelector('#doc-keyword-search');
  const searchCount = modal.querySelector('#doc-search-count');
  const btnPrev = modal.querySelector('#doc-search-prev');
  const btnNext = modal.querySelector('#doc-search-next');
  const btnClear = modal.querySelector('#doc-search-clear');
  const textContainer = modal.querySelector('#doc-text-container');

  let currentMatchIndex = -1;
  let matchesCount = 0;

  function applyInDocSearch() {
    const term = (searchInput.value || '').trim();
    const rawText = textarea.value || '';
    if (!term) {
      textContainer.textContent = rawText || 'Sin texto extraído.';
      searchCount.textContent = '';
      currentMatchIndex = -1;
      matchesCount = 0;
      return;
    }

    const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedTerm})`, 'gi');
    const parts = rawText.split(regex);
    
    matchesCount = 0;
    let newHtml = '';

    parts.forEach(part => {
      if (part.toLowerCase() === term.toLowerCase()) {
        newHtml += `<mark class="doc-match" data-idx="${matchesCount}">${escapeHtml(part)}</mark>`;
        matchesCount++;
      } else {
        newHtml += escapeHtml(part);
      }
    });

    textContainer.innerHTML = newHtml || 'Sin coincidencias.';

    if (matchesCount > 0) {
      currentMatchIndex = 0;
      updateActiveMatch(true);
    } else {
      currentMatchIndex = -1;
      searchCount.textContent = '0 coincidencias';
    }
  }

  function updateActiveMatch(shouldScroll = true) {
    const marks = textContainer.querySelectorAll('mark.doc-match');
    marks.forEach((m, idx) => {
      if (idx === currentMatchIndex) {
        m.classList.add('current');
        if (shouldScroll) {
          m.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } else {
        m.classList.remove('current');
      }
    });
    searchCount.textContent = `${currentMatchIndex + 1} de ${matchesCount} coincidencias`;
  }

  if (searchInput) {
    searchInput.addEventListener('input', applyInDocSearch);
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (matchesCount > 0) {
          currentMatchIndex = (currentMatchIndex + 1) % matchesCount;
          updateActiveMatch(true);
        }
      }
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', () => {
      if (matchesCount > 0) {
        currentMatchIndex = (currentMatchIndex + 1) % matchesCount;
        updateActiveMatch(true);
      }
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      if (matchesCount > 0) {
        currentMatchIndex = (currentMatchIndex - 1 + matchesCount) % matchesCount;
        updateActiveMatch(true);
      }
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', () => {
      searchInput.value = '';
      applyInDocSearch();
      searchInput.focus();
    });
  }

  // Close Modal
  modal.querySelectorAll('.btn-close').forEach(btn => {
    btn.addEventListener('click', () => {
      if (hasUnsavedChanges) {
        const confirmClose = confirm('Tiene cambios sin guardar en el documento. ¿Desea cerrar de todos modos?');
        if (!confirmClose) return;
      }
      modal.remove();
    });
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
