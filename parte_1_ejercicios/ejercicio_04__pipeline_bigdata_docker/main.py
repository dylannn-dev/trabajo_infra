import sys
from scripts.bronze import ingestar_a_bronze
from scripts.plata import transformar_a_silver
from scripts.oro import generar_metricas_gold

def ejecutar_pipeline_completo():
    print("=========================================")
    print("🚀 INICIANDO PIPELINE DE DATOS EN DOCKER")
    print("=========================================\n")
    
    # 1. Ejecutamos la ingesta (Zona Bronze)
    print("--- FASE 1: ADQUISICIÓN DE DATOS ---")
    exito_bronze = ingestar_a_bronze()
    
    # Si la ingesta falla (no encuentra el archivo), detenemos el pipeline
    if not exito_bronze:
        print("\n❌ Pipeline detenido: No se pudo completar la ingesta de datos.")
        sys.exit(1) 
        
    print("\n")
    
    # 2. Ejecutamos la limpieza y validación (Zona Silver)
    print("--- FASE 2: CALIDAD Y ESTANDARIZACIÓN ---")
    transformar_a_silver()
    
    print("\n")
    
    # 3. Ejecutamos la analítica y exportación (Zona Gold)
    print("--- FASE 3: MÉTRICAS Y ANALÍTICA ---")
    generar_metricas_gold()
    
    print("\n=========================================")
    print("✅ PIPELINE FINALIZADO CON ÉXITO")
    print("=========================================")

if __name__ == "__main__":
    ejecutar_pipeline_completo()