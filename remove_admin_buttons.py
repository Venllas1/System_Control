
import re

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex to find the anchor tag for panel_estados:
# <a href="{{ url_for('panel_estados') }}" ... </i></a>
# It spans multiple lines.
pattern = r'<a\s+href="{{ url_for\(\'panel_estados\'\)\ }}"[\s\S]*?</i></a>'

# Verify if we find matches
matches = re.findall(pattern, content)
print(f"Found {len(matches)} buttons to remove.")

# Remove them
new_content = re.sub(pattern, '', content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Buttons removed successfully.")
