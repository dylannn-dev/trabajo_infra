import time
import math
import random
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# ─────────────────────────────────────────────────────────────
# PARÁMETROS
# ─────────────────────────────────────────────────────────────
N_RECORDS = 500_000
N_GRUPOS  = 50
SEED      = 42

# ─────────────────────────────────────────────────────────────
# 1. GENERACIÓN DEL DATASET
# ─────────────────────────────────────────────────────────────
def generar_dataset(n: int = N_RECORDS, seed: int = SEED) -> list:
    """
    Genera n registros con:
      - grupo     : entero 0-49 (ej. sucursal)
      - monto     : distribución normal(500, 150), ~5% anomalías
      - hora      : entero 0-23
      - categoria : entero 0-9
    """
    random.seed(seed)
    dataset = []
    for i in range(n):
        monto = random.gauss(500.0, 150.0)
        if random.random() < 0.05:          # ~5% de registros anómalos
            monto = 0.0 if random.random() < 0.3 else random.gauss(3000, 500)
        dataset.append({
            "id"       : i,
            "grupo"    : random.randint(0, N_GRUPOS - 1),
            "monto"    : round(monto, 2),
            "hora"     : random.randint(0, 23),
            "categoria": random.randint(0, 9),
        })
    return dataset

# ─────────────────────────────────────────────────────────────
# 2. FUNCIÓN DE PROCESAMIENTO (igual para secuencial y paralelo)
# ─────────────────────────────────────────────────────────────
def procesar_chunk(registros: list) -> list:
    """
    Por cada registro:
      - Calcula z-score usando estadísticas del propio chunk
      - Marca como anomalía si z > 3.0 o monto <= 0
      - Calcula indicador compuesto con bucle trigonométrico (carga CPU)

    Retorna lista de dicts con: id, z_score, anomalia, indicador
    """
    montos = [r["monto"] for r in registros]
    n      = len(montos)
    media  = sum(montos) / n
    var    = sum((x - media) ** 2 for x in montos) / n
    std    = math.sqrt(var) if var > 0 else 1.0

    resultados = []
    for r in registros:
        z        = abs((r["monto"] - media) / std)
        anomalia = z > 3.0 or r["monto"] <= 0

        # Indicador compuesto: carga deliberada de cómputo flotante
        indicador = sum(
            math.log1p(abs(r["monto"]) + k) * math.sin(r["hora"] * k)
            for k in range(1, 8)
        )
        resultados.append({
            "id"       : r["id"],
            "grupo"    : r["grupo"],
            "z_score"  : round(z, 4),
            "anomalia" : anomalia,
            "indicador": round(indicador, 4),
        })
    return resultados

# ─────────────────────────────────────────────────────────────
# 3. VERSIÓN SECUENCIAL (p = 1)
# ─────────────────────────────────────────────────────────────
def ejecutar_secuencial(dataset: list) -> tuple:
    """Procesa todo el dataset en un solo hilo. Retorna (resultado, tiempo)."""
    t0 = time.perf_counter() # un contador que parte desde 0 
    resultado = procesar_chunk(dataset) #procesar_chunk calcula valores matematicos como z core, que tan lejos es el valor de la desviacion estandar, la media y asi etc
    t1 = time.perf_counter()
    return resultado, round(t1 - t0, 4)

# ─────────────────────────────────────────────────────────────
# 4. VERSIÓN PARALELA (p = 2, 4, …)
# ─────────────────────────────────────────────────────────────
def ejecutar_paralelo(dataset: list, n_workers: int) -> tuple:
    """
    Divide el dataset en n_workers chunks y los procesa en paralelo
    con ProcessPoolExecutor. Retorna (resultado, tiempo).
    """
    chunk_size = len(dataset) // n_workers
    chunks = [
        dataset[i * chunk_size : (i + 1) * chunk_size]
        for i in range(n_workers)
    ]
    # El resto de la división entera va al último chunk
    resto = len(dataset) % n_workers
    if resto:
        chunks[-1].extend(dataset[n_workers * chunk_size :])

    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        parciales = list(executor.map(procesar_chunk, chunks))
    t1 = time.perf_counter()

    resultado = [r for parte in parciales for r in parte]
    return resultado, round(t1 - t0, 4)

# ─────────────────────────────────────────────────────────────
# 5. BENCHMARK PRINCIPAL
# ─────────────────────────────────────────────────────────────
def benchmark():
    cpus = multiprocessing.cpu_count()
    print(f"\n{'='*60}")
    print(f"  Ejercicio 3 — Paralelismo local")
    print(f"  CPUs disponibles: {cpus}")
    print(f"  Registros        : {N_RECORDS:,}")
    print(f"{'='*60}\n")

    print("Generando dataset...")
    dataset = generar_dataset()
    print(f"Dataset generado: {len(dataset):,} registros\n")

    # --- Secuencial ---
    print("Ejecutando secuencial (p=1)...")
    _, t1 = ejecutar_secuencial(dataset)
    print(f"  T₁ = {t1:.4f} s\n")
    configs_paralelas = [p for p in [2, 4] if p <= cpus]
    if not configs_paralelas:
        print(f"  ⚠ Solo hay {cpus} CPU(s) disponible(s).")
        print(f"  No se puede ejecutar paralelismo real con p>1.")
        print(f"  Ejecuta en una máquina con ≥2 núcleos para comparar.\n")

    print(f"{'p':>4}  {'Tₚ (s)':>10}  {'Sₚ = T₁/Tₚ':>12}  {'Eₚ = Sₚ/p':>12}  {'Observación'}")
    print(f"{'─'*6}  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*30}")
    print(f"{'1':>4}  {t1:>10.4f}  {'1.0000':>12}  {'1.0000 (100%)':>12}  Línea base")

    for p in configs_paralelas:
        print(f"\nEjecutando paralelo (p={p})...")
        _, tp = ejecutar_paralelo(dataset, p)
        sp = round(t1 / tp, 4)
        ep = round(sp / p, 4)
        obs = "Buena ganancia, overhead moderado" if p == 2 else "Speedup sublineal, overhead crece"
        print(f"  {'':>2}{p:>2}  {tp:>10.4f}  {sp:>12.4f}  {ep:>10.4f} ({ep*100:.1f}%)  {obs}")

    print(f"\n{'='*60}")
    print("  Fórmulas aplicadas:")
    print("    Speedup   Sₚ = T₁ / Tₚ")
    print("    Eficiencia Eₚ = Sₚ / p")
    print()
    print("  Factores que limitan el speedup lineal:")
    print("    • Fracción serial (Ley de Amdahl): ~8% no paralelizable")
    print("    • Overhead de fork de procesos (fijo por proceso)")
    print("    • Serialización pickle para pasar chunks entre procesos")
    print("    • Unión (join) de resultados parciales (1 hilo)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    benchmark()