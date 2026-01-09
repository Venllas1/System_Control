
import os

file_path = r'c:\Users\User\Documents\Virtual Machines\Pizarra Virtual\templates\panel_estados.html'

html_block = """
        <!-- CARD: HISTORIAL ENTREGADOS (PAGINATED) -->
        <div class="col-12 mt-4" id="cardEntregados">
            <div class="card bg-dark border-secondary shadow-sm h-100">
                <div class="card-header border-secondary d-flex justify-content-between align-items-center">
                    <div class="text-white fw-bold"><i class="fas fa-history me-2"></i> HISTORIAL DE ENTREGADOS</div>
                    <input type="text" id="searchEntregadosGrouped" class="form-control form-control-sm bg-dark text-light border-secondary" placeholder="Buscar..." style="width: 150px;">
                </div>
                <div class="card-body p-0 table-responsive">
                    <table class="table table-dark table-hover mb-0 align-middle">
                        <thead>
                            <tr class="text-secondary text-xs text-uppercase">
                                <th class="ps-4">Equipo</th>
                                <th>Estado</th>
                                <th>Encargado</th>
                                <th>Fecha</th>
                                <th>Tiempo</th>
                                <th class="text-end pe-4">Acción</th>
                            </tr>
                        </thead>
                        <tbody id="tableEntregadosGrouped">
                            <!-- JS Rendered -->
                        </tbody>
                    </table>
                </div>
                <div class="card-footer border-secondary d-flex justify-content-between align-items-center py-2">
                    <small class="text-muted" id="infoEntregadosGrouped">0-0/0</small>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-secondary" id="btnPrevEntregadosGrouped" disabled><i class="fas fa-chevron-left"></i></button>
                        <button class="btn btn-outline-secondary" id="btnNextEntregadosGrouped" disabled><i class="fas fa-chevron-right"></i></button>
                    </div>
                </div>
            </div>
        </div>
"""

js_block = """
            // LOGIC FOR ENTREGADOS PAGINATION (GROUPED VIEW)
            const cardEntregados = document.getElementById('cardEntregados');
            
            if (isAlmacenRole) {
                if(cardEntregados) cardEntregados.classList.add('d-none');
            } else {
                if(cardEntregados) cardEntregados.classList.remove('d-none');
                
                // Render Logic
                const tEntregados = document.getElementById('tableEntregadosGrouped');
                const sEntregados = document.getElementById('searchEntregadosGrouped');
                const btnPrev = document.getElementById('btnPrevEntregadosGrouped');
                const btnNext = document.getElementById('btnNextEntregadosGrouped');
                const infoEnt = document.getElementById('infoEntregadosGrouped');
                
                let entPage = 1;
                const entLimit = 5;
                let entData = equipments.filter(i => (i.estado||'').toLowerCase().includes('entregado'));
                
                function renderEntregadosSpecial() {
                    const term = normalize(sEntregados ? sEntregados.value : '');
                    const filtered = entData.filter(item => 
                        normalize(item.fr).includes(term) ||
                        normalize(item.marca).includes(term) ||
                        normalize(item.modelo).includes(term) ||
                        normalize(item.cliente).includes(term)
                    );
                    
                    const totalPages = Math.ceil(filtered.length / entLimit) || 1;
                    if (entPage > totalPages) entPage = 1;
                    
                    const start = (entPage - 1) * entLimit;
                    const end = start + entLimit;
                    const pageData = filtered.slice(start, end);
                    
                    if (tEntregados) {
                        tEntregados.innerHTML = pageData.length ? pageData.map(i => createRow(i, true)).join('') 
                            : '<tr><td colspan="6" class="text-center text-muted">Sin equipos entregados</td></tr>';
                    }
                    
                    if(infoEnt) infoEnt.innerText = `${entPage}/${totalPages}`;
                    if(btnPrev) btnPrev.disabled = (entPage === 1);
                    if(btnNext) btnNext.disabled = (entPage === totalPages);
                }
                
                if (sEntregados) {
                    sEntregados.addEventListener('input', () => { entPage = 1; renderEntregadosSpecial(); });
                }
                
                if (btnPrev) btnPrev.onclick = () => { if(entPage > 1) { entPage--; renderEntregadosSpecial(); } };
                if (btnNext) btnNext.onclick = () => { 
                    const term = normalize(sEntregados ? sEntregados.value : '');
                    const filtered = entData.filter(item => normalize(item.fr).includes(term) || normalize(item.marca).includes(term));
                    const totalPages = Math.ceil(filtered.length / entLimit); 
                    if(entPage < totalPages) { entPage++; renderEntregadosSpecial(); } 
                };
                
                // Initial call
                renderEntregadosSpecial();
            }
"""

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Insert HTML
# Find "<!-- FIN GROUPED VIEW -->" or the end of the cards container row.
# In `panel_estados.html`, the Grouped View is:
# {% else %} (of visualizador check)
# <div class="container-fluid ...">
#    <div class="row g-4">
#       ... Cards ...
#    </div>
# </div>
#
# I need to insert `html_block` inside the `.row g-4`.
# I'll look for `id="cardRepServ"` and insert after its closing div.
# But `cardRepServ` is specific to Almacen?
# Rec/Ops have `cardAprobadosOp`.
# Let's find the closing `</div>` of the `.row`.
# It's usually a `</div>` followed by `{% endif %}` or `<script>`.
#
# Best marker: The `renderGrouped` function in JS is further down.
# Let's verify markers in file.

# Previous view showed `id="cardRepServ"` (line ~782 in JS ref).
# HTML definition must be earlier.
# I will search for the lines that define `id="tableAprobadosOp"`.
# The HTML card closing `</div>` follows that.
# Then I insert my new card inside the row.

row_end_idx = -1
found_aprobados = False

for i, line in enumerate(lines):
    if 'id="tableAprobadosOp"' in line:
        found_aprobados = True
    
    if found_aprobados and "</div>" in line:
        # We need to skip a few divs to exit the card, but stay in row.
        # This is risky doing blindly.
        pass

# Alternative:
# Just append it to the end of the `NON-VISUALIZADOR` HTML block.
# The HTML block ends at `{% endif %}`? No, the `if is_visualizador` wraps the whole body content almost.
# Let's look for `<script>` tag. The body content usually ends before that.
# I will look for `<script>` and insert BEFORE it? No, that's outside the container.
#
# Let's look for `<!-- FIN CONTAINER -->` if it exists.
#
# Let's use `createRow` function call in previous Step 561.
# It seems `lines 772` is `} else { // UNIFIED VIEW LOGIC`.
# This is JS.
#
# The HTML is in the first half of the file (lines 300-400?). I need to find the HTML section.
# I'll rely on finding `id="cardAprobadosOp"` in the file (HTML side).

html_insert_idx = -1
for i, line in enumerate(lines):
    if 'id="cardAprobadosOp"' in line:
        # Found the start of the card.
        # I want to go to the end of this card.
        # Card usually ends with `</div></div></div>` (Card, Col, etc?)
        # Let's find the next card or the end of the row.
        # Next card might be `cardRepDiag`?
        pass

# Since I can't interactively scroll, I'll use a safer anchor.
# "<!-- CONTENT FOR NON-VISUALIZADOR -->" ??
#
# I will insert the HTML block by replacing a known distinctive closing tag of the last card, if I can find it.
# Or I insert it immediately BEFORE `<!-- JAVASCRIPT LOGIC -->` if that exists.
#
# Actually, I'll use `multi_replace` logic or `write_to_file` with search.
# But `write_to_file` is overwriting.
#
# I will perform a search for `id="cardAprobadosOp"` HTML block end.
# It likely ends before `{% endif %}` of some sort or `</div>` of row.
#
# Let's use a very specific string to anchor: `</tbody>` of `tableAprobadosOp`.
# Then find the closing tags `</table> </div> </div> </div> </div>`.
# Then insert.

# JS Insert:
# Find `renderGrouped(equipments);`
# Insert `js_block` AFTER it.
# This works.

# Finding HTML insert point is the tricky part.
# Let's scan for `id="tableAprobadosOp"`.
table_apro_idx = -1
for i, line in enumerate(lines):
    if 'id="tableAprobadosOp"' in line:
        table_apro_idx = i
        break

if table_apro_idx != -1:
    # Scan forward for 5 closing </div>s?
    # Or just scan until `<!--` (next comment) or `{%`?
    # Usually: </tbody> </table> </div> </div> </div> </div>
    # Let's insert it 20 lines after `tableAprobadosOp`? Risky.
    # Let's look for the next distinct element.
    # `cardRepDiag` logic is for Almacen.
    # `cardAprobadosOp` is for Rec/Ops.
    # They are Siblings in the same row?
    # If so, I can insert after `cardRepServ` (Almacen last card).
    # Does `cardRepServ` exist?
    pass

# Search for `id="cardRepServ"`.
card_rep_serv_idx = -1
for i, line in enumerate(lines):
    if 'id="cardRepServ"' in line:
        card_rep_serv_idx = i

if card_rep_serv_idx != -1:
    # This is likely the LAST card in the row (for Almacen).
    # I should insert AFTER this card.
    # Scan for `</tbody>` of `tableRepServ`.
    # Then scan for `</div>`s.
    pass

# Anchor on `tableRepServ`.
table_rep_serv_idx = -1
for i, line in enumerate(lines):
    if 'id="tableRepServ"' in line:
        table_rep_serv_idx = i

final_html_idx = -1
if table_rep_serv_idx != -1:
    # Look for the closing divs.
    # Let's assume 15 lines down is safe to insert BEFORE the next big thing.
    # The next big thing is `</div>` (row) or `<script>`.
    # Let's search for the next `<script>` tag after `tableRepServ`.
    # And insert BEFORE the closing `</div>` that precedes it.
    
    for i in range(table_rep_serv_idx, len(lines)):
        if "<script>" in lines[i]:
            final_html_idx = i - 2 # Approximate
            break

# JS Insert Point
js_insert_point = -1
for i, line in enumerate(lines):
    if "renderGrouped(equipments);" in line:
        js_insert_point = i + 1
        break

if final_html_idx != -1 and js_insert_point != -1:
    # Insert HTML
    lines.insert(final_html_idx, html_block)
    
    # Recalculate JS insert point (shifted by html_block length)
    # html_block is multi-line string, but insert adds it as 1 item? 
    # NO. `lines` is list of strings. `insert` adds 1 string.
    # So index shifts by 1.
    if js_insert_point >= final_html_idx:
        js_insert_point += 1
        
    lines.insert(js_insert_point, js_block)
else:
    print("Could not find insertion points.")
    exit(1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
    
print("Panel Updated.")
