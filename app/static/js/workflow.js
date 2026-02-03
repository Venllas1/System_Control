/**
 * Workflow Management - Guided State Transitions
 * Handles pending tasks display and guided equipment advancement
 */

// Global state
let pendingTasks = [];
let currentUserRole = '';

/**
 * Initialize workflow functionality
 */
async function initWorkflow() {
    // Get user role from data element
    const dataEl = document.getElementById('equipmentsData');
    if (dataEl) {
        currentUserRole = JSON.parse(dataEl.dataset.userRole || '""').toLowerCase();
    }

    // Load pending tasks
    await loadPendingTasks();

    // Set up event listeners
    setupWorkflowEventListeners();
}

/**
 * Load pending tasks from API
 */
async function loadPendingTasks() {
    try {
        const response = await fetch('/api/pending_tasks');
        const data = await response.json();

        if (data.success) {
            pendingTasks = data.data || [];
            renderPendingTasks();
        } else {
            console.error('Error loading pending tasks:', data.error);
        }
    } catch (error) {
        console.error('Error fetching pending tasks:', error);
    }
}

/**
 * Render pending tasks table
 */
function renderPendingTasks() {
    const container = document.getElementById('pendingTasksContainer');
    const tableBody = document.getElementById('pendingTasksTable');
    const countBadge = document.getElementById('pendingTasksCount');

    if (!container || !tableBody) return;

    // Update count badge
    if (countBadge) {
        countBadge.textContent = `${pendingTasks.length} tarea${pendingTasks.length !== 1 ? 's' : ''}`;
        countBadge.className = `badge ${pendingTasks.length > 0 ? 'bg-warning text-dark' : 'bg-secondary'}`;
    }

    // Show/hide container based on tasks
    if (pendingTasks.length === 0) {
        container.classList.add('d-none');
        return;
    }

    container.classList.remove('d-none');

    // Render table rows
    tableBody.innerHTML = pendingTasks.map(item => {
        const today = new Date();
        const ingreso = new Date(item.fecha_ingreso);
        const diffDays = Math.ceil(Math.abs(today - ingreso) / (1000 * 60 * 60 * 24));
        const frDisplay = item.fr || 'Sin FR';

        return `
            <tr class="${diffDays > 5 ? 'table-warning' : ''}">
                <td class="ps-4">
                    <div class="d-flex flex-column">
                        <span class="fw-bold text-white text-uppercase">${item.marca} ${item.modelo}</span>
                        <span class="text-xs text-info">${frDisplay}</span>
                    </div>
                </td>
                <td>${getStatusBadge(item.estado)}</td>
                <td class="text-sm text-light"><i class="fas fa-user-circle me-1 text-muted"></i> ${item.encargado_diagnostico || 'N/A'}</td>
                <td class="text-sm text-muted">${item.fecha_ingreso || 'N/A'}</td>
                <td><span class="badge ${diffDays > 5 ? 'bg-danger' : 'bg-success'} badge-pill">${diffDays} días</span></td>
                <td class="text-end pe-4">
                    <button class="btn btn-sm btn-primary" onclick="showAdvanceModal(${item.id})">
                        <i class="fas fa-arrow-right me-1"></i> Avanzar
                    </button>
                    <button class="btn btn-sm btn-outline-info ms-1" onclick="showInfo(${item.id})" title="Ver Detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Show modal to advance equipment to next state
 */
async function showAdvanceModal(equipmentId, targetState = null) {
    try {
        const response = await fetch(`/api/equipment/${equipmentId}/next_state`);
        const result = await response.json();

        if (!result.success) {
            showError(result.error || 'Error al obtener información del estado');
            return;
        }

        const info = result.data;

        if (!info.can_advance) {
            showError(`Tu rol (${currentUserRole}) no puede avanzar equipos desde '${info.current_state}'`);
            return;
        }

        if (info.is_terminal) {
            showError('El equipo ya está en estado terminal (Entregado)');
            return;
        }

        // If target state is forced, skip decision logic
        let nextState = targetState;

        if (!nextState) {
            // If requires decision and no target forced, show decision modal
            if (info.requires_decision && info.next_states.length > 1) {
                showDecisionModal(equipmentId, info.current_state, info.next_states);
                return;
            }
            nextState = info.next_states[0];
        }

        // Check prompts for the chosen state (reload info if needed or use existing logic)
        // Since we got next_states from info, we might need to check prompts for this SPECIFIC state
        // The API /equipment/:id/next_state?target=STATE gives us the specific prompts
        if (nextState) {
            const specificRes = await fetch(`/api/equipment/${equipmentId}/next_state?target=${encodeURIComponent(nextState)}`);
            const specificInfo = await specificRes.json();

            if (specificInfo.success && specificInfo.data.prompt_fields && specificInfo.data.prompt_fields.length > 0) {
                showDataPromptModal(equipmentId, nextState, specificInfo.data.prompt_fields);
            } else {
                if (confirm(`¿Avanzar equipo de '${info.current_state}' a '${nextState}'?`)) {
                    await advanceEquipment(equipmentId, nextState);
                }
            }
        }
    } catch (error) {
        console.error('Error showing advance modal:', error);
        showError('Error al procesar la solicitud');
    }
}

/**
 * Show modal to collect additional data before advancing
 */
function showDataPromptModal(equipmentId, nextState, fields) {
    const fieldDefinitions = {
        'encargado_diagnostico': {
            label: 'Encargado de Diagnóstico',
            type: 'text',
            required: true,
            placeholder: 'Nombre del técnico'
        },
        'numero_informe': {
            label: 'Número de Informe',
            type: 'text',
            required: true,
            placeholder: 'Ej: INF-2024-001'
        },
        'encargado_mantenimiento': {
            label: 'Encargado de Mantenimiento',
            type: 'text',
            required: true,
            placeholder: 'Nombre del técnico'
        },
        'observaciones_diagnostico': {
            label: 'Observaciones de Diagnóstico',
            type: 'textarea',
            required: true,
            placeholder: 'Detalles del diagnóstico...'
        },
        'observaciones_mantenimiento': {
            label: 'Observaciones de Mantenimiento',
            type: 'textarea',
            required: true,
            placeholder: 'Detalles del servicio...'
        }
    };

    const modalHtml = `
        <div class="modal fade" id="promptModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark-card border-secondary text-light">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title">
                            <i class="fas fa-edit text-info me-2"></i>
                            Información Requerida
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="promptForm">
                        <div class="modal-body">
                            <p class="text-white mb-3">Para avanzar a <strong class="text-success">${nextState}</strong>, completa los siguientes datos:</p>
                            ${fields.map(fieldName => {
        const def = fieldDefinitions[fieldName] || { label: fieldName, type: 'text' };
        if (def.type === 'select') {
            return `
                                        <div class="mb-3">
                                            <label class="form-label text-secondary">${def.label}</label>
                                            <select name="${fieldName}" class="form-select bg-dark text-light border-secondary" required>
                                                <option value="">Seleccione encargado...</option>
                                                ${def.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                                            </select>
                                        </div>
                                    `;
        }
        if (def.type === 'textarea') {
            return `
                <div class="mb-3">
                    <label class="form-label text-secondary">${def.label}</label>
                    <textarea name="${fieldName}" class="form-control bg-dark text-light border-secondary" 
                           placeholder="${def.placeholder || ''}" rows="3" ${def.required ? 'required' : ''}></textarea>
                </div>
            `;
        }
        return `
                                    <div class="mb-3">
                                        <label class="form-label text-secondary">${def.label}</label>
                                        <input type="${def.type}" name="${fieldName}" class="form-control bg-dark text-light border-secondary" 
                                               placeholder="${def.placeholder || ''}" ${def.required ? 'required' : ''}>
                                    </div>
                                `;
    }).join('')}
                        </div>
                        <div class="modal-footer border-secondary">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary">Continuar y Avanzar</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;

    // Remove existing
    const existing = document.getElementById('promptModal');
    if (existing) existing.remove();

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('promptModal'));
    modal.show();

    // Form submission
    document.getElementById('promptForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        modal.hide();
        await advanceEquipment(equipmentId, nextState, data);
    });
}

/**
 * Show decision modal when multiple next states are available
 */
function showDecisionModal(equipmentId, currentState, nextStates) {
    // Note: If multiple states exist, we only show buttons. 
    // If a button is clicked and THAT state needs prompts, showAdvanceModal will handle it
    // if recursively called or we can just call it again.
    const modalHtml = `
        <div class="modal fade" id="decisionModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark-card border-secondary text-light">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title">
                            <i class="fas fa-code-branch text-warning me-2"></i>
                            Selecciona el Siguiente Estado
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-muted">Estado actual: <strong class="text-info">${currentState}</strong></p>
                        <p class="mb-3">Selecciona el siguiente estado para este equipo:</p>
                        <div class="d-grid gap-2">
                            ${nextStates.map(state => `
                                <button class="btn btn-outline-primary btn-lg" onclick="handleDecisionClick(${equipmentId}, '${state}')">
                                    <i class="fas fa-arrow-right me-2"></i> ${state}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    const existing = document.getElementById('decisionModal');
    if (existing) existing.remove();

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('decisionModal'));
    modal.show();

    window.handleDecisionClick = async (id, state) => {
        modal.hide();
        // Re-check for prompts for the specific selected target state
        const response = await fetch(`/api/equipment/${id}/next_state?target=${encodeURIComponent(state)}`);
        const result = await response.json();

        if (result.success && result.data.prompt_fields && result.data.prompt_fields.length > 0) {
            showDataPromptModal(id, state, result.data.prompt_fields);
        } else {
            if (confirm(`¿Avanzar equipo a '${state}'?`)) {
                await advanceEquipment(id, state);
            }
        }
    };
}

/**
 * Advance equipment to next state
 */
async function advanceEquipment(equipmentId, nextState = null, additionalData = {}) {
    // Idempotency: Block interaction during fetch
    const submitBtn = document.querySelector('#promptForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
    }

    try {
        const payload = { next_state: nextState, ...additionalData };
        const response = await fetch(`/api/equipment/${equipmentId}/update_status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            showSuccess(result.message || 'Equipo avanzado correctamente');
            setTimeout(() => location.reload(), 1000);
        } else {
            showError(result.error || 'Error al avanzar equipo');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Continuar y Avanzar';
            }
        }
    } catch (error) {
        console.error('Error advancing equipment:', error);
        showError('Error al procesar la solicitud');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Continuar y Avanzar';
        }
    }
}

/**
 * Setup event listeners for workflow
 */
function setupWorkflowEventListeners() {
    // Refresh button for pending tasks
    const refreshBtn = document.getElementById('refreshPendingTasks');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadPendingTasks);
    }
}

/**
 * Show success message
 */
function showSuccess(message) {
    // Use existing notification system or create simple alert
    if (typeof showNotification === 'function') {
        showNotification(message, 'success');
    } else {
        alert(message);
    }
}

/**
 * Show error message
 */
function showError(message) {
    // Use existing notification system or create simple alert
    if (typeof showNotification === 'function') {
        showNotification(message, 'error');
    } else {
        alert('Error: ' + message);
    }
}

/**
 * Get status badge HTML (reuse existing function if available)
 */
function getStatusBadge(status) {
    let badgeClass = 'bg-secondary';
    let icon = 'fa-circle';
    let s = status.toLowerCase();

    // prioritized specific match for colors
    if (s === 'espera de diagnostico') { badgeClass = 'bg-warning text-dark'; icon = 'fa-clock'; }
    else if (s === 'en diagnostico') { badgeClass = 'bg-info text-dark'; icon = 'fa-stethoscope'; }
    else if (s.includes('diagnostico') || s.includes('revision') || s.includes('standby')) {
        badgeClass = 'bg-info text-dark';
        icon = 'fa-stethoscope';
    } else if (s.includes('aprobado')) {
        badgeClass = 'bg-success';
        icon = 'fa-check-circle';
    } else if (s.includes('espera') || s.includes('pendiente')) {
        badgeClass = 'bg-warning text-dark';
        icon = 'fa-clock';
    } else if (s.includes('servicio') || s.includes('reparacion')) {
        badgeClass = 'bg-primary';
        icon = 'fa-tools';
    } else if (s.includes('culminado') || s.includes('entregado')) {
        badgeClass = 'bg-success';
        icon = 'fa-flag-checkered';
    }

    return `<span class="badge ${badgeClass} text-uppercase"><i class="fas ${icon} me-1"></i> ${status}</span>`;
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWorkflow);
} else {
    initWorkflow();
}
