
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    original_content = f.read()

# 1. Update Critical Equipment Alert Style
# Old: <div class="alert alert-warning mb-4">
# New: <div class="alert bg-dark border border-danger text-light mb-4 shadow-sm">
new_content = original_content.replace(
    '<div class="alert alert-warning mb-4">',
    '<div class="alert bg-dark border border-danger text-light mb-4 shadow-sm">'
)

# 2. Add Button to Header
# Look for the Import Button to place the new one next to it.
import_btn_str = """
            <button class="btn btn-primary shadow-sm ms-2" data-bs-toggle="modal" data-bs-target="#importInformesModal">
                <i class="fas fa-file-csv me-2"></i> Importar Informes
            </button>
"""
# Note: indentation might vary, so let's try a safer replace using a unique part.
# Or just replace the block if we are strict.
# Let's try to find a unique string anchor.
anchor = '<i class="fas fa-file-csv me-2"></i> Importar Informes\n            </button>'

# We want to add this BEFORE the closing div of that flex container? 
# Actually user said "alado de importar informes" (next to).
# The current HTML has:
# <div class="d-flex ...">
#    ...
#    <a href ... Backup >
#    <button ... Importar >
# </div>

# So I can append it after the Import button.
new_button_html = """
            <a href="{{ url_for('panel_estados') }}" class="btn btn-info shadow-sm ms-2" title="Ir a Gestión de Equipos">
                <i class="fas fa-tasks me-2"></i> Gestión de Equipos
            </a>"""

# Let's try to replace the closing `</button>` of the import modal with `</button>` + new_html.
# But `</button>` is common.
# I'll use the unique target attributes of the import button to identify it.
import_btn_tag = 'data-bs-target="#importInformesModal">'
if import_btn_tag in new_content:
    # Find the closing tag for this button
    # It usually follows closely.
    # Let's search for the substring and append the button after the closing tag of this specific button.
    # Simple string replace of the button's closing sequence might be risky if formatted unexpectedly.
    # However, I know the content from view_file:
    # <button class="btn btn-primary shadow-sm ms-2" data-bs-toggle="modal" data-bs-target="#importInformesModal">
    #      <i class="fas fa-file-csv me-2"></i> Importar Informes
    # </button>
    
    target_str = '<i class="fas fa-file-csv me-2"></i> Importar Informes\n            </button>'
    replacement_str = target_str + new_button_html
    new_content = new_content.replace(target_str, replacement_str)
else:
    print("Warning: Import button not found exactly as expected.")


# 3. Remove the redirection button from 'Accion' column
# Target: <a href="{{ url_for('panel_estados') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>
# This was added in my previous script (update_admin_dashboard.py) in the stacked cards.
btn_to_remove = '<a href="{{ url_for(\'panel_estados\') }}" class="btn btn-sm btn-outline-light ms-1"><i class="fas fa-external-link-alt"></i></a>'

# Replace with empty string
new_content = new_content.replace(btn_to_remove, '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Dashboard UI updated successfully.")
