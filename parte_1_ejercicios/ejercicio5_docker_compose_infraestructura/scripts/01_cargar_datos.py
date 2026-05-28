"""
scripts/01_cargar_datos.py
==========================
Genera un dataset sintético de ventas y lo carga en PostgreSQL.

¿Por qué este script existe?
- Simula el flujo real: tienes un CSV externo y lo cargas a la BD
- Demuestra la comunicación contenedor Jupyter → contenedor PostgreSQL
- El nombre del host es 'postgres' (nombre del servicio en docker-compose)
  NO es 'localhost' — esto es clave en infraestructuras con contenedores

Ejecución:
  Desde Jupyter terminal: python scripts/01_cargar_datos.py
  O desde celda de notebook: %run scripts/01_cargar_datos.py
"""

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import date, timedelta
import random
import json

# ── CONFIGURACIÓN DE CONEXIÓN ─────────────────────────────────
# Las variables de entorno vienen del docker-compose.yml
# Esto hace el script portable (no hay credenciales hardcodeadas)
DB_HOST = os.getenv("DB_HOST", "postgres")       # Nombre del servicio Docker
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "datasciencedb")
DB_USER = os.getenv("DB_USER", "dsuser")
DB_PASS = os.getenv("DB_PASSWORD", "dspassword")

# URL de conexión SQLAlchemy
# Formato: postgresql://usuario:contraseña@host:puerto/basededatos
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔌 Conectando a PostgreSQL en {DB_HOST}:{DB_PORT}/{DB_NAME}...")

# ── GENERAR DATASET SINTÉTICO ─────────────────────────────────
def generar_dataset(n_registros: int = 500) -> pd.DataFrame:
    """
    Genera un dataset de ventas ficticias para análisis.
    En un caso real, aquí leerías: pd.read_csv('datos.csv')
    """
    random.seed(42)  # Semilla para reproducibilidad
    np.random.seed(42)

    productos = {
        "Laptop Pro":      ("Tecnología", 1200.00),
        "Mouse Inalámbrico": ("Periféricos", 29.99),
        "Teclado Mecánico": ("Periféricos", 89.99),
        "Monitor 4K":      ("Tecnología", 450.00),
        "Webcam HD":       ("Periféricos", 79.99),
        "SSD 1TB":         ("Almacenamiento", 110.00),
        "RAM 16GB":        ("Almacenamiento", 65.00),
        "Auriculares BT":  ("Audio", 149.99),
        "Hub USB-C":       ("Periféricos", 45.00),
        "Tablet 10\"":     ("Tecnología", 320.00),
    }

    regiones   = ["Norte", "Sur", "Centro", "Oriente", "Occidente"]
    vendedores = ["Ana García", "Luis Martínez", "Carmen López",
                  "Pedro Soto", "María Fernández"]

    fecha_inicio = date(2024, 1, 1)
    fechas = [
        fecha_inicio + timedelta(days=random.randint(0, 364))
        for _ in range(n_registros)
    ]

    nombres_productos = random.choices(list(productos.keys()), k=n_registros)

    data = {
        "fecha":           fechas,
        "producto":        nombres_productos,
        "categoria":       [productos[p][0] for p in nombres_productos],
        "cantidad":        np.random.randint(1, 20, n_registros),
        "precio_unitario": [
            round(productos[p][1] * np.random.uniform(0.9, 1.1), 2)
            for p in nombres_productos
        ],
        "region":   random.choices(regiones, k=n_registros),
        "vendedor": random.choices(vendedores, k=n_registros),
    }

    df = pd.DataFrame(data)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


# ── CARGA A POSTGRESQL ────────────────────────────────────────
def cargar_a_postgres(df: pd.DataFrame, engine) -> None:
    """
    Inserta el DataFrame en la tabla ciencia_datos.ventas.
    if_exists='append': agrega filas sin borrar las existentes
    """
    df.to_sql(
        name="ventas",
        con=engine,
        schema="ciencia_datos",
        if_exists="append",   # 'replace' borraría la tabla primero
        index=False,          # No guardar el índice de pandas como columna
        method="multi",       # Inserta múltiples filas en un solo INSERT (más rápido)
        chunksize=100,        # Lotes de 100 filas
    )
    print(f"  ✅ {len(df)} registros insertados en ciencia_datos.ventas")


# ── GUARDAR DATASET LOCALMENTE ────────────────────────────────
def guardar_csv(df: pd.DataFrame) -> None:
    """
    Guarda el dataset como CSV en el volumen compartido.
    Evidencia de que los datos existen antes de ir a la BD.
    """
    ruta = "/home/jovyan/work/data/ventas_generadas.csv"
    df.to_csv(ruta, index=False)
    print(f"  💾 CSV guardado en: {ruta}")


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        # 1. Crear motor de conexión SQLAlchemy
        engine = create_engine(DATABASE_URL, echo=False)

        # 2. Probar conexión
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            print(f"  ✅ Conexión exitosa → {version[:50]}...")

        # 3. Generar dataset
        print("\n📊 Generando dataset de ventas...")
        df = generar_dataset(500)
        print(f"  Shape: {df.shape} | Columnas: {list(df.columns)}")
        print(df.head(3).to_string())

        # 4. Guardar CSV localmente (evidencia)
        print("\n💾 Guardando CSV local...")
        guardar_csv(df)

        # 5. Cargar a PostgreSQL
        print("\n📤 Cargando datos a PostgreSQL...")
        cargar_a_postgres(df, engine)

        # 6. Verificar carga
        with engine.connect() as conn:
            total = conn.execute(
                text("SELECT COUNT(*) FROM ciencia_datos.ventas")
            ).scalar()
            print(f"\n✅ Verificación: {total} registros en la tabla")

        print("\n🎉 Carga completada exitosamente")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
