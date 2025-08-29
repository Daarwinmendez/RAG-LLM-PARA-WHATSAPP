# --- PASO 1: Usar una imagen base oficial de Python ---
# Empezamos con un sistema operativo ligero que ya tiene Python 3.12 instalado.
FROM python:3.12-slim

# --- PASO 2: Establecer el directorio de trabajo ---
# Creamos una carpeta llamada '/app' dentro del contenedor y la definimos
# como nuestro directorio de trabajo principal. Todos los comandos siguientes se
# ejecutarán desde aquí.
WORKDIR /app

# --- PASO 3: Instalar las dependencias ---
# Copiamos ÚNICAMENTE el archivo de requerimientos primero. Docker guarda en caché
# este paso. Si no cambiamos 'requirements.txt', Docker no reinstalará todo
# cada vez, haciendo las construcciones futuras mucho más rápidas.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- PASO 4: Copiar el resto del proyecto ---
# Ahora copiamos todo lo demás: nuestros scripts de Python, la base de datos
# de vectores ('db_chroma'), y el archivo '.env'. El archivo '.dockerignore'
# asegurará que los archivos innecesarios no se copien.
COPY . .

# --- PASO 5: Exponer el puerto ---
# Le decimos a Docker que la aplicación dentro de este contenedor escuchará
# en el puerto 8000. Esto es como abrir una ventana para que el mundo exterior
# pueda hablar con nuestra API.
EXPOSE 8000

# --- PASO 6: Definir el comando de ejecución ---
# Este es el comando que se ejecutará automáticamente cuando se inicie el contenedor.
# Inicia el servidor Uvicorn para nuestra aplicación FastAPI, haciéndolo accesible
# desde cualquier dirección IP ('0.0.0.0') en el puerto 8000.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]