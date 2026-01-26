/**
 * Excel-like Inline Editing Logic
 * Handles double-click to edit, blur to save
 * Includes Frontend Filtering
 */

let allExcelData = [];

document.addEventListener('DOMContentLoaded', function () {
    loadData();
    document.getElementById('refreshBtn').addEventListener('click', loadData);

    // Filter Event Listeners
    document.getElementById('filterText').addEventListener('keyup', applyFilters);
    document.getElementById('filterStatus').addEventListener('change', applyFilters);
    document.getElementById('clearFiltersBtn').addEventListener('click', clearFilters);
});

async function loadData() {
    try {
        const response = await fetch('/api/search?q=all');
        const result = await response.json();
        if (result.success) {
            allExcelData = result.data;
            applyFilters(); // Render with current filters (or empty)
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function applyFilters() {
    const textTerm = document.getElementById('filterText').value.toLowerCase().trim();
    const statusTerm = document.getElementById('filterStatus').value;

    const filtered = allExcelData.filter(item => {
        // Text Filter
        const matchesText = !textTerm ||
            (item.fr || '').toLowerCase().includes(textTerm) ||
            (item.marca || '').toLowerCase().includes(textTerm) ||
            (item.modelo || '').toLowerCase().includes(textTerm) ||
            (item.cliente || '').toLowerCase().includes(textTerm);

        // Status Filter
        const matchesStatus = !statusTerm || (item.estado || '').toLowerCase().trim() === statusTerm.toLowerCase().trim();

        return matchesText && matchesStatus;
    });

    renderExcelTable(filtered);
}

function clearFilters() {
    document.getElementById('filterText').value = '';
    document.getElementById('filterStatus').value = '';
    applyFilters();
}

function renderExcelTable(data) {
    const tbody = document.getElementById('excelTableBody');
    tbody.innerHTML = data.map(item => `
        <tr data-id="${item.id}">
            <td class="editable" data-field="fr">${item.fr || ''}</td>
            <td class="editable" data-field="marca">${item.marca || ''}</td>
            <td class="editable" data-field="modelo">${item.modelo || ''}</td>
            <td class="editable text-truncate" data-field="reporte_cliente" style="max-width: 250px;" title="${item.reporte_cliente || ''}">${item.reporte_cliente || ''}</td>
            <td class="text-info fst-italic bg-darker font-monospace" style="font-size: 0.8rem;">${(item.estado || '').toUpperCase()}</td>
            <td class="editable" data-field="condicion">${item.condicion || ''}</td>
            <td class="editable" data-field="encargado">${item.encargado || ''}</td>
            <td class="editable" data-field="fecha_ingreso">${item.fecha_ingreso || ''}</td>
            <td class="editable text-truncate" data-field="observaciones" style="max-width: 250px;" title="${item.observaciones || ''}">${item.observaciones || ''}</td>
            <td class="editable" data-field="cliente">${item.cliente || ''}</td>
            <td class="editable" data-field="serie">${item.serie || ''}</td>
            <td class="editable text-truncate" data-field="accesorios" style="max-width: 200px;" title="${item.accesorios || ''}">${item.accesorios || ''}</td>
            <!-- NEW COLUMNS -->
            <td class="editable" data-field="encargado_mantenimiento">${item.encargado_mantenimiento || ''}</td>
            <td class="editable" data-field="numero_informe">${item.numero_informe || ''}</td>
            <td class="editable" data-field="hora_inicio_diagnostico">${item.hora_inicio_diagnostico || ''}</td>
            <td class="editable text-truncate" data-field="observaciones_diagnostico" style="max-width: 200px;" title="${item.observaciones_diagnostico || ''}">${item.observaciones_diagnostico || ''}</td>
            <td class="editable" data-field="hora_inicio_mantenimiento">${item.hora_inicio_mantenimiento || ''}</td>
            <td class="editable text-truncate" data-field="observaciones_mantenimiento" style="max-width: 200px;" title="${item.observaciones_mantenimiento || ''}">${item.observaciones_mantenimiento || ''}</td>
        </tr>
    `).join('');

    setupEditableCells();
}

function setupEditableCells() {
    const cells = document.querySelectorAll('.editable');

    cells.forEach(cell => {
        cell.addEventListener('dblclick', function () {
            if (this.querySelector('input')) return; // Already editing

            const currentText = this.innerText;
            const field = this.dataset.field;

            // Create input
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentText;
            input.className = 'form-control form-control-sm bg-secondary text-white border-0 p-1';
            input.style.minWidth = '100px';

            // Replace text with input
            this.innerText = '';
            this.appendChild(input);
            input.focus();

            // Save on blur or enter
            input.addEventListener('blur', () => saveCell(this, input.value, currentText));
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') input.blur();
                if (e.key === 'Escape') {
                    this.innerText = currentText; // Cancel
                }
            });
        });
    });
}

async function saveCell(cell, newValue, originalValue) {
    if (newValue === originalValue) {
        cell.innerText = originalValue;
        return;
    }

    const row = cell.closest('tr');
    const id = row.dataset.id;
    const field = cell.dataset.field;

    // Construct payload
    const payload = {};
    payload[field] = newValue;

    // Show loading state (opacity)
    cell.style.opacity = '0.5';

    try {
        const response = await fetch(`/api/equipment/${id}/update_data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (result.success) {
            cell.innerText = newValue;
            cell.classList.add('bg-success', 'bg-opacity-25');
            setTimeout(() => cell.classList.remove('bg-success', 'bg-opacity-25'), 1000);
            showToast();

            // Update local data store to reflect change for filtering
            const item = allExcelData.find(i => i.id == id);
            if (item) item[field] = newValue;

        } else {
            cell.innerText = originalValue;
            alert('Error al guardar: ' + result.error);
        }
    } catch (error) {
        console.error('Save error:', error);
        cell.innerText = originalValue;
        alert('Error de conexión');
    } finally {
        cell.style.opacity = '1';
    }
}

function showToast() {
    const toastEl = document.getElementById('saveToast');
    const toast = new bootstrap.Toast(toastEl, { delay: 1500 });
    toast.show();
}
