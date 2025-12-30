import pandas as pd
import os
from datetime import datetime
from extensions import db
from models import Equipment

# PUBLIC LINK PROVIDED BY USER
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1P878SusAnFOkX9PZC5NlqVNyQ3qywkY1/export?format=xlsx"

def sync_excel_to_db(app, local_filename=None):
    """
    Reads from Google Drive Public Link (Priority) or Local File (Fallback).
    Populates SQLite database.
    """
    source_name = "Remote Google Sheet"
    df = None

    # 1. Try Google Sheet URL
    try:
        print(f"Excel Sync: Attempting to read from {GOOGLE_SHEET_URL}...")
        # Header is on Row 2 (Index 1) per previous debug
        df = pd.read_excel(GOOGLE_SHEET_URL, header=1)
        print("Excel Sync: Successfully downloaded from Google Drive.")
    except Exception as e:
        print(f"Excel Sync: Failed to read from Google Drive ({e}).")
        
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
            print(f"Excel Sync: Imported {count} records from {source_name}.")
            return True

    except Exception as e:
        print(f"Excel Sync Logic Error: {e}")
        return False
