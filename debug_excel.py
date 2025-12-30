import pandas as pd
import os

filename = 'Copia de CONTROL DE EQUIPOS CABELAB(Recuperado automáticamente).xlsx'
try:
    df = pd.read_excel(filename, header=1)
    
    # Filter for rows where FR or MARCA is not null
    valid_rows = df[df['FR'].notna() | df['MARCA'].notna()]
    
    print("\n--- FIRST 5 VALID ROWS ---")
    if not valid_rows.empty:
        print(valid_rows[['FR', 'MARCA', 'MODELO', 'ESTADO']].head(10).to_string())
        
        # Check unique statuses
        print("\n--- UNIQUE STATUSES FOUND ---")
        print(valid_rows['ESTADO'].unique())
    else:
        print("NO VALID DATA FOUND (All FR/MARCA are NaN)")

except Exception as e:
    print(e)
