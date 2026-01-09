
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to find the START of the damage.
# It seems to be after the Import Button content.
# Expected structure:
# Header -> Stats -> Critical -> Stacked Cards (1, 2, 3, 4, 5)

# 1. Locate the Import Button lines.
import_btn_line = -1
for i, line in enumerate(lines):
    if 'data-bs-target="#importInformesModal"' in line:
        import_btn_line = i
        break

if import_btn_line == -1:
    print("Could not find import button anchor.")
    exit(1)

# The file currently has the Import Button, then maybe some blank lines, then "<!-- 2. EN DIAGNOSTICO / REVISION -->"
# We want to INSERT the missing content (Header finish, Stats, Critical, Card 1) BEFORE Card 2.

card_2_marker = "<!-- 2. EN DIAGNOSTICO / REVISION -->"
card_2_line = -1
for i, line in enumerate(lines):
    if card_2_marker in line:
        card_2_line = i
        break

if card_2_line == -1:
    print("Could not find Card 2 marker.")
    exit(1)

# We will replace everything between Import Button Line (and its closing tags) and Card 2 marker.
# Let's find the closing </button> for the import button.
closing_btn_idx = -1
for i in range(import_btn_line, len(lines)):
    if '</button>' in lines[i]:
        closing_btn_idx = i
        break

start_replace_idx = closing_btn_idx + 1
end_replace_idx = card_2_line

# Content to Insert:
# 1. Rest of Header (with NEW BUTTON)
# 2. Stats Container
# 3. Critical Equipment Alert
# 4. Start of Row for Cards
# 5. Card 1 (Pendientes)

restored_content = """            <a href="{{ url_for('panel_estados') }}" class="btn btn-info shadow-sm ms-2" title="Ir a Gestión de Equipos">
                <i class="fas fa-tasks me-2"></i> Gestión de Equipos
            </a>
        </div>
        <div class="subtitle">Vista Completa del Sistema - Última actualización: {{ stats_admin.ultima_actualizacion }}
        </div>
    </div>

    <!-- ESTADÍSTICAS GLOBALES -->
    <div class="stats-container">
        <div class="stat-card total">
            <div class="stat-icon">
                <i class="fas fa-laptop-medical" style="color: #8b5cf6;"></i>
            </div>
            <div class="stat-number">{{ stats_admin.total }}</div>
            <div class="stat-label">Total Equipos</div>
        </div>

        <div class="stat-card diagnostico">
            <div class="stat-icon">
                <i class="fas fa-cog fa-spin" style="color: var(--primary);"></i>
            </div>
            <div class="stat-number">{{ stats_admin.activos }}</div>
            <div class="stat-label">Equipos Activos</div>
        </div>

        <div class="stat-card pendiente">
            <div class="stat-icon">
                <i class="fas fa-exclamation-triangle" style="color: var(--warning);"></i>
            </div>
            <div class="stat-number">{{ stats_admin.atrasados }}</div>
            <div class="stat-label">Atrasados (+5 días)</div>
        </div>

        <div class="stat-card aprobado">
            <div class="stat-icon">
                <i class="fas fa-clock" style="color: var(--success);"></i>
            </div>
            <div class="stat-number">{{ stats_admin.tiempo_promedio }}</div>
            <div class="stat-label">Días Promedio</div>
        </div>
    </div>

    <!-- EQUIPOS CRÍTICOS -->
    {% if equipos_criticos %}
    <div class="alert bg-dark border border-danger text-light mb-4 shadow-sm">
        <h5><i class="fas fa-exclamation-circle"></i> Equipos Críticos (más de 7 días)</h5>
        <div class="table-responsive">
            <table class="table table-sm table-dark">
                <thead>
                    <tr>
                        <th>FR</th>
                        <th>Marca/Modelo</th>
                        <th>Estado</th>
                        <th>Días</th>
                        <th>Fecha Ingreso</th>
                    </tr>
                </thead>
                <tbody>
                    {% for eq in equipos_criticos %}
                    <tr>
                        <td><span class="badge bg-danger">{{ eq.fr or 'N/A' }}</span></td>
                        <td>{{ eq.marca }} {{ eq.modelo }}</td>
                        <td><span class="badge bg-secondary">{{ eq.estado }}</span></td>
                        <td><strong>{{ (now() - eq.fecha_ingreso).days }}</strong></td>
                        <td>{{ eq.fecha_ingreso.strftime('%d/%m/%Y') if eq.fecha_ingreso else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- VISTA ADMIN: TARJETAS APILADAS POR CATEGORIA -->
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

"""

# Apply the replacement
lines = lines[:start_replace_idx] + [restored_content] + lines[end_replace_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Restored Admin Dashboard sections.")
