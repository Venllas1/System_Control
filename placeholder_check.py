
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We want to insert this BEFORE the end of the .main-container or just before {% endblock %}
# Let's find the closing `</div>` of the main container.
# It usually starts at line 6 or 7.
# A safe place is just before the scripts at the bottom or before {% endblock %}

# But `dashboard.html` structure:
# ...
# <!-- 5. TERMINADOS -->
# ...
# </div> (Closing .row g-4 mb-4 of Stacked Cards)
# </div> (Closing .main-container)

# We want to insert AFTER the Stacked Cards Row, but INSIDE main-container.

# Let's find the "<!-- 5. TERMINADOS / LISTOS -->" marker.
terminados_idx = -1
for i, line in enumerate(lines):
    if "<!-- 5. TERMINADOS / LISTOS -->" in line:
        terminados_idx = i
        break

if terminados_idx == -1:
    print("Could not find Terminados section.")
    exit(1)

# Find the closing specific div for that col-12.
# It's tricky to count divs.
# Instead, let's look for where the Stacked Row ends.
# It ends before `{% else %}` (line ~312 in current file view for User View check) OR
# if it's the Admin View, it ends before `{% endif %}` (line ~1121? No, lines shown were cut).

# Safer approach:
# The `dashboard.html` has `{% if is_admin_view %}` block and `{% else %}` (User view) block.
# We want this table for BOTH Admin and User (except Almacen).
# BUT the layout inside Admin vs User is different.
# Admin has stacked cards.
# User has "Mis Tareas" header, then Stats, then "Categorized Lists".

# WAIT. User request: "añadir a todos los roles (excepto almacen) una tabla al final (tanto en tareas como en gestion de equipos)".
# "en tareas" = User View (dashboard).
# "gestion de equipos" = Admin View (dashboard) AND Panel de Estados.

# So I need to add it in TWO places in `dashboard.html`?
# Or just once if I can put it outside the if/else?
# No, `is_admin_view` splits the whole file structure.
# Admin View ends around line 311 (in previous view) before `{% else %}`.
# User View ends before `{% endblock %}`.

# Strategy:
# 1. Insert into Admin View (At the bottom of stacked cards).
# 2. Insert into User View (At the bottom).

# Let's verify file content around the split.
# I will read the file again to be sure of line numbers/context.
pass
