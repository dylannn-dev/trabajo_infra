import pandas as pd
import os
import glob
from datetime import datetime

# ==========================================
# 1. REGLAS DE NEGOCIO Y ESTANDARIZACIÓN
# ==========================================
SCHEMA_MAPPING = {
    'id_sensor': ['id', 'sensor', 'device_id', 'mac_address', 'id_dispositivo'],
    'timestamp': ['time', 'fecha', 'fecha_hora', 'ts', 'datetime', 'date', 'timestamp'],
    'temperatura': ['temp', 'tmp', 't', 'temperatura_c', 'temp_celsius', 'temp_c'],
    'humedad': ['hum', 'humidity', 'h', 'humedad_rel', 'humidity_pct'],
    'ubicacion': ['location', 'loc', 'zona', 'area', 'sector', 'room'],
    'co2_ppm': ['co2', 'co2_ppm'],
    'light_lux': ['light', 'light_lux', 'iluminacion'],
    'occupancy': ['occupancy', 'ocupacion', 'personas'],
    'estado_hvac': ['hvac', 'hvac_status', 'estado', 'climatizacion']
}

# ==========================================
# 2. DEFINICIÓN DE RUTAS (Raíz del Proyecto)
# ==========================================
# Sube un directorio (..) desde la carpeta 'scripts' para apuntar a la raíz
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def estandarizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza los nombres de las columnas basándose en el diccionario."""
    renombramiento = {}
    for col in df.columns:
        col_limpia = str(col).strip().lower()
        for nombre_oficial, lista_alias in SCHEMA_MAPPING.items():
            if col_limpia in lista_alias or col_limpia == nombre_oficial:
                renombramiento[col] = nombre_oficial
                break 
    return df.rename(columns=renombramiento)

def procesar_archivos_bronze() -> pd.DataFrame:
    """Lee todos los archivos de la zona Bronze y los estandariza."""
    directorio_bronze = os.path.join(BASE_DIR, "data", "bronze")
    
    archivos_csv = glob.glob(os.path.join(directorio_bronze, "*.csv"))
    archivos_json = glob.glob(os.path.join(directorio_bronze, "*.json*"))
    
    dataframes = []
    
    for ruta in archivos_csv:
        print(f"  [Leyendo Bronze CSV]: {os.path.basename(ruta)}")
        try:
            df = pd.read_csv(ruta, comment='#')
        except pd.errors.ParserError:
            df = pd.read_csv(ruta, comment='#', on_bad_lines='skip', engine='python')
        dataframes.append(estandarizar_columnas(df))
        
    for ruta in archivos_json:
        print(f"  [Leyendo Bronze JSON]: {os.path.basename(ruta)}")
        try:
            df = pd.read_json(ruta, lines=True) 
        except ValueError:
            df = pd.read_json(ruta) 
        dataframes.append(estandarizar_columnas(df))
        
    if not dataframes:
        raise ValueError(f"No se encontraron datos en: {directorio_bronze}")
        
    return pd.concat(dataframes, ignore_index=True)

def aplicar_calidad(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica las reglas de calidad para la zona Silver."""
    print("  Aplicando reglas de calidad (Silver)...")
    filas_iniciales = len(df)
    
    # Regla 1: Eliminar registros sin ID de sensor
    if 'id_sensor' in df.columns:
        df = df.dropna(subset=['id_sensor'])
        
    # Regla 2: Eliminar filas exactamente duplicadas
    df = df.drop_duplicates()
    
    # Regla 3: Validar rango lógico de temperatura
    if 'temperatura' in df.columns:
        df['temperatura'] = pd.to_numeric(df['temperatura'], errors='coerce')
        df = df[(df['temperatura'] >= -20.0) & (df['temperatura'] <= 60.0)]
        
    filas_finales = len(df)
    print(f"  -> Filas descartadas por mala calidad: {filas_iniciales - filas_finales}")
    return df

def transformar_a_silver():
    print("=== PIPELINE: ZONA SILVER ===")
    try:
        df_unificado = procesar_archivos_bronze()
        df_limpio = aplicar_calidad(df_unificado)
        
        if df_limpio.empty:
            print("\n  [!] Advertencia: Después de la limpieza, no quedaron datos válidos.")
            return

        directorio_silver = os.path.join(BASE_DIR, "data", "silver")
        os.makedirs(directorio_silver, exist_ok=True)
        
        ruta_salida = os.path.join(directorio_silver, "sensores_limpios.parquet")
        
        # Guardar como archivo Parquet
        df_limpio.to_parquet(ruta_salida, index=False)
        
        print(f"Transformación Silver completada exitosamente.")
        print(f"Datos guardados en:\n  -> {ruta_salida}")
        print(f"Filas resultantes: {len(df_limpio)}")
        
    except Exception as e:
        print(f"Error crítico en la capa Silver: {e}")

if __name__ == "__main__":
    transformar_a_silver()