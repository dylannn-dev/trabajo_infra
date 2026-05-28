-- =============================================================
-- init-db/01_crear_tablas.sql
-- Se ejecuta AUTOMÁTICAMENTE la primera vez que arranca PostgreSQL
-- (solo cuando el volumen postgres_data está vacío)
-- =============================================================

-- Creamos un esquema separado para organizar mejor los objetos
CREATE SCHEMA IF NOT EXISTS ciencia_datos;

-- Tabla principal: dataset de ventas de ejemplo
-- Representa datos que un científico de datos analizaría
CREATE TABLE IF NOT EXISTS ciencia_datos.ventas (
    id              SERIAL PRIMARY KEY,
    fecha           DATE NOT NULL,
    producto        VARCHAR(100) NOT NULL,
    categoria       VARCHAR(50) NOT NULL,
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10, 2) NOT NULL,
    total           NUMERIC(10, 2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    region          VARCHAR(50) NOT NULL,
    vendedor        VARCHAR(100),
    creado_en       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para guardar resultados de análisis (evidencia de persistencia)
CREATE TABLE IF NOT EXISTS ciencia_datos.resultados_analisis (
    id              SERIAL PRIMARY KEY,
    nombre_analisis VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    resultado_json  JSONB,         -- Almacena resultados como JSON flexible
    ejecutado_en    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_ventas_fecha     ON ciencia_datos.ventas(fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_categoria ON ciencia_datos.ventas(categoria);
CREATE INDEX IF NOT EXISTS idx_ventas_region    ON ciencia_datos.ventas(region);

-- Comentarios en la BD (buena práctica de documentación)
COMMENT ON TABLE ciencia_datos.ventas IS 
    'Dataset principal de ventas para análisis. Cargado por el script Python.';
COMMENT ON TABLE ciencia_datos.resultados_analisis IS 
    'Resultados de análisis ejecutados desde Jupyter, persisten en BD.';

-- Mensaje de confirmación en los logs de PostgreSQL
DO $$ BEGIN
    RAISE NOTICE '✅ Tablas creadas correctamente en esquema ciencia_datos';
END $$;
