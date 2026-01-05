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
    # Note: excel_sync.py uses header=1.
    print("Attempting pd.read_excel...")
    df = pd.read_excel(URL, header=1, engine='openpyxl')
    
    print("SUCCESS: DataFrame loaded.")
    print(f"Shape: {df.shape}")
    print("Columns found:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
