import pandas as pd
import os
from datetime import datetime
from extensions import db
from models import Equipment

# PUBLIC LINK PROVIDED BY USER
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1P878SusAnFOkX9PZC5NlqVNyQ3qywkY1/export?format=xlsx"

def sync_excel_to_db(app, local_filename=None, force=False):
    """
    Reads from Google Drive Public Link (Priority) or Local File (Fallback).
    Populates SQLite/Postgres database.
    force: If True, ignores the 5-minute cooldown.
    """
    source_name = "Remote Google Sheet"
    df = None

    from models import GlobalSettings
    from datetime import timedelta

    with app.app_context():
        # 0. Check Cooldown (Anti-Duplication)
        if not force:
            setting = GlobalSettings.query.filter_by(key='last_sync').first()
            if setting:
                now = datetime.utcnow()
                # If synced less than 3 minutes ago, skip
                if setting.updated_at and (now - setting.updated_at) < timedelta(minutes=3):
                    print("Excel Sync: Skipped (Cooldown active). Data is fresh.")
                    return True

    # 1. Try Google Sheet URL
    import time
    
    # 1. Try Google Sheet URL
    try:
        # Cache Busting: Add generic unique param
        unique_url = f"{GOOGLE_SHEET_URL}&t={int(time.time())}"
        print(f"Excel Sync: Downloading workbook from {unique_url}...")
        
        # Load ALL sheets without header first to start scanning
        xls = pd.read_excel(unique_url, sheet_name=None, header=None, engine='openpyxl')
        
        df = None
        target_name = 'CONTROL DE EQUIPOS CABELAB'
        
        # Priority search: specific name first
        sheets_to_check = [target_name] + [k for k in xls.keys() if k != target_name]
        
        for name in sheets_to_check:
            if name not in xls: continue
            
            raw_df = xls[name]
            # Scan first 10 rows for Header Signature
            for i in range(min(10, len(raw_df))):
                # Convert row to checks
                row_vals = [str(x).upper().strip() for x in raw_df.iloc[i].tolist()]
                
                # Signature: must have MARCA and MODELO
                if 'MARCA' in row_vals and 'MODELO' in row_vals:
                    print(f"Excel Sync: FOUND HEADERS in sheet '{name}' at row {i}.")
                    
                    # Reload or Slice? Slicing is faster.
                    # Set header
                    raw_df.columns = raw_df.iloc[i] # Set header to this row
                    df = raw_df[i+1:].reset_index(drop=True) # Data is everything below
                    break
            
            if df is not None: 
                break
        
        if df is None:
            print("Excel Sync: CRITICAL - Could not find 'MARCA'/'MODELO' columns in any sheet.")
            return False

        print(f"Excel Sync: Loaded data. Shape: {df.shape}")

    except Exception as e:
        print(f"Excel Sync: Failed to read from Google Drive. Error: {str(e)}")
        
        # 2. Key Fallback: Local File
        if local_filename:
            file_path = os.path.join(app.root_path, local_filename)
            if os.path.exists(file_path):
                print(f"Excel Sync: Falling back to local file {local_filename}...")
                try:
                    df = pd.read_excel(file_path, header=1)
                    source_name = f"Local File ({local_filename})"
                except Exception as local_e:
                    print(f"Excel Sync: Failed to read local file ({local_e}).")

    if df is None:
        print("Excel Sync: No data source available. Aborting sync.")
        return False

    try:
        # Normalize columns: upper case + strip
        df.columns = [str(c).upper().strip() for c in df.columns]
        
        # MAPPING
        col_map = {
            'fr': ['FR', 'NUMERO FR', 'NRO FR', 'F.R.'],
            'marca': ['MARCA'],
            'modelo': ['MODELO'],
            'estado': ['ESTADO', 'UBICACION', 'SITUACION'],
            'condicion': ['CONDICION', 'ESTADO FISICO'],
            'encargado': ['ENCARGADO', 'TECNICO', 'ASIGNADO'],
            'fecha_ingreso': ['FECHA DE INGRESO', 'FECHA', 'INGRESO'],
            'observaciones': ['OBSERVACIONES DIAGNOSTICO', 'OBSERVACIONES', 'NOTA', 'COMENTARIOS', 'OBSERVACIONES DE MANTENIMIENTO'],
            'reporte_cliente': ['REPORTE DE CLIENTE', 'REPORTE', 'FALLA', 'PROBLEMA']
        }

        def get_val(row, field_candidates):
            for col in field_candidates:
                if col in row:
                    val = row[col]
                    return val if pd.notna(val) else None
            return None

        with app.app_context():
            # Wiping and reloading is the safest way to ensure exact sync with Sheet
            Equipment.query.delete()
            
            count = 0
            for index, row in df.iterrows():
                fr = get_val(row, col_map['fr'])
                marca = get_val(row, col_map['marca'])
                modelo = get_val(row, col_map['modelo'])
                estado = get_val(row, col_map['estado'])
                
                if not marca and not modelo: continue 

                if not estado: estado = 'Espera de Diagnostico'
                
                fecha = get_val(row, col_map['fecha_ingreso'])
                fecha_obj = datetime.now()
                if isinstance(fecha, datetime):
                    fecha_obj = fecha
                elif isinstance(fecha, str):
                    try:
                        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                    except:
                        pass

                eq = Equipment(
                    fr=str(fr) if fr else '',
                    marca=str(marca),
                    modelo=str(modelo),
                    estado=str(estado),
                    condicion=str(get_val(row, col_map['condicion']) or 'Regular'),
                    encargado=str(get_val(row, col_map['encargado']) or 'No asignado'),
                    observaciones=str(get_val(row, col_map['observaciones']) or ''),
                    reporte_cliente=str(get_val(row, col_map['reporte_cliente']) or 'Importado desde Excel'),
                    fecha_ingreso=fecha_obj
                )
                db.session.add(eq)
                count += 1
            
            db.session.commit()
            
            # Update Timestamp
            setting = GlobalSettings.query.filter_by(key='last_sync').first()
            if not setting:
                setting = GlobalSettings(key='last_sync')
                db.session.add(setting)
            setting.updated_at = datetime.utcnow()
            setting.value = "Success"
            db.session.commit()

            print(f"Excel Sync: Imported {count} records from {source_name}.")
            return True

    except Exception as e:
        print(f"Excel Sync Logic Error: {e}")
        return False

def sync_users_from_excel(app):
    """
    Reads users from the same Google Sheet if a 'USUARIOS' tab exists.
    Expected Columns: USUARIO, PASSWORD, ROL
    """
    from models import User, UserRoles
    
    try:
        print(f"User Sync: Checking for USUARIOS tab in {GOOGLE_SHEET_URL}...")
        # Read specifically the 'USUARIOS' sheet (or try to find it)
        # using header=0 because presumably user will put headers on row 1
        xls = pd.read_excel(GOOGLE_SHEET_URL, sheet_name=None, engine='openpyxl')
        
        # Find sheet case-insensitive
        user_sheet_name = next((s for s in xls.keys() if s.upper().strip() == 'USUARIOS'), None)
        
        if not user_sheet_name:
            print("User Sync: 'USUARIOS' tab not found in Excel. Skipping user sync.")
            return False
            
        df = xls[user_sheet_name]
        # Normalize columns
        df.columns = [str(c).upper().strip() for c in df.columns]
        
        print(f"User Sync: Found tab '{user_sheet_name}'. Columns: {df.columns.tolist()}")
        
        # Expected cols: USUARIO, PASSWORD, ROL
        if 'USUARIO' not in df.columns or 'PASSWORD' not in df.columns:
            print("User Sync: Missing required columns (USUARIO, PASSWORD).")
            return False

        count = 0
        with app.app_context():
            # Strategy: Upsert users. 
            # Note: In Vercel, DB is empty anyway, so we just insert.
            # But we must respect the hardcoded 'Venllas'/'admin' if we want to keep them as backups?
            # Actually, Excel should be the source of truth if it exists.
            
            for index, row in df.iterrows():
                username = row['USUARIO']
                password = row['PASSWORD']
                role_raw = str(row['ROL']).upper() if 'ROL' in df.columns and pd.notna(row['ROL']) else 'VISUALIZADOR'
                
                if pd.isna(username) or pd.isna(password): continue
                username = str(username).strip()
                password = str(password).strip()
                
                # Map Roles
                role = UserRoles.VISUALIZADOR
                is_admin_flag = False
                
                if 'ADMIN' in role_raw or 'GEREN' in role_raw:
                    role = UserRoles.ADMIN
                    is_admin_flag = True
                elif 'RECEPCION' in role_raw:
                    role = UserRoles.RECEPCION
                elif 'OPERACION' in role_raw:
                    role = UserRoles.OPERACIONES
                elif 'ALMACEN' in role_raw:
                    role = UserRoles.ALMACEN
                
                # Check exist
                existing = User.query.filter_by(username=username).first()
                if not existing:
                    u = User(username=username, role=role, is_admin=is_admin_flag, is_approved=True)
                    u.set_password(password)
                    db.session.add(u)
                    count += 1
                else:
                    # Optional: Update password/role if changed in Excel?
                    existing.role = role
                    existing.is_admin = is_admin_flag
                    existing.set_password(password) # Reset password to match Excel
            
            db.session.commit()
            print(f"User Sync: Synced {count} users from Excel.")
            return True

    except Exception as e:
        print(f"User Sync Error: {e}")
        return False
