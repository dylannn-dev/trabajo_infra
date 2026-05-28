# Evaluación de Infraestructura y Procesamiento Paralelo

Este repositorio contiene el desarrollo práctico y experimental correspondiente a las semanas 1 a 6 de la asignatura INFB6074 - Infraestructura para Ciencia de Datos. 

El propósito central de esta investigación es comprender cómo las características internas del hardware condicionan el rendimiento del software analítico moderno. El contenido abarca desde la programación directa en bajo nivel e interacción con hardware, pasando por el análisis de concurrencia y construcción de pipelines optimizados, hasta el despliegue de arquitecturas distribuidas masivas mediante contenedores y el desarrollo del anteproyecto.

##  Requisitos del Sistema (Entorno de Validación)

El proyecto fue desarrollado y auditado bajo la siguiente configuración técnica:
* **Sistema Operativo:** Windows 11 Pro (Entorno de desarrollo PowerShell)
* **Procesador:** CPU multinúcleo con 12 hilos lógicos de procesamiento
* **Memoria RAM:** 16 GB unificada
* **Motor Docker:** Docker Desktop Versión 29.5.2
* **Compiladores y Emuladores:** NASM Versión 2.16.01 y QEMU Emulator Versión 11.0.0
* **Entorno de Lenguaje:** Python Versión 3.11

---

## Estructura del Repositorio

A continuación se detalla lo que el lector encontrará en cada carpeta del proyecto:

| Directorio / Carpeta | Descripción de los Contenidos |
| :--- | :--- |
| **`ejercicio_1/`** | Código fuente de un programa de arranque básico (*Bootloader*) escrito en lenguaje Ensamblador de 16 bits. Interactúa directamente con la memoria de video VGA y es emulado utilizando QEMU. |
| **`ejercicio_2/`** | Perfiladores de rendimiento en Python desarrollados para registrar la latencia y velocidad de la CPU, la memoria RAM y el disco de almacenamiento, evaluando los fallos de caché (*cache misses*). |
| **`ejercicio_3/`** | Implementación de procesamiento paralelo mediante el uso de hilos independientes (`ProcessPoolExecutor`) para medir el *Speedup* y la *Eficiencia* sobre registros transaccionales. |
| **`ejercicio_4/`** | Despliegue de un pipeline de Big Data basado en la metodología estructurada Medallion (Zonas Bronze, Silver y Gold). Incluye transformación a formato columnar Apache Parquet y consultas vectorizadas con DuckDB. |
| **`ejercicio_5/`** | Mini infraestructura multi-servicio coordinada mediante Docker Compose. Interconecta de forma aislada un motor PostgreSQL, Jupyter Lab y la interfaz de administración pgAdmin bajo una red privada. |
| **`ejercicio_6/`** | Matriz analítica multicriterio diseñada en Python para evaluar la viabilidad de distintas infraestructuras frente a escenarios organizacionales reales. |
| **`informe/`** | Contiene el documento oficial del informe técnico (`Informe - Dylan Novoa - infra.pdf`), el cual detalla de manera explicativa todos los análisis, métricas, conclusiones y resultados del proyecto. |
| **`parte_2_anteproyecto/`** | Documentos, archivos PDF y presentaciones (slides) correspondientes al desarrollo del anteproyecto de infraestructura de monitoreo y telemetría ambiental para ríos. |

---

## 🚀 Instrucciones de Ejecución y Reproducción

Para garantizar la reproducibilidad absoluta de las pruebas, sitúese en la carpeta del ejercicio correspondiente y ejecute los siguientes comandos estructurados en su terminal:

### Ejercicio 1: Compilación y Emulación del Entorno Booteable
```bash
nasm -f bin boot.asm -o boot.bin
qemu-system-i386 -drive format=raw,file=boot.bin