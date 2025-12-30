/**
 * CABELAB 2025 - Dashboard JavaScript
 * Funcionalidades: DataTables, búsqueda en tiempo real, exportación, notificaciones
 */

// ============================================
// CONFIGURACIÓN GLOBAL
// ============================================
const CABELAB = {
    autoRefreshInterval: null,
    autoRefreshEnabled: false,
    refreshIntervalMinutes: 5,
    
    // Estado de la aplicación
    state: {
        currentTab: 'resumen',
        lastUpdate: null,
        dataTablesInstances: []
    }
};

// ============================================
// INICIALIZACIÓN AL CARGAR PÁGINA
// ============================================
$(document).ready(function() {
    console.log('🚀 CABELAB Dashboard iniciado');
    
    // Inicializar componentes
    initDataTables();
    initEventListeners();
    initAnimations();
    startAutoRefresh();
    
    // Mostrar notificación de bienvenida
    showToast('Sistema iniciado correctamente', 'success');
});

// ============================================
// DATATABLES - INICIALIZACIÓN
// ============================================
function initDataTables() {
    console.log('📊 Inicializando DataTables...');
    
    // Configuración común para todas las tablas
    const commonConfig = {
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"]],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json',
            search: "🔍 Buscar:",
            lengthMenu: "Mostrar _MENU_ registros",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "No hay registros disponibles",
            infoFiltered: "(filtrado de _MAX_ registros totales)",
            zeroRecords: "No se encontraron coincidencias",
            emptyTable: "No hay datos disponibles en la tabla",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            }
        },
        responsive: true,
        autoWidth: false,
        order: [[0, 'asc']],
        dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rtip',
        drawCallback: function() {
            // Animación al cambiar página
            $(this).closest('.table-container').css('opacity', '0.5');
            setTimeout(() => {
                $(this).closest('.table-container').css('opacity', '1');
            }, 100);
        }
    };
    
    // Inicializar cada tabla con configuración específica
    $('table').each(function(index) {
        const tableId = $(this).attr('id');
        
        try {
            const table = $(this).DataTable(commonConfig);
            CABELAB.state.dataTablesInstances.push(table);
            console.log(`✅ Tabla ${tableId || index} inicializada`);
        } catch (error) {
            console.error(`❌ Error al inicializar tabla ${tableId || index}:`, error);
        }
    });
}

// ============================================
// EVENT LISTENERS
// ============================================
function initEventListeners() {
    console.log('🎯 Configurando event listeners...');
    
    // Botón de refresh
    $('#refresh-btn, .refresh-btn').on('click', function(e) {
        e.preventDefault();
        refreshData();
    });
    
    // Cambio de pestañas
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        const target = $(e.target).data('bs-target');
        CABELAB.state.currentTab = target.replace('#', '');
        console.log(`📑 Pestaña activa: ${CABELAB.state.currentTab}`);
        
        // Recalcular columnas de DataTables
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
    });
    
    // Búsqueda en tiempo real (si hay input de búsqueda personalizado)
    $('#global-search').on('keyup debounce', function() {
        const searchTerm = $(this).val();
        performGlobalSearch(searchTerm);
    });
    
    // Botones de exportación
    $('.export-btn').on('click', function() {
        const format = $(this).data('format');
        const estado = $(this).data('estado') || 'all';
        exportData(format, estado);
    });
    
    // Toggle auto-refresh
    $('#toggle-auto-refresh').on('change', function() {
        CABELAB.autoRefreshEnabled = $(this).is(':checked');
        if (CABELAB.autoRefreshEnabled) {
            startAutoRefresh();
            showToast('Auto-actualización activada', 'info');
        } else {
            stopAutoRefresh();
            showToast('Auto-actualización desactivada', 'info');
        }
    });
}

// ============================================
// ANIMACIONES
// ============================================
function initAnimations() {
    console.log('✨ Inicializando animaciones...');
    
    // Animación de entrada para las cards
    $('.stat-card').each(function(i) {
        $(this).css({
            'animation': `fadeInUp 0.5s ease-in-out ${i * 0.1}s both`
        });
    });
    
    // Animación de contador para números
    animateStatNumbers();
}

function animateStatNumbers() {
    $('.stat-number').each(function() {
        const $this = $(this);
        const finalValue = parseInt($this.text());
        
        if (isNaN(finalValue)) return;
        
        $({ value: 0 }).animate({ value: finalValue }, {
            duration: 1500,
            easing: 'swing',
            step: function() {
                $this.text(Math.floor(this.value));
            },
            complete: function() {
                $this.text(finalValue);
            }
        });
    });
}

// ============================================
// REFRESH DE DATOS
// ============================================
function refreshData() {
    console.log('🔄 Refrescando datos...');
    
    const $refreshIcon = $('.refresh-btn i');
    $refreshIcon.addClass('loading');
    
    // Deshabilitar botón temporalmente
    $('.refresh-btn').prop('disabled', true);
    
    fetch('/api/refresh')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('✅ Datos actualizados:', data);
                
                // Actualizar estadísticas en tiempo real
                updateStats(data.stats);
                
                // Mostrar notificación
                showToast(`Datos actualizados - ${data.stats.total} equipos totales`, 'success');
                
                // Recargar página después de 1 segundo
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                throw new Error(data.error || 'Error desconocido');
            }
        })
        .catch(error => {
            console.error('❌ Error al refrescar:', error);
            showToast(`Error al actualizar: ${error.message}`, 'danger');
        })
        .finally(() => {
            $refreshIcon.removeClass('loading');
            $('.refresh-btn').prop('disabled', false);
        });
}

// ============================================
// ACTUALIZAR ESTADÍSTICAS
// ============================================
function updateStats(stats) {
    console.log('📈 Actualizando estadísticas...', stats);
    
    const statMapping = [
        { selector: '.stat-card.diagnostico .stat-number', value: stats.diagnostico },
        { selector: '.stat-card.aprobado .stat-number', value: stats.aprobado },
        { selector: '.stat-card.pendiente .stat-number', value: stats.pendiente },
        { selector: '.stat-card.servicio .stat-number', value: stats.diagnostico_servicio },
        { selector: '.stat-card.total .stat-number', value: stats.total }
    ];
    
    statMapping.forEach(({ selector, value }) => {
        const $element = $(selector);
        const currentValue = parseInt($element.text()) || 0;
        animateValue($element, currentValue, value, 800);
    });
    
    // Actualizar timestamp
    if (stats.ultima_actualizacion) {
        $('.footer').html(`
            <i class="fas fa-sync-alt"></i>
            <strong>Última actualización:</strong> ${stats.ultima_actualizacion}
        `);
    }
}

function animateValue($element, start, end, duration) {
    if (start === end) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        $element.text(Math.round(current));
    }, 16);
}

// ============================================
// BÚSQUEDA GLOBAL
// ============================================
function performGlobalSearch(query) {
    console.log(`🔍 Búsqueda global: "${query}"`);
    
    if (!query || query.length < 2) {
        // Si no hay query, resetear todas las tablas
        CABELAB.state.dataTablesInstances.forEach(table => {
            table.search('').draw();
        });
        return;
    }
    
    // Aplicar búsqueda a todas las tablas
    CABELAB.state.dataTablesInstances.forEach(table => {
        table.search(query).draw();
    });
}

// ============================================
// EXPORTACIÓN DE DATOS
// ============================================
function exportData(format, estado) {
    console.log(`📥 Exportando datos: formato=${format}, estado=${estado}`);
    
    showToast(`Preparando exportación en formato ${format.toUpperCase()}...`, 'info');
    
    const url = `/api/export/${format}?estado=${estado}`;
    
    // Crear enlace de descarga temporal
    const link = document.createElement('a');
    link.href = url;
    link.download = `cabelab_export_${estado}_${new Date().getTime()}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
        showToast(`Archivo ${format.toUpperCase()} descargado`, 'success');
    }, 1000);
}

// ============================================
// AUTO-REFRESH
// ============================================
function startAutoRefresh() {
    if (CABELAB.autoRefreshInterval) {
        clearInterval(CABELAB.autoRefreshInterval);
    }
    
    if (CABELAB.autoRefreshEnabled) {
        const intervalMs = CABELAB.refreshIntervalMinutes * 60 * 1000;
        console.log(`⏰ Auto-refresh activado: cada ${CABELAB.refreshIntervalMinutes} minutos`);
        
        CABELAB.autoRefreshInterval = setInterval(() => {
            console.log('⏰ Auto-refresh ejecutado');
            refreshData();
        }, intervalMs);
    }
}

function stopAutoRefresh() {
    if (CABELAB.autoRefreshInterval) {
        clearInterval(CABELAB.autoRefreshInterval);
        CABELAB.autoRefreshInterval = null;
        console.log('⏰ Auto-refresh desactivado');
    }
}

// ============================================
// SISTEMA DE NOTIFICACIONES (TOASTS)
// ============================================
function showToast(message, type = 'info', duration = 3000) {
    const iconMap = {
        success: 'check-circle',
        danger: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    
    const icon = iconMap[type] || 'info-circle';
    
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0 shadow-lg" role="alert" style="min-width: 300px;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const $container = $('#toast-container');
    if ($container.length === 0) {
        $('body').append('<div id="toast-container" class="position-fixed top-0 end-0 p-3" style="z-index: 9999;"></div>');
    }
    
    const $toast = $(toastHtml);
    $('#toast-container').append($toast);
    
    const toast = new bootstrap.Toast($toast[0], { delay: duration });
    toast.show();
    
    $toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// ============================================
// UTILIDADES
// ============================================

// Debounce para optimizar eventos
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Formatear fecha
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

// Copiar texto al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Texto copiado al portapapeles', 'success');
    }).catch(err => {
        console.error('Error al copiar:', err);
        showToast('Error al copiar texto', 'danger');
    });
}

// Mostrar loader
function showLoader(message = 'Cargando...') {
    return `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="text-muted mt-3 fw-bold">${message}</p>
        </div>
    `;
}

// ============================================
// CONSOLA DE DEBUG
// ============================================
window.CABELAB_DEBUG = {
    getState: () => CABELAB.state,
    getTables: () => CABELAB.state.dataTablesInstances,
    refreshNow: () => refreshData(),
    showTestToast: () => showToast('Test de notificación', 'info'),
    exportCSV: () => exportData('csv', 'all'),
    version: '2.0.0'
};

console.log('💡 Debug: window.CABELAB_DEBUG disponible');
console.log('📝 Ejemplo: CABELAB_DEBUG.getState()');