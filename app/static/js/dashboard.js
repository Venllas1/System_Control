/**
 * CABELAB 2025 - Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Force UpperCase on Inputs
    const form = document.getElementById('createEquipmentForm');
    if (form) {
        form.querySelectorAll('input[type="text"], textarea').forEach(input => {
            input.addEventListener('input', function () {
                this.value = this.value.toUpperCase();
            });
        });

        // Auto-fill Current Date/Time on show
        const createModal = document.getElementById('createEquipmentModal');
        createModal.addEventListener('show.bs.modal', function () {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');

            const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
            const fechaInput = document.getElementById('create_fecha_ingreso');
            if (fechaInput && !fechaInput.value) {
                fechaInput.value = formattedDate;
            }
        });

        // 2. Submit New Equipment
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(form);
            fetch('/api/equipment/create', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Error: ' + data.error);
                })
                .catch(err => alert('Error de red: ' + err));
        });
    }

    // 3. Update Status Logic
    const updateForm = document.getElementById('updateStatusForm');
    if (updateForm) {
        updateForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const id = document.getElementById('update_id').value;
            const formData = new FormData(updateForm);
            fetch(`/api/equipment/${id}/update_status`, { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => {
                    if (data.success) location.reload();
                    else alert('Error: ' + data.error);
                })
                .catch(err => alert('Error de red: ' + err));
        });
    }
});

// GLOBAL FUNCTIONS
window.showInfo = function (btn) {
    const d = btn.dataset;
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val || 'N/A';
    };

    set('infoFr', d.fr);
    set('infoMarca', d.marca);
    set('infoCliente', d.cliente);
    set('infoEncargado', d.encargado);
    set('infoFecha', d.fecha);
    set('infoReporte', d.reporte);
    set('infoObservaciones', d.observaciones);

    const infoEstado = document.getElementById('infoEstado');
    if (infoEstado) {
        infoEstado.innerHTML = `<span class="badge bg-secondary">${d.state || d.estado}</span>`;
    }

    const modal = new bootstrap.Modal(document.getElementById('detailedInfoModal'));
    modal.show();
};

window.showEditStatusModal = function (id, currentStatus) {
    document.getElementById('update_id').value = id;
    const select = document.getElementById('update_status_select');
    if (select) {
        // Try to match the current status in select
        for (let opt of select.options) {
            if (opt.value.includes(currentStatus)) {
                opt.selected = true;
                break;
            }
        }
    }
    const modal = new bootstrap.Modal(document.getElementById('updateStatusModal'));
    modal.show();
};
