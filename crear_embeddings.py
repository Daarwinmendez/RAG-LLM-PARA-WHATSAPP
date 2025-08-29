import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# --- 1. CONFIGURACIÓN INICIAL (USANDO VARIABLES DE ENTORNO) ---
DIRECTORIO_PERSISTENTE = os.getenv("DIRECTORIO_PERSISTENTE", "db_chroma")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
PATH_A_PRODUCTOS = "productos_pdf" # Esta puede seguir siendo una ruta fija

print("--- Iniciando el proceso de indexación de archivos PDF ---")
print(f"Directorio de persistencia: {DIRECTORIO_PERSISTENTE}")
print(f"Modelo de embeddings: {EMBEDDING_MODEL_NAME}")
print(f"Carpeta de documentos: {PATH_A_PRODUCTOS}")

# --- 2. Cargar los Documentos PDF ---

# Comprobamos si la carpeta de productos existe.
if not os.path.exists(PATH_A_PRODUCTOS):
    raise FileNotFoundError(
        f"La carpeta '{PATH_A_PRODUCTOS}' no fue encontrada. "
        "Por favor, créala y coloca tus archivos PDF dentro."
    )

# Usamos DirectoryLoader para cargar todos los archivos .pdf de la carpeta.
loader = DirectoryLoader(
    PATH_A_PRODUCTOS,
    glob="**/*.pdf",       # Patrón para encontrar todos los archivos .pdf
    loader_cls=PyPDFLoader
)

documents = loader.load()

if not documents:
    raise ValueError(
        f"No se encontraron documentos PDF en la carpeta '{PATH_A_PRODUCTOS}'. "
        "Asegúrate de que la ruta es correcta y que los archivos están ahí."
    )

print(f"Se han cargado {len(documents)} páginas desde los archivos PDF.")

# --- 3. Dividir los Documentos en Chunks ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)
print(f"Los documentos se han dividido en {len(chunks)} trozos (chunks).")


# --- 4. Crear los Embeddings ---
print("Inicializando el modelo de embeddings. Esto puede tardar un momento...")
embeddings = HuggingFaceEndpointEmbeddings(
    model=EMBEDDING_MODEL_NAME,
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
)


# --- 5. Guardar en la Base de Datos de Vectores (ChromaDB) ---
print("Creando y guardando los embeddings en el Vector Store (ChromaDB)...")

# Chroma.from_documents se encarga de crear la base de datos,
# generar los embeddings para cada chunk y guardarlos de forma persistente.
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DIRECTORIO_PERSISTENTE,
)

print("-" * 50)
print("¡Proceso de indexación completado con éxito!")
print(f"La base de datos de vectores ha sido guardada en la carpeta: '{DIRECTORIO_PERSISTENTE}'")
print("-" * 50)