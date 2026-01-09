
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\panel_estados.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. REPLACE HTML BLOCK ("VISTA OPERATIVA")
# Find {% else %} and {% endif %} around lines 255-277.
# We look for "<!-- VISTA OPERATIVA (TABLA UNIFICADA) -->"
start_marker = "<!-- VISTA OPERATIVA (TABLA UNIFICADA) -->"
start_idx = -1
for i, line in enumerate(lines):
    if start_marker in line:
        start_idx = i
        break

if start_idx == -1:
    print("HTML start marker not found")
    exit(1)

# Find the {% endif %}
end_idx = -1
for i in range(start_idx, len(lines)):
    if "{% endif %}" in lines[i]:
        end_idx = i
        break

# New HTML Content
new_html = """    <!-- VISTA OPERATIVA (AGRUPADA) -->
    <div id="operationalView">
        <!-- LOGIC HANDLED BY JS: We create containers for all possibilities, and JS hides/shows based on Role -->
        
        <!-- ROW 1: PENDIENTES (Rec/Ops) -->
        <div class="card bg-dark-card border-secondary shadow-sm mb-4" id="cardPendientesOp">
            <div class="card-header border-secondary text-warning">
                <i class="fas fa-clock me-2"></i> Pendientes de Aprobación
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead class="text-secondary text-uppercase text-xs font-weight-bolder">
                            <tr>
                                <th class="ps-4">Equipo / FR</th>
                                <th>Estado</th>
                                <th>Encargado</th>
                                <th>Fecha</th>
                                <th>Días</th>
                                <th class="text-end pe-4">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="tablePendientesOp"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ROW 2: DIAGNOSTICO (Rec/Ops) -->
        <div class="card bg-dark-card border-secondary shadow-sm mb-4" id="cardDiagnosticoOp">
            <div class="card-header border-secondary text-info">
                <i class="fas fa-microscope me-2"></i> En Diagnóstico
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead class="text-secondary text-uppercase text-xs font-weight-bolder">
                            <tr>
                                <th class="ps-4">Equipo / FR</th>
                                <th>Estado</th>
                                <th>Encargado</th>
                                <th>Fecha</th>
                                <th>Días</th>
                                <th class="text-end pe-4">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="tableDiagnosticoOp"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ROW 3: APROBADOS (Rec/Ops) -->
        <div class="card bg-dark-card border-secondary shadow-sm mb-4" id="cardAprobadosOp">
            <div class="card-header border-secondary text-success">
                <i class="fas fa-check-circle me-2"></i> Aprobados / Servicio
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead class="text-secondary text-uppercase text-xs font-weight-bolder">
                            <tr>
                                <th class="ps-4">Equipo / FR</th>
                                <th>Estado</th>
                                <th>Encargado</th>
                                <th>Fecha</th>
                                <th>Días</th>
                                <th class="text-end pe-4">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="tableAprobadosOp"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ALMACEN CONTAINERS -->
        <!-- ROW 1: REPUESTOS DIAG -->
        <div class="card bg-dark-card border-secondary shadow-sm mb-4 d-none" id="cardRepDiag">
            <div class="card-header border-secondary text-warning">
                <i class="fas fa-boxes me-2"></i> Repuestos para Diagnóstico
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead class="text-secondary text-uppercase text-xs font-weight-bolder">
                            <tr>
                                <th class="ps-4">Equipo / FR</th>
                                <th>Estado</th>
                                <th>Encargado</th>
                                <th>Fecha</th>
                                <th>Días</th>
                                <th class="text-end pe-4">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="tableRepDiag"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ROW 2: REPUESTOS SERV -->
        <div class="card bg-dark-card border-secondary shadow-sm mb-4 d-none" id="cardRepServ">
            <div class="card-header border-secondary text-info">
                <i class="fas fa-cogs me-2"></i> Repuestos para Servicio
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead class="text-secondary text-uppercase text-xs font-weight-bolder">
                            <tr>
                                <th class="ps-4">Equipo / FR</th>
                                <th>Estado</th>
                                <th>Encargado</th>
                                <th>Fecha</th>
                                <th>Días</th>
                                <th class="text-end pe-4">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="tableRepServ"></tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>
"""

# Replace HTML
lines = lines[:start_idx] + [new_html + "\n"] + lines[end_idx:]


# 2. REPLACE JS LOGIC ("UNIFIED VIEW LOGIC")
# Find "// UNIFIED VIEW LOGIC" and the block after.
js_start_marker = "// UNIFIED VIEW LOGIC"
js_start_idx = -1
for i, line in enumerate(lines):
    if js_start_marker in line:
        js_start_idx = i
        break

if js_start_idx == -1:
    print("JS marker not found")
    exit(1)

# Find "Global Action wrappers" which starts the next section
js_end_marker = "// Global Action wrappers"
js_end_idx = -1
for i, line in enumerate(lines):
    if js_end_marker in line and i > js_start_idx:
        js_end_idx = i
        break

# New JS Logic
new_js = """            // UNIFIED VIEW LOGIC (GROUPED)
            const isAlmacenRole = userRole === 'almacen';
            
            // Toggle visibility of containers based on role
            if (isAlmacenRole) {
                document.getElementById('cardPendientesOp').classList.add('d-none');
                document.getElementById('cardDiagnosticoOp').classList.add('d-none');
                document.getElementById('cardAprobadosOp').classList.add('d-none');
                document.getElementById('cardRepDiag').classList.remove('d-none');
                document.getElementById('cardRepServ').classList.remove('d-none');
            } else {
                document.getElementById('cardPendientesOp').classList.remove('d-none');
                document.getElementById('cardDiagnosticoOp').classList.remove('d-none');
                document.getElementById('cardAprobadosOp').classList.remove('d-none');
                // Almacen cards defined as d-none by default in HTML? No, I added d-none class in HTML just in case.
            }

            function renderGrouped(data) {
                // Containers
                const tPend = document.getElementById('tablePendientesOp');
                const tDiag = document.getElementById('tableDiagnosticoOp');
                const tApro = document.getElementById('tableAprobadosOp');
                const tRepD = document.getElementById('tableRepDiag');
                const tRepS = document.getElementById('tableRepServ');

                if (isAlmacenRole) {
                    // Filter Almacen
                    // 1. Repuestos Diag
                    const d1 = data.filter(i => {
                        const s = (i.estado || '').toLowerCase();
                        return s.includes('diagnostico') || s.includes('consumible');
                    });
                     // 2. Repuestos Serv
                    const d2 = data.filter(i => {
                        const s = (i.estado || '').toLowerCase();
                        return s.includes('servicio') && s.includes('repuesto');
                    });

                    tRepD.innerHTML = d1.length ? d1.map(i => createRow(i, false)).join('') : '<tr><td colspan="6" class="text-center text-muted">Sin pendientes</td></tr>';
                    tRepS.innerHTML = d2.length ? d2.map(i => createRow(i, false)).join('') : '<tr><td colspan="6" class="text-center text-muted">Sin pendientes</td></tr>';

                } else {
                    // Filter Rec/Ops
                    // 1. Pendientes
                    const d1 = data.filter(i => {
                        const s = (i.estado || '').toLowerCase();
                        return (s.includes('pendiente') && s.includes('aprobacion'));
                    });
                    // 2. Diagnostico
                    const d2 = data.filter(i => {
                        const s = (i.estado || '').toLowerCase();
                        return s.includes('diagnostico') || s.includes('consumible') || s.includes('repuesto entregado');
                    });
                    // 3. Aprobado / Servicio
                    const d3 = data.filter(i => {
                        const s = (i.estado || '').toLowerCase();
                        return (s.includes('aprobado') || s.includes('servicio') || s.includes('entregado'));
                    });

                    tPend.innerHTML = d1.length ? d1.map(i => createRow(i, false)).join('') : '<tr><td colspan="6" class="text-center text-muted">Sin equipos</td></tr>';
                    tDiag.innerHTML = d2.length ? d2.map(i => createRow(i, false)).join('') : '<tr><td colspan="6" class="text-center text-muted">Sin equipos</td></tr>';
                    tApro.innerHTML = d3.length ? d3.map(i => createRow(i, false)).join('') : '<tr><td colspan="6" class="text-center text-muted">Sin equipos</td></tr>';
                }
            }

            renderGrouped(equipments);

            // Search (Generic filtering across all visible tables)
             const searchInput = document.getElementById('searchInput');
             if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    const term = normalize(e.target.value);
                    const filtered = equipments.filter(item =>
                        normalize(item.fr).includes(term) ||
                        normalize(item.marca).includes(term) ||
                        normalize(item.modelo).includes(term)
                    );
                    renderGrouped(filtered);
                });
             }

"""

# Replace JS
lines = lines[:js_start_idx] + [new_js + "\n"] + lines[js_end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Panel Estados updated successfully.")
