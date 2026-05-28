import os
import duckdb
import pandas as pd

def generar_metricas_gold():
    print("\n=== INICIO PIPELINE: ZONA GOLD ===")
    
    # ==========================================
    # 1. DEFINICIÓN DE RUTAS (Raíz del Proyecto)
    # ==========================================
    # Sube un directorio (..) desde la carpeta 'scripts' para apuntar a la raíz
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Ruta de lectura (Silver Parquet)
    archivo_silver = os.path.join(BASE_DIR, "data", "silver", "sensores_limpios.parquet")
    # DuckDB funciona mejor con barras normales (/) en Windows
    ruta_duckdb = os.path.join(BASE_DIR, "data", "silver", "*.parquet").replace("\\", "/")
    
    # Rutas de escritura (Gold y Metrics)
    directorio_gold = os.path.join(BASE_DIR, "data", "gold")
    directorio_metrics = os.path.join(BASE_DIR, "metrics")
    
    if not os.path.exists(archivo_silver):
        print(f"[ERROR] No se encontró el archivo en:\n{archivo_silver}")
        print("Ejecuta plata.py primero.")
        return

    # Asegurar que las carpetas de salida existan
    os.makedirs(directorio_gold, exist_ok=True)
    os.makedirs(directorio_metrics, exist_ok=True)
    
    # Conexión a DuckDB en memoria
    con = duckdb.connect(database=':memory:')
    print("--- Ejecutando Consultas Analíticas con DuckDB ---\n")

    # ==========================================
    # CONSULTA 1: Perfil Climático -> CSV
    # ==========================================
    query_clima = f"""
        SELECT 
            ubicacion,
            ROUND(AVG(temperatura), 2) AS temp_promedio_c,
            ROUND(AVG(humedad), 2) AS humedad_promedio_pct,
            MIN(temperatura) AS temp_minima,
            MAX(temperatura) AS temp_maxima
        FROM read_parquet('{ruta_duckdb}')
        GROUP BY ubicacion
        ORDER BY temp_promedio_c DESC
    """
    df_clima = con.execute(query_clima).df()
    print("1. Perfil Climático por Habitación:")
    print(df_clima.to_string(index=False))
    
    ruta_csv_clima = os.path.join(directorio_metrics, "reporte_perfil_climatico.csv")
    df_clima.to_csv(ruta_csv_clima, index=False)
    print(f"  [→] CSV guardado en: {ruta_csv_clima}\n")

    # ==========================================
    # CONSULTA 2: Eficiencia HVAC -> JSON
    # ==========================================
    query_energia = f"""
        SELECT 
            ubicacion,
            estado_hvac,
            ROUND(AVG(light_lux), 2) AS luz_lux_promedio,
            ROUND(AVG(temperatura), 2) AS temp_promedio
        FROM read_parquet('{ruta_duckdb}')
        WHERE estado_hvac IS NOT NULL
        GROUP BY ubicacion, estado_hvac
        ORDER BY ubicacion, estado_hvac
    """
    try:
        df_energia = con.execute(query_energia).df()
        print("2. Impacto del HVAC en Temperatura e Iluminación:")
        print(df_energia.to_string(index=False))
        
        ruta_json_energia = os.path.join(directorio_metrics, "reporte_eficiencia_hvac.json")
        df_energia.to_json(ruta_json_energia, orient="records", indent=4, force_ascii=False)
        print(f"  [→] JSON guardado en: {ruta_json_energia}\n")
    except duckdb.BinderException:
        print("2. (Consulta omitida: Faltan columnas en el archivo Silver)\n")

    # ==========================================
    # CONSULTA 3: Calidad del Aire -> CSV
    # ==========================================
    query_calidad_aire = f"""
        SELECT 
            ubicacion,
            occupancy AS hay_personas,
            ROUND(AVG(co2_ppm), 2) AS co2_promedio,
            MAX(co2_ppm) AS co2_pico
        FROM read_parquet('{ruta_duckdb}')
        WHERE co2_ppm IS NOT NULL
        GROUP BY ubicacion, occupancy
        ORDER BY ubicacion, hay_personas
    """
    try:
        df_calidad_aire = con.execute(query_calidad_aire).df()
        print("3. Calidad del Aire (CO2) según Ocupación:")
        print(df_calidad_aire.to_string(index=False))
        
        ruta_csv_aire = os.path.join(directorio_metrics, "reporte_calidad_aire.csv")
        df_calidad_aire.to_csv(ruta_csv_aire, index=False)
        print(f"  [→] CSV guardado en: {ruta_csv_aire}\n")
    except duckdb.BinderException:
        print("3. (Consulta omitida: Faltan columnas en el archivo Silver)\n")

    # ==========================================
    # GUARDADO GOLD: Parquet Particionado
    # ==========================================
    print("--- Generando Tabla Analítica Final ---")
    query_tabla_final = f"""
        SELECT 
            ubicacion,
            CAST(timestamp AS VARCHAR)[:13] AS ventana_hora, 
            ROUND(AVG(temperatura), 2) AS temperatura_media,
            ROUND(AVG(humedad), 2) AS humedad_media,
            COUNT(*) AS cantidad_lecturas
        FROM read_parquet('{ruta_duckdb}')
        GROUP BY ubicacion, ventana_hora
    """
    try:
        df_tabla_final = con.execute(query_tabla_final).df()
        ruta_gold_particionada = os.path.join(directorio_gold, "metricas_por_habitacion")
        
        df_tabla_final.to_parquet(
            ruta_gold_particionada, 
            engine='pyarrow', 
            partition_cols=['ubicacion'], 
            index=False
        )
        print(f"[✓] Tabla analítica particionada guardada en:\n  -> {ruta_gold_particionada}")
    except Exception as e:
        print(f"\n[ERROR] Falló la creación de la tabla particionada: {e}")

if __name__ == "__main__":
    generar_metricas_gold()