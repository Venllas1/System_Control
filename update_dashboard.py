
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find Start of Block
start_marker = "<!-- 3. MAIN TABLE (REPLACES CARDS) -->"
start_idx = -1
for i, line in enumerate(lines):
    if start_marker in line:
        start_idx = i
        break

if start_idx == -1:
    print("Start marker not found")
    exit(1)

# Find End of Block (The endif after the table)
# We know the table ends with </div> lines, then {% endif %} around line 353.
# We will search for {% endif %} after start_idx
end_idx = -1
for i in range(start_idx, len(lines)):
    if "{% endif %}" in lines[i]:
        # Verify it's the one we want (User view end)
        # Check context? It's the first endif after the main table.
        # The main table card doesn't contain endif (except inside loops? No).
        # Loops use {% endfor %}. Checks use {% endif %}.
        # Inside the table logic:
        # Line 269: {% endif %} (Client header)
        # Line 275: {% endif %} (Encargado header)
        # Line 286: {% endif %} (Client cell)
        # Line 293: {% endif %} (Condicion)
        # Line 312: {% endif %} (Encargado cell)
        # Line 353: {% endif %} (Main User View)
        # So I need to be careful.
        # The table ends at line 346/347 </div> </div>.
        # I want to replace everything from start_idx+1 up to (but not including) the LAST </div> before the LAST {% endif %}?
        # Actually I want to replace the `card` div completely.
        # Let's verify the Card closing div. lines[347] is "    </div>\n"
        pass
        
# Hardcode approach based on line reading:
# Start_idx is line 245 (0-indexed -> 245).
# I want to replace lines[start_idx+1 : 353?]. 
# Lines[351] is "</div>\n". Lines[352] is "\n". Lines[353] is "{% endif %}\n".
# So I want to replace from start_idx+1 UP TO line 351 (inclusive or exclusive?).
# I want to KEEP line 351 (</div>) if it closes main-container.
# So replace up to 350.

# Let's find index of line 353 ("{% endif %}") and go back 2 lines.
final_endif_idx = -1
# Search backwards from 360 region
for i in range(360, start_idx, -1):
     if i < len(lines) and "{% endif %}" in lines[i]:
         final_endif_idx = i
         break

if final_endif_idx == -1:
    # Try forward search
    for i in range(start_idx, len(lines)):
        if "{% endif %}" in lines[i] and i > 350: # Heuristic
             final_endif_idx = i
             break

# Verify we found the right one.
# It should be around line 353.
print(f"Start index: {start_idx}")
print(f"End index candidate: {final_endif_idx}")

# The block to replace is lines[start_idx+1 : final_endif_idx-2] ?
# Lines to remove: The Card Div.
# Card starts at start_idx+1.
# Card ends BEFORE the final </div> (which is main-container).
# So we remove lines[start_idx+1 : final_endif_idx-1] ?
# lines[final_endif_idx-1] is blank?
# lines[final_endif_idx-2] is </div> (main container?)

# Let's look at the content to be inserted.
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
            <div class="col-md-6">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-header border-secondary text-warning">
                        <i class="fas fa-boxes me-2"></i> Repuestos para Diagnóstico
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0">
                                <tbody>
                                    {% for eq in equipos_relevantes if 'diagnostico' in eq.estado|lower or 'consumible' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-secondary">{{ eq.fr or 'N/A' }}</span></td>
                                        <td><small>{{ eq.marca }} {{ eq.modelo }}</small></td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr or 'N/A' }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') if eq.fecha_ingreso else 'N/A' }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e or 'N/A' }}"
                                                data-observaciones="{{ eq.observaciones | e or 'Sin observaciones' }}"
                                                data-serie="{{ eq.serie | e or 'N/A' }}"
                                                data-informe="{{ eq.numero_informe | e or 'N/A' }}"
                                                data-accesorios="{{ eq.accesorios | e or 'Ninguno' }}"
                                                data-condicion="{{ eq.condicion | e or 'Regular' }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="text-center text-muted">Sin pendientes</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Repuestos Servicio -->
            <div class="col-md-6">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-header border-secondary text-info">
                        <i class="fas fa-cogs me-2"></i> Repuestos para Servicio
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0">
                                <tbody>
                                    {% for eq in equipos_relevantes if 'servicio' in eq.estado|lower and 'repuesto' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-secondary">{{ eq.fr or 'N/A' }}</span></td>
                                        <td><small>{{ eq.marca }} {{ eq.modelo }}</small></td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr or 'N/A' }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') if eq.fecha_ingreso else 'N/A' }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e or 'N/A' }}"
                                                data-observaciones="{{ eq.observaciones | e or 'Sin observaciones' }}"
                                                data-serie="{{ eq.serie | e or 'N/A' }}"
                                                data-informe="{{ eq.numero_informe | e or 'N/A' }}"
                                                data-accesorios="{{ eq.accesorios | e or 'Ninguno' }}"
                                                data-condicion="{{ eq.condicion | e or 'Regular' }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="text-center text-muted">Sin pendientes</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    {% else %}
        <!-- RECEPCION / OPERACIONES / DEFAULT: 3 COLUMNS -->
         <div class="row g-4">
            <!-- Col 1: Pendientes de Aprobación -->
            <div class="col-md-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-header border-secondary text-warning">
                        <i class="fas fa-clock me-2"></i> Pendientes de Aprobación
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0">
                                <tbody>
                                    {% for eq in equipos_relevantes if 'pendiente' in eq.estado|lower and 'aprobacion' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-warning text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                        <td>
                                            <div class="small fw-bold">{{ eq.marca }}</div>
                                            <div class="text-muted small">{{ eq.modelo }}</div>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr or 'N/A' }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') if eq.fecha_ingreso else 'N/A' }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e or 'N/A' }}"
                                                data-observaciones="{{ eq.observaciones | e or 'Sin observaciones' }}"
                                                data-serie="{{ eq.serie | e or 'N/A' }}"
                                                data-informe="{{ eq.numero_informe | e or 'N/A' }}"
                                                data-accesorios="{{ eq.accesorios | e or 'Ninguno' }}"
                                                data-condicion="{{ eq.condicion | e or 'Regular' }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="text-center text-muted">Sin equipos</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Col 2: En Diagnóstico -->
            <div class="col-md-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-header border-secondary text-info">
                        <i class="fas fa-microscope me-2"></i> En Diagnóstico
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0">
                                <tbody>
                                    {% for eq in equipos_relevantes if 'diagnostico' in eq.estado|lower or 'consumible' in eq.estado|lower or 'repuesto entregado' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-info text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                        <td>
                                            <div class="small fw-bold">{{ eq.marca }}</div>
                                            <div class="text-muted small">{{ eq.estado }}</div>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr or 'N/A' }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') if eq.fecha_ingreso else 'N/A' }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e or 'N/A' }}"
                                                data-observaciones="{{ eq.observaciones | e or 'Sin observaciones' }}"
                                                data-serie="{{ eq.serie | e or 'N/A' }}"
                                                data-informe="{{ eq.numero_informe | e or 'N/A' }}"
                                                data-accesorios="{{ eq.accesorios | e or 'Ninguno' }}"
                                                data-condicion="{{ eq.condicion | e or 'Regular' }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="text-center text-muted">Sin equipos</td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Col 3: Aprobados / Servicio -->
            <div class="col-md-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-header border-secondary text-success">
                        <i class="fas fa-check-circle me-2"></i> Aprobados / Servicio
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover mb-0">
                                <tbody>
                                    {% for eq in equipos_relevantes if 'aprobado' in eq.estado|lower or 'servicio' in eq.estado|lower or 'entregado' in eq.estado|lower %}
                                    <tr>
                                        <td><span class="badge bg-success">{{ eq.fr or 'N/A' }}</span></td>
                                        <td>
                                            <div class="small fw-bold">{{ eq.marca }}</div>
                                            <div class="text-muted small">{{ eq.estado }}</div>
                                        </td>
                                        <td class="text-end">
                                             <button class="btn btn-sm btn-outline-info" onclick="showInfo(this)"
                                                data-fr="{{ eq.fr or 'N/A' }}" data-marca="{{ eq.marca }} {{ eq.modelo }}"
                                                data-estado="{{ eq.estado }}" data-encargado="{{ eq.encargado }}"
                                                data-fecha="{{ eq.fecha_ingreso.strftime('%Y-%m-%d') if eq.fecha_ingreso else 'N/A' }}"
                                                data-reporte="{{ eq.reporte_cliente | e }}"
                                                data-cliente="{{ eq.cliente | e or 'N/A' }}"
                                                data-observaciones="{{ eq.observaciones | e or 'Sin observaciones' }}"
                                                data-serie="{{ eq.serie | e or 'N/A' }}"
                                                data-informe="{{ eq.numero_informe | e or 'N/A' }}"
                                                data-accesorios="{{ eq.accesorios | e or 'Ninguno' }}"
                                                data-condicion="{{ eq.condicion | e or 'Regular' }}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    {% else %}
                                    <tr><td colspan="3" class="text-center text-muted">Sin equipos</td></tr>
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

# Stitch it
# Keep everything BEFORE start_idx (exclusive? No, we kept the comment in start_marker so start_idx is the comment line)
# We want to keep lines[0...start_idx-1].
# Actually, new_content HAS the start_marker.
# So replace lines[start_idx : final_endif_idx-2] ?
# Let's say we replace from start_idx up to the line BEFORE </div> (line 351).
# which is final_endif_idx - 2.

final_lines = lines[:start_idx] + [new_content + "\n"] + lines[final_endif_idx-2:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("File updated successfully.")
