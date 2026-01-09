
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. FIND BAD BLOCK
# Look for the first occurrence of "<!-- HISTORIAL ENTREGADOS (SHARED) -->"
# It should be around line 431.
start_idx = -1
for i, line in enumerate(lines):
    if "<!-- HISTORIAL ENTREGADOS (SHARED) -->" in line:
        start_idx = i
        break

if start_idx == -1:
    print("Could not find start of bad block.")
    exit(1)

# Find the end of this block.
# It ends just before the `{% else %}` of the `for` loop (line ~599).
# OR simpler: The block ends with `{% endif %}` followed by `<script>` close?
# My block ends with `{% endif %}` (line 598 in view).
# The NEXT line is `                                        {% else %}` (indent varying).

end_idx = -1
for i in range(start_idx, len(lines)):
    if "{% else %}" in lines[i]:
        # This is the for-else. The block ends at i-1.
        end_idx = i
        break

if end_idx == -1:
    print("Could not find end of bad block.")
    exit(1)

# Extract the block to check/save (we want to re-insert it).
# The block lines are lines[start_idx : end_idx]
bad_block = lines[start_idx:end_idx]

# 2. REMOVE BAD BLOCK
# Delete lines[start_idx : end_idx]
del lines[start_idx:end_idx]

# 3. FIND CORRECT INSERTION POINT
# We want to insert it in the Admin View.
# The Admin View ends at `{% else %}` (Switch to User View).
# This `{% else %}` was around line 614 (before deletion).
# Now it shifted up by (end_idx - start_idx).

# Let's search for "<!-- VISTA USUARIO - Mis Tareas -->"
# The insertion point is BEFORE the `{% else %}` that precedes this comment.
user_view_idx = -1
for i, line in enumerate(lines):
    if "<!-- VISTA USUARIO - Mis Tareas -->" in line:
        user_view_idx = i
        break

if user_view_idx == -1:
    print("Could not find User View marker.")
    exit(1)

# Backtrack to find {% else %}
insert_idx = -1
for i in range(user_view_idx, 0, -1):
    if "{% else %}" in lines[i]:
        insert_idx = i
        break

if insert_idx == -1:
    print("Could not find insertion point (else).")
    exit(1)

# Insert BEFORE `{% else %}`.
# But wait, we need to make sure we are AFTER the `</div>` of the row.
# The row closes just before `{% else %}`.
# So inserting before `{% else %}` is perfect.

# 4. RE-INSERT
# We insert `bad_block` at `insert_idx`.
# We should probably strip excessive indentation if needed, but HTML tolerates it.
lines[insert_idx:insert_idx] = bad_block

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Dashboard Fixed.")
