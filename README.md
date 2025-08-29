# Proyecto RAG - SolvexBot

Este documento contiene la guía completa para desplegar y ejecutar el agente RAG SolvexBot utilizando Docker. El proyecto está diseñado para ser empaquetado en un contenedor autocontenido que expone una API para consultas.

-----

## ⚙️ Pasos de Configuración (Requisitos Previos)

Antes de construir la imagen de Docker, es necesario realizar dos pasos de configuración únicos en tu máquina local.

### Paso 1: Configurar las Variables de Entorno

La aplicación necesita credenciales para funcionar. Deberás crear un archivo `.env` a partir del ejemplo proporcionado.

1.  Desde tu terminal, copia el archivo de ejemplo:
    ```bash
    cp .env.example .env
    ```
2.  Abre el nuevo archivo `.env` con un editor de texto.
3.  Rellena los valores, especialmente tu `HUGGINGFACE_API_TOKEN` y el `EMBEDDING_MODEL_NAME` que desees usar.

### Paso 2: Obtener la Base de Datos de Vectores

Debido al gran tamaño de la base de datos de vectores (`db_chroma`), resultó poco práctico subirla directamente al repositorio de GitHub. Por lo tanto, tienes dos opciones para obtenerla.

#### Opción A: Descargar la Base de Datos Pre-generada (Recomendado)

Esta es la forma más rápida de empezar.

1.  Descarga el archivo `db_chroma.zip` desde el siguiente enlace de Google Drive:
      * **Enlace de descarga:** [https://drive.google.com/drive/folders/15onQ1dTiiLqEddWGy7lSdjMYFcTMrlZS?usp=share\_link](https://drive.google.com/drive/folders/15onQ1dTiiLqEddWGy7lSdjMYFcTMrlZS?usp=share_link)
2.  Descomprime el archivo en la raíz de tu proyecto. Al finalizar, deberías tener una carpeta llamada `db_chroma`.

#### Opción B: Generar la Base de Datos Manualmente

Si prefieres, puedes generar los embeddings desde cero utilizando el script proporcionado.

1.  Asegúrate de tener Python 3.12 y `pip` instalados.
2.  Instala las dependencias necesarias para ejecutar el script:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecuta el script de indexación:
    ```bash
    python crear_embeddings.py
    ```

Al completar una de las dos opciones, tendrás la carpeta `db_chroma` en tu proyecto y estarás listo para usar Docker.

-----

## 🐳 Despliegue con Docker

Con la configuración previa completada, puedes empaquetar y ejecutar la aplicación.

### Paso 3: Construir la Imagen de Docker

Este comando lee el `Dockerfile`, copia todos los archivos necesarios (incluida la carpeta `db_chroma`) y construye la imagen de la aplicación.

```bash
docker build -t solvex-bot-api .
```

### Paso 4: Ejecutar el Contenedor

Este comando inicia un contenedor a partir de la imagen que acabas de crear. El contenedor ejecutará la API en segundo plano.

```bash
docker run -d -p 8000:8000 --env-file ./.env solvex-bot-api
```

**Importante:** El flag `--env-file ./.env` inyecta tus secretos de forma segura en el contenedor en tiempo de ejecución, sin exponerlos dentro de la imagen.

### Paso 5: Probar la API

Una vez que el contenedor esté en ejecución, puedes enviarle consultas.

  - **Verificar que está corriendo:**

    ```bash
    docker ps
    ```

  - **Ejemplos de Consultas con `curl`:**

    **Consulta 1: Objetivo de FormeSX**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Cuál es el objetivo principal de la aplicación FormeSX?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 2: Servicio CloudFlow MSP**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Qué significa que el servicio CloudFlow MSP es proactivo en lugar de reactivo?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 3: Beneficios de CloudFlow MSP**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Cuáles son los beneficios clave de CloudFlow MSP?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 4: Sobre Media Shelter**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Qué es Media Shelter?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 5: Plataformas de Capacitación**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Ofrecen plataformas para capacitación?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 6: Soluciones de IA**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Qué soluciones ofrecen de Inteligencia de Negocios e Inteligencia Artificial?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 7: Soluciones Tecnológicas**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Qué soluciones Tecnológicas Ofrecen Ustedes?"}' \
      http://127.0.0.1:8000/query
    ```

    **Consulta 8: Sobre CRMs**

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"user_id": "user-test-001", "query": "¿Ustedes hacen CRMs?, somos una agencia de viajes, y necesitamos de su ayuda."}' \
      http://127.0.0.1:8000/query
    ```

-----

## 🚢 Gestión del Contenedor

Comandos útiles para administrar tu contenedor.

  - **Ver los logs (registros) de la aplicación en tiempo real:**

    ```bash
    docker logs -f <ID_DEL_CONTENEDOR>
    ```

    *(Obtienes el ID con `docker ps`)*

  - **Detener el contenedor:**

    ```bash
    docker stop <ID_DEL_CONTENEDOR>
    ```
