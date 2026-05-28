# Ejercicio 5 — Mini Infraestructura Docker Compose para Ciencia de Datos
**INFB6074 - Infraestructura para Ciencia de Datos | UTM**

---

## Arquitectura de servicios

```
┌─────────────────────────────────────────────────────────────┐
│                    Red: ds_network (bridge)                  │
│                                                             │
│  ┌─────────────┐    SQL     ┌──────────────┐               │
│  │   jupyter   │ ─────────► │   postgres   │               │
│  │  :8888      │            │   :5432      │               │
│  └─────────────┘            └──────┬───────┘               │
│                                    │                        │
│  ┌─────────────┐            ┌──────▼───────┐               │
│  │   pgadmin   │ ─────────► │   postgres   │               │
│  │  :5050      │            │  (mismo svc) │               │
│  └─────────────┘            └──────────────┘               │
└─────────────────────────────────────────────────────────────┘

Volúmenes:
  postgres_data  → /var/lib/postgresql/data  (datos de la BD)
  notebooks_data → /home/jovyan/work         (notebooks)
  pgadmin_data   → /var/lib/pgadmin          (config pgAdmin)
```

---

## Servicios, puertos y variables de entorno

| Servicio   | Imagen              | Puerto Host | Puerto Contenedor | Descripción              |
|------------|---------------------|-------------|-------------------|--------------------------|
| `postgres` | postgres:15-alpine  | 5432        | 5432              | Motor de base de datos   |
| `jupyter`  | (build local)       | 8888        | 8888              | Entorno análisis Python  |
| `pgadmin`  | dpage/pgadmin4      | 5050        | 80                | GUI para PostgreSQL      |

### Variables de entorno relevantes

| Variable            | Servicio   | Valor por defecto     | Propósito                    |
|--------------------|------------|-----------------------|------------------------------|
| POSTGRES_DB         | postgres   | datasciencedb         | Nombre de la base de datos   |
| POSTGRES_USER       | postgres   | dsuser                | Usuario de PostgreSQL        |
| POSTGRES_PASSWORD   | postgres   | dspassword            | Contraseña de PostgreSQL     |
| JUPYTER_TOKEN       | jupyter    | datascience123        | Token de acceso a Jupyter    |
| DB_HOST             | jupyter    | postgres              | Hostname interno (red Docker)|
| PGADMIN_DEFAULT_EMAIL | pgadmin  | admin@datascience.local | Login pgAdmin              |

---

## Volúmenes y persistencia

| Volumen         | Montado en                        | Propósito                           |
|-----------------|-----------------------------------|-------------------------------------|
| `postgres_data` | `/var/lib/postgresql/data`        | Datos de PostgreSQL (persisten)     |
| `notebooks_data`| `/home/jovyan/work`               | Notebooks de Jupyter (persisten)    |
| `pgadmin_data`  | `/var/lib/pgadmin`                | Configuración de pgAdmin            |
| `./notebooks`   | `/home/jovyan/work/notebooks`     | Carpeta local sincronizada          |
| `./data`        | `/home/jovyan/work/data`          | Dataset CSV y gráficos              |
| `./scripts`     | `/home/jovyan/work/scripts`       | Scripts Python                      |

**Evidencia de persistencia:** Los datos en `postgres_data` sobreviven a
`docker compose down`. Solo se eliminan con `docker compose down -v`.

---

## Comandos de ejecución

### Levantar la infraestructura
```bash
# Construir imágenes y levantar todos los servicios
docker compose up --build

# En segundo plano (modo detached)
docker compose up --build -d
```

### Verificar estado
```bash
# Ver servicios corriendo y puertos
docker compose ps

# Ver logs de todos los servicios
docker compose logs

# Ver logs de un servicio específico
docker compose logs jupyter
docker compose logs postgres
```

### Cargar y analizar datos
```bash
# Opción 1: Desde la terminal del contenedor Jupyter
docker compose exec jupyter bash
python work/scripts/01_cargar_datos.py
python work/scripts/02_analisis.py

# Opción 2: Ejecutar directamente
docker compose exec jupyter python work/scripts/01_cargar_datos.py
docker compose exec jupyter python work/scripts/02_analisis.py
```

### Acceder a los servicios
```
Jupyter Lab:  http://localhost:8888  (token: datascience123)
pgAdmin:      http://localhost:5050  (admin@datascience.local / adminpass)
PostgreSQL:   localhost:5432         (dsuser / dspassword)
```

### Apagar la infraestructura
```bash
# Apagar (datos persisten en volúmenes)
docker compose down

# Apagar Y ELIMINAR volúmenes (borra todos los datos)
docker compose down -v
```

---

## Dependencias entre servicios

```
postgres  ──(healthcheck OK)──►  jupyter  (depends_on: service_healthy)
postgres  ──────────────────────►  pgadmin  (depends_on: service_started)
```

`jupyter` no arranca hasta que PostgreSQL responda al healthcheck
(`pg_isready`). Esto evita errores de conexión durante el inicio.

---

## Flujo de datos

```
1. docker compose up --build
        │
        ▼
2. PostgreSQL inicia → ejecuta init-db/01_crear_tablas.sql
   (crea esquema ciencia_datos, tablas ventas y resultados_analisis)
        │
        ▼
3. Jupyter inicia → espera que PG esté healthy
        │
        ▼
4. Usuario ejecuta: python scripts/01_cargar_datos.py
   → Genera 500 registros de ventas sintéticas
   → Guarda CSV en ./data/ventas_generadas.csv
   → Inserta datos en ciencia_datos.ventas (PostgreSQL)
        │
        ▼
5. Usuario ejecuta: python scripts/02_analisis.py
   → Consulta SQL (ventas por categoría, tendencia, top vendedores)
   → Genera gráfico PNG en ./data/analisis_ventas.png
   → Guarda resultados en ciencia_datos.resultados_analisis (PG)
```

---

## Estructura del proyecto

```
ejercicio5/
├── docker-compose.yml          # Orquestador principal
├── Dockerfile.jupyter          # Imagen Jupyter personalizada
├── .env                        # Variables de entorno (no versionar)
├── .gitignore
├── README.md
├── init-db/
│   └── 01_crear_tablas.sql     # Inicialización de PostgreSQL
├── scripts/
│   ├── 01_cargar_datos.py      # Genera e inserta el dataset
│   └── 02_analisis.py          # Consultas, análisis y resultados
├── notebooks/                  # Notebooks Jupyter (vacío inicial)
└── data/                       # CSVs y gráficos generados
```

---

## ¿Qué problemas resuelve Docker Compose?

✅ **Reproducibilidad**: cualquier persona puede levantar la misma infraestructura exacta con un solo comando.  
✅ **Aislamiento**: los servicios no interfieren con el sistema operativo del host.  
✅ **Comunicación entre servicios**: red interna automática; `postgres` es el hostname de PostgreSQL.  
✅ **Dependencias declarativas**: `depends_on` + `healthcheck` evitan race conditions al iniciar.  
✅ **Persistencia controlada**: volúmenes explícitos; claro qué datos sobreviven y cuáles no.  
✅ **Configuración centralizada**: un solo archivo `.yml` documenta toda la arquitectura.  

## ¿Qué problemas NO resuelve Docker Compose?

❌ **Escalabilidad horizontal**: no distribuye carga entre múltiples nodos (eso es Kubernetes).  
❌ **Alta disponibilidad**: si el host cae, todo cae. No hay failover automático.  
❌ **Seguridad en producción**: credenciales en `.env` no son adecuadas para entornos reales (usar Vault, Secrets Manager).  
❌ **Monitoreo y alertas**: no incluye Prometheus, Grafana ni sistemas de alertas.  
❌ **Gobierno de datos**: no gestiona linaje, calidad ni catalogación de datos.  
❌ **Backups automáticos**: los volúmenes persisten localmente pero no tienen respaldo automático.  
❌ **Actualizaciones sin downtime**: un `docker compose up` recrea los contenedores con interrupción de servicio.

---

## Diferencia clave: script local vs mini infraestructura

| Aspecto            | Script local (`python analisis.py`) | Mini infraestructura Docker Compose      |
|--------------------|--------------------------------------|------------------------------------------|
| Reproducibilidad   | Depende del entorno del usuario      | Idéntica en cualquier máquina con Docker |
| Dependencias       | Instaladas manualmente en el host    | Declaradas en Dockerfile y compose       |
| Aislamiento        | Ninguno                              | Cada servicio en su contenedor           |
| Persistencia       | Archivos locales                     | Volúmenes gestionados por Docker         |
| Comunicación       | Localhost directo                    | Red interna con DNS entre servicios      |
| Inicio             | Manual, orden importa                | `docker compose up` orquesta todo        |
| Colaboración       | "En mi máquina funciona"             | Funciona igual en todas las máquinas     |
