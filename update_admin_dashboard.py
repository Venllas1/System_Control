
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# TARGET BLOCK: "<!-- TODOS LOS EQUIPOS ACTIVOS -->" (line ~95) up to the "{% else %}" (line ~162) that starts the USER VIEW.
start_marker = "<!-- TODOS LOS EQUIPOS ACTIVOS -->"
end_marker = "<!-- VISTA USUARIO" # Actually it's {% else %} but let's find the content before it.

# Find extraction points
start_idx = -1
for i, line in enumerate(lines):
    if start_marker in line:
        start_idx = i
        break

if start_idx == -1:
    print("Start marker not found")
    exit(1)

# Find the {% else %} associated with {% if is_admin_view %} (Line 8)
# The block ends before the {% else %} which is around line 162.
# We can search for the {% else %} that follows the table </div>.
end_idx = -1
# Scan forward from start_idx
for i in range(start_idx, len(lines)):
    if "{% else %}" in lines[i]:
        end_idx = i
        break

if end_idx == -1:
    print("End marker not found")
    exit(1)

# New HTML Content for Admin Stacked Cards
new_html = """    <!-- VISTA ADMIN: TARJETAS APILADAS POR CATEGORIA -->
    <div class="row g-4 mb-4">
        
        <!-- 1. PENDIENTES DE APROBACION -->
        <div class="col-12">
            <div class="card bg-dark border-secondary shadow-sm">
                <div class="card-header border-secondary text-warning">
                    <i class="fas fa-clock me-2"></i> Pendientes de Aprobación
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
                                    <th>Encargado</th>
                                    <th>Fecha</th>
                                    <th>Días</th>
                                    <th class="text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% set pendientes = [] %}
                                {% for eq in todos_equipos if 'pendiente' in eq.estado|lower or 'espera' in eq.estado|lower and 'diagnostico' not in eq.estado|lower and 'repuesto' not in eq.estado|lower and 'servicio' not in eq.estado|lower %}
                                <tr>
                                    <td><span class="badge bg-warning text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                    <td>{{ eq.cliente or 'N/A' }}</td>
                                    <td>
                                        <span class="fw-bold">{{ eq.marca }}</span>
                                        <small class="d-block text-muted">{{ eq.modelo }}</small>
                                    </td>
                                    <td><span class="badge bg-secondary">{{ eq.estado }}</span></td>
                                    <td>{{ eq.encargado or 'N/A' }}</td>
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
                                        <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr><td colspan="8" class="text-center text-muted">No hay equipos pendientes</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. EN DIAGNOSTICO / REVISION -->
        <div class="col-12">
            <div class="card bg-dark border-secondary shadow-sm">
                <div class="card-header border-secondary text-info">
                    <i class="fas fa-microscope me-2"></i> En Diagnóstico / Revisión
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
                                    <th>Encargado</th>
                                    <th>Fecha</th>
                                    <th>Días</th>
                                    <th class="text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for eq in todos_equipos if 'diagnostico' in eq.estado|lower or 'revision' in eq.estado|lower %}
                                <tr>
                                    <td><span class="badge bg-info text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                    <td>{{ eq.cliente or 'N/A' }}</td>
                                    <td>
                                        <span class="fw-bold">{{ eq.marca }}</span>
                                        <small class="d-block text-muted">{{ eq.modelo }}</small>
                                    </td>
                                    <td><span class="badge bg-secondary">{{ eq.estado }}</span></td>
                                    <td>{{ eq.encargado or 'N/A' }}</td>
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
                                        <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr><td colspan="8" class="text-center text-muted">No hay equipos en diagnóstico</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. ESPERA DE REPUESTOS -->
        <div class="col-12">
            <div class="card bg-dark border-secondary shadow-sm">
                <div class="card-header border-secondary text-warning">
                    <i class="fas fa-boxes me-2"></i> Espera de Repuestos / Consumibles
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
                                    <th>Encargado</th>
                                    <th>Fecha</th>
                                    <th>Días</th>
                                    <th class="text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for eq in todos_equipos if 'repuesto' in eq.estado|lower or 'consumible' in eq.estado|lower %}
                                <tr>
                                    <td><span class="badge bg-warning text-dark">{{ eq.fr or 'N/A' }}</span></td>
                                    <td>{{ eq.cliente or 'N/A' }}</td>
                                    <td>
                                        <span class="fw-bold">{{ eq.marca }}</span>
                                        <small class="d-block text-muted">{{ eq.modelo }}</small>
                                    </td>
                                    <td><span class="badge bg-secondary">{{ eq.estado }}</span></td>
                                    <td>{{ eq.encargado or 'N/A' }}</td>
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
                                        <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr><td colspan="8" class="text-center text-muted">No hay equipos en espera de repuestos</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- 4. APROBADOS / EN SERVICIO -->
        <div class="col-12">
            <div class="card bg-dark border-secondary shadow-sm">
                <div class="card-header border-secondary text-success">
                    <i class="fas fa-tools me-2"></i> Aprobados / En Servicio
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
                                    <th>Encargado</th>
                                    <th>Fecha</th>
                                    <th>Días</th>
                                    <th class="text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for eq in todos_equipos if ('aprobado' in eq.estado|lower or 'servicio' in eq.estado|lower) and 'repuesto' not in eq.estado|lower and 'culminado' not in eq.estado|lower %}
                                <tr>
                                    <td><span class="badge bg-success">{{ eq.fr or 'N/A' }}</span></td>
                                    <td>{{ eq.cliente or 'N/A' }}</td>
                                    <td>
                                        <span class="fw-bold">{{ eq.marca }}</span>
                                        <small class="d-block text-muted">{{ eq.modelo }}</small>
                                    </td>
                                    <td><span class="badge bg-secondary">{{ eq.estado }}</span></td>
                                    <td>{{ eq.encargado or 'N/A' }}</td>
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
                                        <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr><td colspan="8" class="text-center text-muted">No hay equipos en servicio</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

         <!-- 5. TERMINADOS / LISTOS -->
        <div class="col-12">
            <div class="card bg-dark border-secondary shadow-sm">
                <div class="card-header border-secondary text-light">
                    <i class="fas fa-check-double me-2"></i> Terminados / Listos para Entrega
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
                                    <th>Encargado</th>
                                    <th>Fecha</th>
                                    <th>Días</th>
                                    <th class="text-end">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for eq in todos_equipos if 'culminado' in eq.estado|lower or 'entregado' in eq.estado|lower %}
                                <tr>
                                    <td><span class="badge bg-secondary">{{ eq.fr or 'N/A' }}</span></td>
                                    <td>{{ eq.cliente or 'N/A' }}</td>
                                    <td>
                                        <span class="fw-bold">{{ eq.marca }}</span>
                                        <small class="d-block text-muted">{{ eq.modelo }}</small>
                                    </td>
                                    <td><span class="badge bg-success">{{ eq.estado }}</span></td>
                                    <td>{{ eq.encargado or 'N/A' }}</td>
                                    <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') }}</td>
                                    <td>
                                        {% set dias = (now() - eq.fecha_ingreso).days %}
                                        <span class="badge bg-success">{{ dias }}</span>
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
                                        <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr><td colspan="8" class="text-center text-muted">No hay equipos terminados recientes</td></tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

    </div>
"""

# Replace content
lines = lines[:start_idx] + [new_html] + lines[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Admin Dashboard updated successfully.")
