FROM python:3.11-slim
# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /work
# 3. Copiar el archivo de dependencias primero (Optimiza el caché de Docker)
COPY requirements.txt .
# 4. Instalar las librerías
RUN pip install --no-cache-dir -r requirements.txt
# 5. Copiar el resto del código al contenedor
COPY . .
# 6. El comando que se ejecutará al encender el contenedor
CMD ["python", "main.py"]