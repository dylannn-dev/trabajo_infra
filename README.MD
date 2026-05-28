# Evaluación de Infraestructura y Procesamiento Paralelo

Repositorio correspondiente al desarrollo práctico y experimental de las semanas 1 a 6 de la asignatura **INF8004 - Infraestructura para Ciencia de Datos**.

El objetivo principal de este proyecto es analizar cómo las características internas del hardware y la infraestructura de software influyen directamente en el rendimiento de aplicaciones analíticas modernas, abordando conceptos como:

* Interacción hardware/software.
* Programación de bajo nivel.
* Paralelismo y concurrencia.
* Arquitecturas distribuidas.
* Contenedores y virtualización.
* Procesamiento Big Data.
* Evaluación de infraestructuras computacionales.

---

# Tabla de Contenidos

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Entorno de Validación](#entorno-de-validación)
3. [Descripción de los Ejercicios](#descripción-de-los-ejercicios)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Instrucciones de Ejecución](#instrucciones-de-ejecución)
6. [Anteproyecto](#anteproyecto)
7. [Referencias](#referencias)

---

# Estructura del Proyecto

```text
evaluacion_semanas_1_5/
├── README.md
├── informe/
│   └── informe_evaluacion.pdf
├── parte_1_ejercicios/
│   ├── ejercicio_01_bootloader_qemu/
│   ├── ejercicio_02_benchmark_arquitectura/
│   ├── ejercicio_03_paralelismo_local/
│   ├── ejercicio_04_pipeline_bigdata_docker/
│   ├── ejercicio_05_docker_compose_infraestructura/
│   └── ejercicio_06_evaluacion_arquitectonica/
├── parte_2_anteproyecto/
│   ├── slides_anteproyecto.pdf
│   ├── documento_anteproyecto.pdf
│   └── diagramas/
└── referencias/
```

---

# Entorno de Validación

El proyecto fue desarrollado y validado bajo el siguiente entorno técnico:

| Componente               | Especificación                        |
| ------------------------ | ------------------------------------- |
| Sistema Operativo        | Windows 11 Pro                        |
| Procesador               | CPU multinúcleo con 12 hilos lógicos  |
| Memoria RAM              | 16 GB                                 |
| Virtualización           | Docker Desktop y QEMU                 |
| Compiladores             | NASM 2.16.01                          |
| Emuladores               | QEMU Emulator 11.0.0                  |
| Lenguaje Principal       | Python 3.11                           |
| Base de Datos            | PostgreSQL                            |
| Herramientas Adicionales | Apache Spark, Docker Compose, pgAdmin |

---

# Descripción de los Ejercicios

## Ejercicio 01 — Bootloader y Emulación con QEMU

Implementación de un bootloader básico en lenguaje ensamblador de 16 bits utilizando NASM y ejecutado mediante QEMU.

### Objetivos

* Comprender el proceso inicial de arranque.
* Analizar interacción directa con hardware.
* Estudiar arquitectura x86 básica.
* Validar ejecución en entorno emulado.

### Tecnologías

* NASM
* QEMU
* Assembly x86

---

## Ejercicio 02 — Benchmark y Evaluación Arquitectónica

Desarrollo de herramientas de benchmarking en Python para analizar:

* Latencia de CPU.
* Rendimiento de memoria RAM.
* Operaciones de entrada/salida.
* Comportamiento de caché.

### Objetivos

* Medir rendimiento computacional.
* Comparar tiempos de ejecución.
* Evaluar cuellos de botella del sistema.

### Tecnologías

* Python
* Multiprocessing
* Timeit
* NumPy

---

## Ejercicio 03 — Paralelismo Local y Concurrencia

Implementación de procesamiento paralelo mediante múltiples procesos independientes utilizando `ProcessPoolExecutor`.

### Objetivos

* Evaluar mejoras de rendimiento.
* Comparar ejecución secuencial vs paralela.
* Analizar escalabilidad local.

### Tecnologías

* Python
* concurrent.futures
* Multiprocessing

---

## Ejercicio 04 — Pipeline Big Data con Docker

Construcción de un pipeline de procesamiento Big Data basado en arquitectura medallion:

* Bronze Layer
* Silver Layer
* Gold Layer

Incluye integración con Apache Spark y servicios distribuidos mediante contenedores Docker.

### Objetivos

* Simular procesamiento distribuido.
* Automatizar flujo ETL.
* Evaluar arquitectura de datos escalable.

### Tecnologías

* Docker
* Apache Spark
* Python
* ETL Pipelines

---

## Ejercicio 05 — Infraestructura Multi-Servicio con Docker Compose

Diseño de infraestructura basada en múltiples servicios interconectados utilizando Docker Compose.

### Componentes

* PostgreSQL
* pgAdmin
* API Backend
* Contenedores auxiliares

### Objetivos

* Gestionar servicios distribuidos.
* Orquestar contenedores.
* Simular despliegues reales.

### Tecnologías

* Docker Compose
* PostgreSQL
* pgAdmin
* Python

---

## Ejercicio 06 — Evaluación Arquitectónica Multicriterio

Desarrollo de una matriz multicriterio en Python para evaluar distintas arquitecturas computacionales según:

* Escalabilidad.
* Rendimiento.
* Costos.
* Tolerancia a fallos.
* Mantenibilidad.

### Objetivos

* Comparar infraestructuras.
* Aplicar análisis cuantitativo.
* Justificar decisiones arquitectónicas.

### Tecnologías

* Python
* Pandas
* Matplotlib

---

# Informe Técnico

La carpeta `informe/` contiene el informe oficial del proyecto:

```text
informe/
└── informe_evaluacion.pdf
```

El documento incluye:

* Desarrollo metodológico.
* Resultados experimentales.
* Métricas obtenidas.
* Conclusiones técnicas.
* Evaluación crítica de la infraestructura.

---

# Anteproyecto

La carpeta `parte_2_anteproyecto/` contiene el desarrollo preliminar del sistema distribuido de monitoreo y telemetría ambiental para ríos.

## Contenido

| Archivo                      | Descripción                        |
| ---------------------------- | ---------------------------------- |
| `slides_anteproyecto.pdf`    | Presentación formal del proyecto   |
| `documento_anteproyecto.pdf` | Documento técnico del anteproyecto |
| `diagramas/`                 | Diagramas de arquitectura y flujo  |

---

# Tecnologías Utilizadas

## Infraestructura y Virtualización

* Docker
* Docker Compose
* QEMU

## Desarrollo y Procesamiento

* Python 3.11
* Assembly x86
* Apache Spark

## Bases de Datos

* PostgreSQL
* pgAdmin

## Herramientas de Evaluación

* Pandas
* NumPy
* Matplotlib

---

# Instrucciones de Ejecución

## Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd evaluacion_semanas_1_5
```

---

## Ejercicio 01 — Bootloader

```bash
cd parte_1_ejercicios/ejercicio_01_bootloader_qemu

nasm -f bin boot.asm -o boot.bin
qemu-system-i386 -drive format=raw,file=boot.bin
```

---

## Ejercicio 02 — Benchmark Arquitectónico

```bash
cd parte_1_ejercicios/ejercicio_02_benchmark_arquitectura

python benchmark.py
```

---

## Ejercicio 03 — Paralelismo Local

```bash
cd parte_1_ejercicios/ejercicio_03_paralelismo_local

python paralelismo.py
```

---

## Ejercicio 04 — Pipeline Big Data

```bash
cd parte_1_ejercicios/ejercicio_04_pipeline_bigdata_docker

docker compose up --build
```

---

## Ejercicio 05 — Infraestructura Multi-Servicio

```bash
cd parte_1_ejercicios/ejercicio_05_docker_compose_infraestructura

docker compose up
```

---

## Ejercicio 06 — Evaluación Arquitectónica

```bash
cd parte_1_ejercicios/ejercicio_06_evaluacion_arquitectonica

python evaluacion.py
```

---

# Referencias

La carpeta `referencias/` almacena documentación técnica, bibliografía y recursos utilizados durante el desarrollo del proyecto.

Ejemplos:

* Manuales de Docker.
* Documentación oficial de QEMU.
* Referencias NASM.
* Papers sobre paralelismo y arquitectura.
* Recursos académicos de infraestructura distribuida.

---

# Autor

**Dylan Alejandro Novoa Toro**
Proyecto académico desarrollado para la asignatura:

**INF8004 — Infraestructura para Ciencia de Datos**

---
