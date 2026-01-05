import pandas as pd
import requests

URL = "https://docs.google.com/spreadsheets/d/1P878SusAnFOkX9PZC5NlqVNyQ3qywkY1/export?format=xlsx"

print(f"Testing download from: {URL}")

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
    print("Attempting to read ALL sheets...")
    # sheet_name=None reads all sheets into a dict
    xls = pd.read_excel(URL, sheet_name=None, engine='openpyxl')
    
    print("SUCCESS: Workbook loaded.")
    print("Sheet Names found:", list(xls.keys()))
    
    for sheet_name, df in xls.items():
        print(f"\n--- Sheet: {sheet_name} ---")
        print(f"Shape: {df.shape}")
        print("Columns:", df.columns.tolist())

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
