
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to locate the block I inserted previously.
# I can look for "<!-- 3. CATEGORIZED LISTS (REPLACES MAIN TABLE) -->"
# and replace everything until "{% endif %}" (Line ~353).

start_marker = "<!-- 3. CATEGORIZED LISTS (REPLACES MAIN TABLE) -->"
start_idx = -1
for i, line in enumerate(lines):
    if start_marker in line:
        start_idx = i
        break

if start_idx == -1:
    print("Start marker not found")
    exit(1)

# Find ending.
# I will look for "{% endif %}" that closes the User View loop.
# It should be the one after "<!-- ALMACEN LOGIC -->" block.
# I'll search for "{% endif %}" after start_idx.
# And ensure it's the one closing the role check.
# Actually, the block I inserted ends with "{% endif %}" (Line 353 in previous version).
# BUT, I stuck it *before* lines[final_endif_idx-2].
# Let's inspect the `dashboard.html` around expected area.
# I will just define the new content and regex replace or precise line replace if I can find the markers.
# The markers "<!-- ALMACEN LOGIC -->" and so on are unique.

# I will replace from `start_idx` down to the `{% endif %}` that corresponds to the layout.
# Note: The Almacen logic is wrapped in `{% if ...ALMACEN... %}` ... `{% else %}` ... `{% endif %}`.
# I will replace that ENTIRE logic block.

# New Content Construction
# Stacked Layout = col-12 for all cards.
# Columns logic as requested.

new_content = """    <!-- 3. CATEGORIZED LISTS (REPLACES MAIN TABLE) -->
    <div class="row mb-3 align-items-center">
        <div class="col">
             <h5 class="mb-0 text-white"><i class="fas fa-list me-2"></i> Gestionar Tareas</h5>
        </div>
        <div class="col-auto d-flex gap-2">
            {% if current_user.role in [UserRoles.RECEPCION, UserRoles.ADMIN] %}
            <button class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#createEquipmentModal">
                <i class="fas fa-plus-circle"></i> Nuevo Equipo
            </button>
            {% endif %}
            <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-primary" title="Ir al Panel Completo">
                <i class="fas fa-expand"></i> Pantalla Completa
            </a>
        </div>
    </div>

    <!-- ALMACEN LOGIC -->
    {% if current_user.role|lower == UserRoles.ALMACEN|lower %}
        <div class="row g-4">
            <!-- Repuestos Diagnóstico -->
            <div class="col-12">
                <div class="card bg-dark border-secondary">
                    <div class="card-header border-secondary text-warning">
                        <i class="fas fa-boxes me-2"></i> Repuestos para Diagnóstico
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0 align-middle">
                                <thead>
                                    <tr>
                                        <th>FR</th>
                                        <th>Cliente</th>
                                        <th>Equipo</th>
                                        <th>Estado</th>
                                        <th>Fecha</th>
                                        <th>Días</th>
                                        <th class="text-end">Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for eq in equipos_relevantes if 'diagnostico' in eq.estado|lower or 'consumible' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-secondary">{{ eq.fr or 'N/A' }}</span></td>
                                        <td>{{ eq.cliente or 'N/A' }}</td>
                                        <td>
                                            <div class="fw-bold">{{ eq.marca }}</div>
                                            <small class="text-muted">{{ eq.modelo }}</small>
                                        </td>
                                        <td><span class="badge bg-dark border border-warning text-warning">{{ eq.estado }}</span></td>
                                        <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') }}</td>
                                        <td>
                                            {% set dias = (now() - eq.fecha_ingreso).days %}
                                            <span class="badge {% if dias > 7 %}bg-danger{% elif dias > 5 %}bg-warning{% else %}bg-success{% endif %}">{{ dias }}</span>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e }}"
                                                data-observaciones="{{ eq.observaciones | e }}"
                                                data-serie="{{ eq.serie | e }}"
                                                data-informe="{{ eq.numero_informe | e }}"
                                                data-accesorios="{{ eq.accesorios | e }}"
                                                data-condicion="{{ eq.condicion | e }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="7" class="text-center text-muted">Sin pendientes</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Repuestos Servicio -->
            <div class="col-12">
                <div class="card bg-dark border-secondary">
                    <div class="card-header border-secondary text-info">
                        <i class="fas fa-cogs me-2"></i> Repuestos para Servicio
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0 align-middle">
                                <thead>
                                    <tr>
                                        <th>FR</th>
                                        <th>Cliente</th>
                                        <th>Equipo</th>
                                        <th>Estado</th>
                                        <th>Fecha</th>
                                        <th>Días</th>
                                        <th class="text-end">Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for eq in equipos_relevantes if 'servicio' in eq.estado|lower and 'repuesto' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-secondary">{{ eq.fr or 'N/A' }}</span></td>
                                        <td>{{ eq.cliente or 'N/A' }}</td>
                                        <td>
                                            <div class="fw-bold">{{ eq.marca }}</div>
                                            <small class="text-muted">{{ eq.modelo }}</small>
                                        </td>
                                        <td><span class="badge bg-dark border border-info text-info">{{ eq.estado }}</span></td>
                                        <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') }}</td>
                                        <td>
                                            {% set dias = (now() - eq.fecha_ingreso).days %}
                                            <span class="badge {% if dias > 7 %}bg-danger{% elif dias > 5 %}bg-warning{% else %}bg-success{% endif %}">{{ dias }}</span>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e }}"
                                                data-observaciones="{{ eq.observaciones | e }}"
                                                data-serie="{{ eq.serie | e }}"
                                                data-informe="{{ eq.numero_informe | e }}"
                                                data-accesorios="{{ eq.accesorios | e }}"
                                                data-condicion="{{ eq.condicion | e }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="7" class="text-center text-muted">Sin pendientes</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    {% else %}
        <!-- RECEPCION (VENTAS) / OPERACIONES LOGIC -->
         <div class="row g-4">
            <!-- LOOP OVER CATEGORIES -->
            <!-- We define categories manualy to ensure order: Pendiente, Diag, Aprobado -->
            
            <!-- Col 1: Pendientes de Aprobación -->
            <div class="col-12">
                <div class="card bg-dark border-secondary">
                    <div class="card-header border-secondary text-warning">
                        <i class="fas fa-clock me-2"></i> Pendientes de Aprobación
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0 align-middle">
                                <thead>
                                    <tr>
                                        <th>FR</th>
                                        <!-- Recepcion sees Client -->
                                        {% if current_user.role|lower == UserRoles.RECEPCION|lower %}
                                        <th>Cliente</th>
                                        {% endif %}
                                        <th>Equipo</th>
                                        <th>Estado</th>
                                        <!-- Operaciones sees Encargado -->
                                        {% if current_user.role|lower == UserRoles.OPERACIONES|lower %}
                                        <th>Encargado</th>
                                        {% endif %}
                                        <th>Fecha</th>
                                        <th>Días</th>
                                        <th class="text-end">Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for eq in equipos_relevantes if 'pendiente' in eq.estado|lower and 'aprobacion' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-warning text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                        
                                        {% if current_user.role|lower == UserRoles.RECEPCION|lower %}
                                        <td>{{ eq.cliente or 'N/A' }}</td>
                                        {% endif %}
                                        
                                        <td>
                                            <div class="fw-bold">{{ eq.marca }}</div>
                                            <small class="text-muted">{{ eq.modelo }}</small>
                                        </td>
                                        <td><span class="badge bg-dark border border-warning text-warning">{{ eq.estado }}</span></td>
                                        
                                        {% if current_user.role|lower == UserRoles.OPERACIONES|lower %}
                                        <td>{{ eq.encargado or 'N/A' }}</td>
                                        {% endif %}

                                        <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') }}</td>
                                        <td>
                                            {% set dias = (now() - eq.fecha_ingreso).days %}
                                            <span class="badge {% if dias > 7 %}bg-danger{% elif dias > 5 %}bg-warning{% else %}bg-success{% endif %}">{{ dias }}</span>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e }}"
                                                data-observaciones="{{ eq.observaciones | e }}"
                                                data-serie="{{ eq.serie | e }}"
                                                data-informe="{{ eq.numero_informe | e }}"
                                                data-accesorios="{{ eq.accesorios | e }}"
                                                data-condicion="{{ eq.condicion | e }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <!-- Colspan dynamic based on role -->
                                    <tr><td colspan="8" class="text-center text-muted">Sin equipos</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Col 2: En Diagnóstico -->
            <div class="col-12">
                <div class="card bg-dark border-secondary">
                    <div class="card-header border-secondary text-info">
                        <i class="fas fa-microscope me-2"></i> En Diagnóstico
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0 align-middle">
                                <thead>
                                    <tr>
                                        <th>FR</th>
                                        <!-- Recepcion sees Client -->
                                        {% if current_user.role|lower == UserRoles.RECEPCION|lower %}
                                        <th>Cliente</th>
                                        {% endif %}
                                        <th>Equipo</th>
                                        <th>Estado</th>
                                        <!-- Operaciones sees Encargado -->
                                        {% if current_user.role|lower == UserRoles.OPERACIONES|lower %}
                                        <th>Encargado</th>
                                        {% endif %}
                                        <th>Fecha</th>
                                        <th>Días</th>
                                        <th class="text-end">Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for eq in equipos_relevantes if 'diagnostico' in eq.estado|lower or 'consumible' in eq.estado|lower or 'repuesto entregado' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-info text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                        
                                        {% if current_user.role|lower == UserRoles.RECEPCION|lower %}
                                        <td>{{ eq.cliente or 'N/A' }}</td>
                                        {% endif %}
                                        
                                        <td>
                                            <div class="fw-bold">{{ eq.marca }}</div>
                                            <small class="text-muted">{{ eq.modelo }}</small>
                                        </td>
                                        <td><span class="badge bg-dark border border-info text-info">{{ eq.estado }}</span></td>
                                        
                                        {% if current_user.role|lower == UserRoles.OPERACIONES|lower %}
                                        <td>{{ eq.encargado or 'N/A' }}</td>
                                        {% endif %}

                                        <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') }}</td>
                                        <td>
                                            {% set dias = (now() - eq.fecha_ingreso).days %}
                                            <span class="badge {% if dias > 7 %}bg-danger{% elif dias > 5 %}bg-warning{% else %}bg-success{% endif %}">{{ dias }}</span>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e }}"
                                                data-observaciones="{{ eq.observaciones | e }}"
                                                data-serie="{{ eq.serie | e }}"
                                                data-informe="{{ eq.numero_informe | e }}"
                                                data-accesorios="{{ eq.accesorios | e }}"
                                                data-condicion="{{ eq.condicion | e }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="8" class="text-center text-muted">Sin equipos</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Col 3: Aprobados / Servicio -->
            <div class="col-12">
                <div class="card bg-dark border-secondary">
                    <div class="card-header border-secondary text-success">
                        <i class="fas fa-check-circle me-2"></i> Aprobados / Servicio
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0 align-middle">
                                <thead>
                                    <tr>
                                        <th>FR</th>
                                        <!-- Recepcion sees Client -->
                                        {% if current_user.role|lower == UserRoles.RECEPCION|lower %}
                                        <th>Cliente</th>
                                        {% endif %}
                                        <th>Equipo</th>
                                        <th>Estado</th>
                                        <!-- Operaciones sees Encargado -->
                                        {% if current_user.role|lower == UserRoles.OPERACIONES|lower %}
                                        <th>Encargado</th>
                                        {% endif %}
                                        <th>Fecha</th>
                                        <th>Días</th>
                                        <th class="text-end">Acción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for eq in equipos_relevantes if 'aprobado' in eq.estado|lower or 'servicio' in eq.estado|lower or 'entregado' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-success">{{ eq.fr or 'N/A' }}</span></td>
                                        
                                        {% if current_user.role|lower == UserRoles.RECEPCION|lower %}
                                        <td>{{ eq.cliente or 'N/A' }}</td>
                                        {% endif %}
                                        
                                        <td>
                                            <div class="fw-bold">{{ eq.marca }}</div>
                                            <small class="text-muted">{{ eq.modelo }}</small>
                                        </td>
                                        <td><span class="badge bg-dark border border-success text-success">{{ eq.estado }}</span></td>
                                        
                                        {% if current_user.role|lower == UserRoles.OPERACIONES|lower %}
                                        <td>{{ eq.encargado or 'N/A' }}</td>
                                        {% endif %}

                                        <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') }}</td>
                                        <td>
                                            {% set dias = (now() - eq.fecha_ingreso).days %}
                                            <span class="badge {% if dias > 7 %}bg-danger{% elif dias > 5 %}bg-warning{% else %}bg-success{% endif %}">{{ dias }}</span>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e }}"
                                                data-observaciones="{{ eq.observaciones | e }}"
                                                data-serie="{{ eq.serie | e }}"
                                                data-informe="{{ eq.numero_informe | e }}"
                                                data-accesorios="{{ eq.accesorios | e }}"
                                                data-condicion="{{ eq.condicion | e }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="8" class="text-center text-muted">Sin equipos</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
         </div>
    {% endif %}
"""

# Find the end of the block.
# We look for the "{% endif %}" that closes the User View role logic.
# My last insertion replaced up to line 352. 
# And the next line was "{% endif %}" (Line 353).
# So I should search for "{% endif %}" from start_idx.
# And replace everything between start_idx and that endif.

end_idx = -1
for i in range(start_idx, len(lines)):
    if "{% endif %}" in lines[i]:
        # This is the endif for the role check logic (Almacen vs others)
        # Wait, the role check logic IS part of my inserted block.
        # "    {% if current_user.role|lower == UserRoles.ALMACEN|lower %}"
        # "    {% else %}"
        # "    {% endif %}"
        # This whole block is what I inserted.
        # But wait, the outer structure was:
        # 1. Header (Inserted)
        # 2. IF ALMACEN (Inserted) ... ELSE ... ENDIF (Inserted).
        
        # So I successfully replaced 246-347 with ALL of that.
        # AND it was followed by "{% endif %}" (Line 353) which closes "is_admin_view".
        
        # So I want to find the "{% endif %}" that closes "is_admin_view". 
        # But wait, my previous script replaced UP TO final_endif_idx-2.
        # My inserted content ended with `{% endif %}` (for Almacen loop).
        # So now in the file there are TWO `{% endif %}`s close to each other?
        # 1. The one closing Almacen loop.
        # 2. The one closing is_admin_view.
        
        pass

# Safe strategy:
# Replace from `start_marker` down to the `{% endif %}` (lines[final_endif_idx]) of the `is_admin_view`.
# Actually, I can just replace from `start_marker` down to line `<!-- MODAL REGISTRO DE EQUIPO -->`.
# This is physically safer.

modal_marker = "<!-- MODAL REGISTRO DE EQUIPO -->"
modal_idx = -1
for i in range(start_idx, len(lines)):
    if modal_marker in lines[i]:
        modal_idx = i
        break

if modal_idx == -1:
    print("Modal marker not found")
    exit(1)

# The block to replace is lines[start_idx : modal_idx].
# Wait, `modal_idx` starts the modal.
# The `{% endif %}` for is_admin_view is usually just before the modal.
# Let's verify line before modal_idx.
# lines[modal_idx-1] should be empty or space.
# lines[modal_idx-2] should be `{% endif %}` (for is_admin_view).
# My inserted content ENDED with `{% endif %}` (for Almacen).
# So lines[modal_idx-3] might be `{% endif %}` for Almacen?

# I will replace lines[start_idx : modal_idx-2].
# Leaving the `{% endif %}` for is_admin_view intact.
# Wait, if I replace up to modal_idx, I risk overwriting the admin_view endif.
# Let's inspect lines before modal.

# print(lines[modal_idx-10:modal_idx]) 
# (Mentally)

# I will write the `new_content` + `\n`.
# And I will replace `lines[start_idx : modal_idx-1]`.
# Why -1? Keep the `{% endif %}` which is likely at modal_idx-2?
# Let's stick to replacing strictly the block I know I own.
# My block starts with `<!-- 3. CATEGORIZED LISTS ... -->`.
# My block ends with `{% endif %}` (Almacen).
# Then there is `</div>` (from the original file? I kept it in the script? "lines[final_endif_idx-2:]").
# Line 351 was `</div>`.
# I concatenated: `lines[:start_idx] + [new_content] + lines[final_endif_idx-2:]`.
# `final_endif_idx-2` was likely line 351 `</div>`.
# So my file currently has:
# ...
# {% endif %} (Almacen)
# </div>
# {% endif %} (Admin View)
# 
# So I should find `</div>` before `{% endif %}` (Admin View) and replace up to there.

# Actually, I'll just replace from `start_marker` until `<!-- MODAL` and assume standard structure, BUT:
# I must ensure I put back `</div>` and `{% endif %}` if I overwrite them.
# The safest way: 
# Replace from `start_marker` to `modal_marker`.
# And `new_content` MUST end with `</div>\n{% endif %}\n`.
# This guarantees structural integrity.

# Let's verify if `start_marker` is indeed after current `is_admin_view`?
# No, `start_marker` replaces the USER view table.
# `is_admin_view` block starts at top. `{% else %}` at middle.
# So this IS the user view.
# The user view ends with `</div>` (main container or section?) and `{% endif %}`.

new_content_with_closers = new_content + "\n</div>\n{% endif %}\n\n"

lines_out = lines[:start_idx] + [new_content_with_closers] + lines[modal_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines_out)
    
print("Updated successfully.")
