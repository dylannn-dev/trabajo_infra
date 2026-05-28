import time        
import os          
import platform    
import psutil      
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

def get_memory_usage():
    """Devuelve cuánta RAM (en bytes) está usando este programa ahora mismo"""
    process = psutil.Process(os.getpid()) # Busca nuestro programa ejecutándose en el sistema
    return process.memory_info().rss      # Extrae la cantidad exacta de memoria usada

def cpu_intensive(n=10**7):
    start = time.time()                     # Inicia cronómetro
    x = np.random.rand(n)                   # Crea 10 millones de números al azar
    y = np.sin(x) * np.cos(x)               # ¡Trabajo pesado para la CPU! (Seno * Coseno a todos)
    end = time.time()                       # Detiene cronómetro
    return end - start, y.nbytes            # Devuelve los segundos que tardó y el tamaño en RAM

def memory_sequential(n=10**7):
    arr = np.arange(n)                      # Crea una lista ordenada de números (0, 1, 2, 3...)
    start = time.time()                     # Inicia cronómetro
    s = 0
    for i in arr:                           # Lee los números uno por uno en orden 
        s += i
    end = time.time()                       # Detiene cronómetro
    return end - start, arr.nbytes          # Devuelve tiempo y tamaño

def memory_random(n=10**7):
    arr = np.arange(n)                      # Crea la lista ordenada
    idx = np.random.randint(0, n, size=n)   # Crea 10 millones de posiciones (índices) completamente al azar
    start = time.time()                     # Inicia cronómetro
    s = 0
    for i in idx:                           # Salta caóticamente por la memoria buscando los números (más lento)
        s += arr[i]
    end = time.time()                       # Detiene cronómetro
    return end - start, arr.nbytes          # Devuelve tiempo y tamaño

def disk_io(filename="testfile.bin", n=10**7):
    data = os.urandom(n)                    # Genera 10 millones de bytes al azar (datos basura)
    start = time.time()                     # Inicia cronómetro
    with open(filename, "wb") as f:         # Abre un archivo en el disco duro para escribir
        f.write(data)                       # Guarda los bytes físicamente en el disco
    with open(filename, "rb") as f:         # Vuelve a abrir el archivo, ahora para leer
        _ = f.read()                        # Lee todo el archivo desde el disco hacia la memoria
    end = time.time()                       # Detiene cronómetro
    return end - start, len(data)           # Devuelve tiempo y tamaño

def run_benchmarks(reps=3):
    print(f"--- Iniciando Benchmark en: {platform.system()} {platform.release()} ---") 
    print(f"Procesador: {platform.processor()}") # Imprime tu modelo exacto de procesador
    
    results = [] # Una lista vacía donde iremos anotando los puntajes
    
    for i in range(reps): # Repite todo el proceso 3 veces para sacar un promedio justo
        
        # --- Prueba 1: CPU ---
        mem_before = get_memory_usage()         # Revisa la RAM antes de empezar
        t, size = cpu_intensive()               # Ejecuta la prueba
        mem_after = get_memory_usage()          # Revisa la RAM al terminar
        # Anota: Nombre, tiempo, tamaño, throughput (velocidad) y diferencia de RAM
        results.append(("CPU", t, size, size/t, abs(mem_after - mem_before)))

        # --- Prueba 2: Memoria en orden ---
        mem_before = get_memory_usage()
        t, size = memory_sequential()
        mem_after = get_memory_usage()
        results.append(("Memoria Secuencial", t, size, size/t, abs(mem_after - mem_before)))

        # --- Prueba 3: Memoria con saltos ---
        mem_before = get_memory_usage()
        t, size = memory_random()
        mem_after = get_memory_usage()
        results.append(("Memoria Aleatoria", t, size, size/t, abs(mem_after - mem_before)))

        # --- Prueba 4: Disco duro ---
        mem_before = get_memory_usage()
        t, size = disk_io()
        mem_after = get_memory_usage()
        results.append(("Disco IO", t, size, size/t, abs(mem_after - mem_before)))
        
    # Transforma nuestras anotaciones en una tabla 
    return pd.DataFrame(results, columns=["Escenario","Tiempo","Tamaño","Throughput","Memoria_Usada_Bytes"])

# ==========================================
# EJECUCIÓN FINAL Y GRÁFICOS
# ==========================================

df = run_benchmarks()                               # Arranca todas las pruebas y guarda la tabla en 'df'
df.to_csv("resultados_benchmark.csv", index=False)  # Exporta la tabla a un archivo CSV (Excel)
print("\nResultados guardados en 'resultados_benchmark.csv'")

# Dibujar Gráfico de Tiempo
plt.figure(figsize=(10,5))                          
df.groupby("Escenario")["Tiempo"].mean().plot(kind="bar", color='skyblue') 
plt.ylabel("Tiempo promedio (s)")                   
plt.title("Tiempo por experimento")                 
plt.xticks(rotation=45)                             
plt.tight_layout()                                  
plt.show()                                          

# Dibujar Gráfico de Throughput
plt.figure(figsize=(10,5))                          
df.groupby("Escenario")["Throughput"].mean().plot(kind="bar", color='lightgreen') 
plt.ylabel("Throughput (bytes/s)")
plt.title("Throughput por experimento")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()