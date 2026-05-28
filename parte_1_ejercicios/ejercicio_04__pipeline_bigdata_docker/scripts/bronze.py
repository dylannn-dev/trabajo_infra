import os
import shutil

# ==========================================
# 1. DEFINICIÓN DE RUTAS (Raíz del Proyecto)
# ==========================================
# Sube un directorio (..) desde la carpeta 'scripts' para apuntar a la raíz (ejercicio_04)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def ingestar_a_bronze():
    print("=== INICIO PIPELINE: ZONA BRONZE ===")
    
    # 1. Identificar el archivo de origen en la raíz del proyecto
    # Le agregué el .csv al final del nombre que me pasaste
    nombre_archivo = "IoTSyn_Smart_Home_20260418_213223.csv"
    ruta_origen = os.path.join(BASE_DIR, nombre_archivo)
    
    # 2. Definir y crear la carpeta de destino (Zona Bronze)
    directorio_bronze = os.path.join(BASE_DIR, "data", "bronze")
    os.makedirs(directorio_bronze, exist_ok=True)
    
    # Validar que el archivo realmente exista antes de intentar copiarlo
    if not os.path.exists(ruta_origen):
        print(f"[-] ERROR: No se encontró el archivo de datos crudos en:\n    {ruta_origen}")
        print("    Asegúrate de que el CSV esté pegado en la misma carpeta que main.py")
        return False
        
    ruta_destino = os.path.join(directorio_bronze, nombre_archivo)
    
    # 3. Mover/Copiar los datos
    try:
        # shutil.copy2 preserva los metadatos originales del archivo
        shutil.copy2(ruta_origen, ruta_destino)
        print(f"  [+] Archivo '{nombre_archivo}' ingestado exitosamente en:")
        print(f"      {directorio_bronze}")
    except Exception as e:
        print(f"  [-] Error crítico al copiar {nombre_archivo}: {e}")
        return False
            
    print("Ingesta Bronze completada. Archivos listos para la capa Silver.\n")
    return True

if __name__ == "__main__":
    ingestar_a_bronze()