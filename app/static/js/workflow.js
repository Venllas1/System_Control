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
                <td class="ps-4 text-info fw-bold">${frDisplay}</td>
                <td class="text-white">${item.marca} ${item.modelo}</td>
                <td>${getStatusBadge(item.estado)}</td>
                <td class="text-sm text-light"><i class="fas fa-user-circle me-1 text-muted"></i> ${item.encargado}</td>
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
async function showAdvanceModal(equipmentId) {
    try {
        // Get next state info
        const response = await fetch(`/api/equipment/${equipmentId}/next_state`);
        const result = await response.json();

        if (!result.success) {
            showError(result.error || 'Error al obtener información del estado');
            return;
        }

        const info = result.data;

        // Check if can advance
        if (!info.can_advance) {
            showError(`Tu rol (${currentUserRole}) no puede avanzar equipos desde '${info.current_state}'`);
            return;
        }

        // Check if terminal state
        if (info.is_terminal) {
            showError('El equipo ya está en estado terminal (Entregado)');
            return;
        }

        // If requires decision (multiple next states), show decision modal
        if (info.requires_decision && info.next_states.length > 1) {
            showDecisionModal(equipmentId, info.current_state, info.next_states);
        } else {
            // Single next state, confirm and advance
            const nextState = info.next_states[0];
            if (confirm(`¿Avanzar equipo de '${info.current_state}' a '${nextState}'?`)) {
                await advanceEquipment(equipmentId, nextState);
            }
        }
    } catch (error) {
        console.error('Error showing advance modal:', error);
        showError('Error al procesar la solicitud');
    }
}

/**
 * Show decision modal when multiple next states are available
 */
function showDecisionModal(equipmentId, currentState, nextStates) {
    // Create modal HTML
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
                                <button class="btn btn-outline-primary btn-lg" onclick="advanceEquipment(${equipmentId}, '${state}'); bootstrap.Modal.getInstance(document.getElementById('decisionModal')).hide();">
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

    // Remove existing modal if any
    const existingModal = document.getElementById('decisionModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('decisionModal'));
    modal.show();

    // Clean up on hide
    document.getElementById('decisionModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

/**
 * Advance equipment to next state
 */
async function advanceEquipment(equipmentId, nextState = null) {
    try {
        const response = await fetch(`/api/equipment/${equipmentId}/update_status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ next_state: nextState })
        });

        const result = await response.json();

        if (result.success) {
            showSuccess(result.message || 'Equipo avanzado correctamente');
            // Reload page to reflect changes
            setTimeout(() => location.reload(), 1000);
        } else {
            showError(result.error || 'Error al avanzar equipo');
        }
    } catch (error) {
        console.error('Error advancing equipment:', error);
        showError('Error al procesar la solicitud');
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

    if (s.includes('diagnostico') || s.includes('revision') || s.includes('standby')) {
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
