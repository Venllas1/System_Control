
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

def get_entregados_block():
    return """
    <!-- HISTORIAL ENTREGADOS (SHARED) -->
    {% if current_user.role|lower != 'almacen' %}
    <div class="row g-4 mt-4">
        <div class="col-12">
            <div class="card bg-dark border-secondary shadow-sm">
                <div class="card-header border-secondary d-flex justify-content-between align-items-center">
                    <div class="text-light">
                        <i class="fas fa-history me-2"></i> Historial de Equipos Entregados
                    </div>
                    <div class="d-flex gap-2">
                        <input type="text" id="searchEntregados" class="form-control form-control-sm bg-dark text-light border-secondary" placeholder="Buscar..." style="width: 200px;">
                    </div>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-dark table-hover mb-0 align-middle" id="tableEntregados">
                            <thead>
                                <tr>
                                    <th>FR</th>
                                    <th>Cliente</th>
                                    <th>Equipo</th>
                                    <th>Estado</th>
                                    <th>Fecha Ingreso</th>
                                    <th class="text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody id="tbodyEntregados">
                                <!-- JS Rendered -->
                            </tbody>
                        </table>
                    </div>
                    <!-- Pagination -->
                    <div class="card-footer border-secondary d-flex justify-content-between align-items-center py-2">
                        <small class="text-muted" id="infoEntregados">Mostrando 0-0 de 0</small>
                        <nav>
                            <ul class="pagination pagination-sm mb-0" id="paginationEntregados">
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Safe Parse
        let entregadosData = [];
        try {
            entregadosData = JSON.parse('{{ entregados_json | safe }}');
        } catch (e) {
            console.error("Error parsing entregados JSON", e);
        }

        const itemsPerPage = 5;
        let currentPage = 1;
        let filteredData = entregadosData;

        const tbody = document.getElementById('tbodyEntregados');
        const searchInput = document.getElementById('searchEntregados');
        const pagination = document.getElementById('paginationEntregados');
        const info = document.getElementById('infoEntregados');

        function renderTable(page) {
            if (!tbody) return;
            tbody.innerHTML = '';
            
            const start = (page - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            const pageData = filteredData.slice(start, end);

            if (pageData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay registros</td></tr>';
                return;
            }

            pageData.forEach(eq => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge bg-secondary">${eq.fr || 'N/A'}</span></td>
                    <td>${eq.cliente || 'N/A'}</td>
                    <td>
                        <span class="fw-bold">${eq.marca}</span>
                        <small class="d-block text-muted">${eq.modelo}</small>
                    </td>
                    <td><span class="badge bg-success">${eq.estado}</span></td>
                    <td>${eq.fecha_ingreso}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                            data-fr="${eq.fr}" 
                            data-marca="${eq.marca} ${eq.modelo}"
                            data-estado="${eq.estado}" 
                            data-encargado="${eq.encargado}"
                            data-fecha="${eq.fecha_ingreso}"
                            data-reporte="${eq.reporte_cliente || ''}"
                            data-cliente="${eq.cliente || ''}"
                            data-observaciones="${eq.observaciones || ''}"
                            data-serie="${eq.serie || ''}"
                            data-informe="${eq.numero_informe || ''}"
                            data-accesorios="${eq.accesorios || ''}"
                            data-condicion="${eq.condicion || ''}">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            updatePagination();
        }

        function updatePagination() {
            if (!pagination) return;
            pagination.innerHTML = '';
            
            const totalPages = Math.ceil(filteredData.length / itemsPerPage);
            
            // Info text
            const start = (currentPage - 1) * itemsPerPage + 1;
            const end = Math.min(currentPage * itemsPerPage, filteredData.length);
            if (info) info.textContent = `Mostrando ${filteredData.length > 0 ? start : 0}-${end} de ${filteredData.length}`;

            // Prev
            const liPrev = document.createElement('li');
            liPrev.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
            liPrev.innerHTML = `<a class="page-link bg-dark border-secondary text-light" href="#">&laquo;</a>`;
            liPrev.onclick = (e) => { e.preventDefault(); if(currentPage > 1) { currentPage--; renderTable(currentPage); } };
            pagination.appendChild(liPrev);

            // Pages (Limit to 5 visible)
            for (let i = 1; i <= totalPages; i++) {
                if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                     const li = document.createElement('li');
                     li.className = `page-item ${i === currentPage ? 'active' : ''}`;
                     li.innerHTML = `<a class="page-link bg-dark border-secondary text-light" href="#">${i}</a>`;
                     li.onclick = (e) => { e.preventDefault(); currentPage = i; renderTable(currentPage); };
                     pagination.appendChild(li);
                }
            }

            // Next
            const liNext = document.createElement('li');
            liNext.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
            liNext.innerHTML = `<a class="page-link bg-dark border-secondary text-light" href="#">&raquo;</a>`;
            liNext.onclick = (e) => { e.preventDefault(); if(currentPage < totalPages) { currentPage++; renderTable(currentPage); } };
            pagination.appendChild(liNext);
        }

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                filteredData = entregadosData.filter(eq => 
                    (eq.fr || '').toLowerCase().includes(term) ||
                    (eq.cliente || '').toLowerCase().includes(term) ||
                    (eq.marca || '').toLowerCase().includes(term) ||
                    (eq.modelo || '').toLowerCase().includes(term)
                );
                currentPage = 1;
                renderTable(currentPage);
            });
        }

        // Initial Render
        if (filteredData.length > 0) renderTable(currentPage);
        else if (tbody) tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay equipos entregados</td></tr>';
    });
    </script>
    {% endif %}
    """

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Insert in Admin View
# Look for "<!-- 5. TERMINADOS / LISTOS -->" section end.
# It ends with closing /div /div /div /div (approx).
# We look for the next "</div>" (closing row mb-4)
admin_insert_idx = -1
found_terminados = False

for i, line in enumerate(lines):
    if "<!-- 5. TERMINADOS / LISTOS -->" in line:
        found_terminados = True
    
    if found_terminados:
         # Rough heuristic: content for terminados ends.
         # Look for the CLOSING of the "row g-4 mb-4" that wraps the cards.
         # This row started at line ~98.
         # It closes before {% else %} (User switch).
         if "{% else %}" in line:
             admin_insert_idx = i
             break

if admin_insert_idx != -1:
    # Insert BEFORE the {% else %}
    # But wait, the row closing div must be respected.
    # Usually the structure is: <div row> ...cols... </div> {% else %}
    # So inserting BEFORE {% else %} puts it AFTER the row div? 
    # Or implies we are appending to the list of elements?
    # If I insert BEFORE {% else %}, I am inside the {% if is_admin_view %}.
    # The `row` closes before that?
    # I should insert it effectively at the bottom of the admin container.
    lines.insert(admin_insert_idx, get_entregados_block())

# 2. Insert in User View
# Logic: Inside {% else %} of Almacen check.
# Find "{% if current_user.role|lower == UserRoles.ALMACEN|lower %}"
# Then find the corresponding {% else %}.
# Then find the {% endif %} of that block.
# We want to insert inside the {% else %} block (Rec/Ops), at the end.

user_almacen_idx = -1
for i, line in enumerate(lines):
    if "UserRoles.ALMACEN|lower" in line and "{% if" in line:
        user_almacen_idx = i
        break

if user_almacen_idx != -1:
    # Find the ELSE
    user_else_idx = -1
    for i in range(user_almacen_idx, len(lines)):
        if "{% else %}" in line: # Careful, might match nested if
            # Assuming simple nesting here based on file view
            pass
    
    # Actually, simpler:
    # The User View structure is: Almacen HTML ... {% else %} ... Rec/Ops HTML ... {% endif %}
    # I want to append to Rec/Ops HTML.
    # So I insert BEFORE the `{% endif %}` that closes the Almacen check.
    
    # Let's find that specific {% endif %}.
    # It should be the one closing the Almacen block.
    # We can search backwards from the end of the file? No.
    # Search forward from Almacen check.
    
    # Since I inserted content earlier into `lines`, indices shift.
    # Re-calculate index or handle shift.
    shift = 1 # We inserted 1 block (which is effectively 1 item in list insert logic, but wait, get_entregados_block returns a string, so 1 element).
    
    # Wait, insert adds 1 element to list so shift is 1.
    
    # Let's search again in modified lines.
    user_almacen_idx = -1
    for i, line in enumerate(lines):
        if "UserRoles.ALMACEN|lower" in line and "{% if" in line:
            user_almacen_idx = i
            break
            
    if user_almacen_idx != -1:
        # Find the NEXT `{% endif %}` corresponding to this.
        # This might be tricky if there are nested ifs.
        # Looking at file: Almacen loop has `{% if ... %}` inside? Not really.
        # It has `table`, `thead`, `tbody`. `for` loop. `if` inside for? Yes `if 'diagnostico'`.
        # So simpler to look for "<!-- REPLCE ME -->"? No.
        
        # Look for the last `</div>` of the Rec/Ops section.
        # The Rec/Ops section ends before `{% endif %}`.
        # I will inject it Just BEFORE the `{% endif %}` that matches the Almacen check.
        # How to identify it? Indentation or Context?
        
        # Context: "<!-- RECEPCION (VENTAS) / OPERACIONES LOGIC -->" usually precedes the ELSE.
        # It's not in the file currently (it was lines 245-353 in old view, but I see `{% else %}` at line ~445 in my mind).
        
        # Let's assume the LAST `{% endif %}` in the file closes the `is_admin_view`.
        # The `{% endif %}` before that closes the `Almacen` check.
        
        # Let's verify with a bottom-up search.
        # ...
        # {% endif %} (Almacen)
        # </div> (Main container)
        # {% endif %} (Admin View)
        # {% endblock %}
        
        # So I will look for the 2nd to last {% endif %}.
        
        endifs = [i for i, line in enumerate(lines) if "{% endif %}" in line]
        if len(endifs) >= 2:
            target_endif = endifs[-2] # 2nd from last
            # Insert before it.
            lines.insert(target_endif, get_entregados_block())
            
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Dashboard Updated.")
