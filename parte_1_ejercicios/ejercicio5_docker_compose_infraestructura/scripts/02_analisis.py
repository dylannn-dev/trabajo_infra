"""
scripts/02_analisis.py
======================
Ejecuta consultas y análisis sobre los datos cargados en PostgreSQL.
Demuestra:
  - Consultas SQL desde Python (Jupyter → PostgreSQL)
  - Transformaciones con pandas
  - Guardado de resultados en la BD (persistencia de análisis)
  - Generación de visualizaciones

Ejecución:
  %run scripts/02_analisis.py  (desde celda de Jupyter)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # Backend sin pantalla (dentro de contenedor)
import seaborn as sns
import json
from sqlalchemy import create_engine, text
from datetime import datetime

# ── CONEXIÓN ──────────────────────────────────────────────────
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "datasciencedb")
DB_USER = os.getenv("DB_USER", "dsuser")
DB_PASS = os.getenv("DB_PASSWORD", "dspassword")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
RUTA_SALIDA = "/home/jovyan/work/data"


# ── ANÁLISIS 1: Ventas por categoría ─────────────────────────
def analisis_por_categoria(engine) -> pd.DataFrame:
    """
    Consulta SQL directa: agrega ventas por categoría.
    El cálculo ocurre EN PostgreSQL (más eficiente que traer todo).
    """
    query = """
        SELECT
            categoria,
            COUNT(*)                            AS num_transacciones,
            SUM(cantidad)                       AS unidades_vendidas,
            ROUND(SUM(total)::numeric, 2)       AS ingresos_totales,
            ROUND(AVG(precio_unitario)::numeric, 2) AS precio_promedio
        FROM ciencia_datos.ventas
        GROUP BY categoria
        ORDER BY ingresos_totales DESC
    """
    df = pd.read_sql(query, engine)
    print("\n📊 Ventas por categoría:")
    print(df.to_string(index=False))
    return df


# ── ANÁLISIS 2: Tendencia mensual ────────────────────────────
def analisis_tendencia_mensual(engine) -> pd.DataFrame:
    """
    Usa funciones de fecha de PostgreSQL (DATE_TRUNC).
    Muestra cómo SQL puede hacer trabajo pesado antes de pandas.
    """
    query = """
        SELECT
            DATE_TRUNC('month', fecha)::date    AS mes,
            COUNT(*)                            AS transacciones,
            ROUND(SUM(total)::numeric, 2)       AS ingresos
        FROM ciencia_datos.ventas
        GROUP BY mes
        ORDER BY mes
    """
    df = pd.read_sql(query, engine)
    df["mes"] = pd.to_datetime(df["mes"])
    print("\n📈 Tendencia mensual:")
    print(df.to_string(index=False))
    return df


# ── ANÁLISIS 3: Top vendedores por región ────────────────────
def analisis_top_vendedores(engine) -> pd.DataFrame:
    """
    Usa window functions de PostgreSQL (RANK OVER PARTITION).
    Demuestra capacidades analíticas avanzadas del motor SQL.
    """
    query = """
        WITH ventas_vendedor AS (
            SELECT
                region,
                vendedor,
                ROUND(SUM(total)::numeric, 2) AS total_ventas,
                RANK() OVER (
                    PARTITION BY region
                    ORDER BY SUM(total) DESC
                ) AS ranking_en_region
            FROM ciencia_datos.ventas
            GROUP BY region, vendedor
        )
        SELECT * FROM ventas_vendedor
        WHERE ranking_en_region = 1
        ORDER BY total_ventas DESC
    """
    df = pd.read_sql(query, engine)
    print("\n🏆 Top vendedor por región:")
    print(df.to_string(index=False))
    return df


# ── GENERAR VISUALIZACIONES ───────────────────────────────────
def generar_graficos(df_cat: pd.DataFrame, df_mensual: pd.DataFrame) -> None:
    """
    Crea gráficos y los guarda como archivos PNG en el volumen.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Análisis de Ventas - Mini Infraestructura Docker",
                 fontsize=14, fontweight="bold")

    # Gráfico 1: Ingresos por categoría
    sns.barplot(
        data=df_cat,
        x="ingresos_totales",
        y="categoria",
        ax=axes[0],
        palette="viridis"
    )
    axes[0].set_title("Ingresos por Categoría")
    axes[0].set_xlabel("Ingresos Totales ($)")
    axes[0].set_ylabel("")

    # Gráfico 2: Tendencia mensual
    axes[1].plot(df_mensual["mes"], df_mensual["ingresos"],
                 marker="o", linewidth=2, color="#2ecc71")
    axes[1].fill_between(df_mensual["mes"], df_mensual["ingresos"],
                         alpha=0.3, color="#2ecc71")
    axes[1].set_title("Ingresos Mensuales")
    axes[1].set_xlabel("Mes")
    axes[1].set_ylabel("Ingresos ($)")
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    ruta = f"{RUTA_SALIDA}/analisis_ventas.png"
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    print(f"\n🖼️  Gráfico guardado en: {ruta}")
    plt.close()


# ── GUARDAR RESULTADOS EN BD ──────────────────────────────────
def guardar_resultados(nombre: str, descripcion: str,
                       df_resultado: pd.DataFrame, engine) -> None:
    """
    Persiste los resultados del análisis en la tabla resultados_analisis.
    ESTO ES CLAVE: demuestra que Jupyter escribe DE VUELTA a PostgreSQL.
    Los resultados sobreviven aunque el contenedor Jupyter se reinicie.
    """
    resultado_json = df_resultado.to_dict(orient="records")

    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO ciencia_datos.resultados_analisis
                    (nombre_analisis, descripcion, resultado_json)
                VALUES (:nombre, :desc, :resultado::jsonb)
            """),
            {
                "nombre":    nombre,
                "desc":      descripcion,
                "resultado": json.dumps(resultado_json, default=str),
            }
        )
        conn.commit()
    print(f"  💾 Resultado '{nombre}' guardado en BD")


# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  ANÁLISIS DE VENTAS - Ejercicio 5 Docker Compose")
    print("=" * 55)

    # Ejecutar análisis
    df_cat      = analisis_por_categoria(engine)
    df_mensual  = analisis_tendencia_mensual(engine)
    df_top      = analisis_top_vendedores(engine)

    # Generar gráficos
    print("\n🎨 Generando visualizaciones...")
    generar_graficos(df_cat, df_mensual)

    # Persistir resultados en PostgreSQL
    print("\n💾 Guardando resultados en PostgreSQL...")
    guardar_resultados(
        "ventas_por_categoria",
        "Ingresos y transacciones agrupadas por categoría de producto",
        df_cat, engine
    )
    guardar_resultados(
        "tendencia_mensual",
        "Evolución mensual de ingresos durante 2024",
        df_mensual, engine
    )

    # Verificar persistencia
    with engine.connect() as conn:
        n = conn.execute(
            text("SELECT COUNT(*) FROM ciencia_datos.resultados_analisis")
        ).scalar()
        print(f"\n✅ {n} análisis almacenados en ciencia_datos.resultados_analisis")

    print("\n🎉 Análisis completado. Los resultados persisten en PostgreSQL.")
