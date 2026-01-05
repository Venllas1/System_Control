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
    
    # 2. Read ONLY the specific sheet
    print(f"\nAttempting to read sheet: {SHEET_NAME}...")
    df = pd.read_excel(URL, sheet_name=SHEET_NAME, engine='openpyxl')
    
    print("SUCCESS: Sheet loaded.")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Show first few rows
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Verify MARCA column exists
    if 'MARCA' in df.columns or any('MARCA' in str(col).upper() for col in df.columns):
        print("\n✅ MARCA column found!")
    else:
        print("\n⚠️ WARNING: MARCA column not found in expected location")
        print("Available columns:", list(df.columns))
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")