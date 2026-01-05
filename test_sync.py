import pandas as pd
import requests

URL = "https://docs.google.com/spreadsheets/d/1P878SusAnFOkX9PZC5NlqVNyQ3qywkY1/export?format=xlsx"
SHEET_NAME = "CONTROL DE EQUIPOS CABELAB"

print(f"Testing download from: {URL}")
print(f"Target sheet: {SHEET_NAME}")

try:
    # 1. Test basic connectivity
    response = requests.get(URL)
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('Content-Type')}")
    print(f"Size: {len(response.content)} bytes")
    
    if response.status_code != 200:
        print("ERROR: Failed to download file.")
        exit(1)
    
    # 2. Test Pandas Read (simulating excel_sync.py)
    print("Attempting to read ALL sheets (header=None)...")
    xls = pd.read_excel(URL, sheet_name=None, header=None, engine='openpyxl')
    
    print("SUCCESS: Workbook loaded.")
    print("Sheet Names found:", list(xls.keys()))
    
    winner = None
    
    for sheet_name, df in xls.items():
        print(f"\n--- Scanning Sheet: {sheet_name} (Rows: {len(df)}) ---")
        
        # Scan first 20 rows for header keywords
        for i in range(min(20, len(df))):
            row_values = [str(x).upper().strip() for x in df.iloc[i].tolist()]
            
            # Check for signature columns
            if 'MARCA' in row_values and 'MODELO' in row_values:
                print(f">>> FOUND HEADERS at Row {i} (Index {i}) in '{sheet_name}'")
                print(f"    Values: {row_values}")
                winner = (sheet_name, i)
                break
        
        if winner: break

    if winner:
        print(f"\nCONCLUSION: The data is in sheet '{winner[0]}' starting at header row {winner[1]}.")
    else:
        print("\nCONCLUSION: Could NOT find 'MARCA'/'MODELO' headers in any sheet (scanned first 20 rows).")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
