import os
import json
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

# . CONFIGURACIÓN INICIAL USANDO VARIABLES DE ENTORNO 
DIRECTORIO_PERSISTENTE = os.getenv("DIRECTORIO_PERSISTENTE", "db_chroma")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
LLM_REPO_ID = os.getenv("LLM_REPO_ID")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
TOP_K = int(os.getenv("TOP_K", 5))

# INICIALIZACIÓN DE COMPONENTES (SE EJECUTA UNA SOLA VEZ)
print("--- Inicializando componentes del agente... ---")
#embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
embeddings = HuggingFaceEndpointEmbeddings(model=EMBEDDING_MODEL_NAME, task="feature-extraction", huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN"))

vectorstore = Chroma(
    persist_directory=DIRECTORIO_PERSISTENTE,
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": TOP_K})

llm = ChatHuggingFace(
    llm=HuggingFaceEndpoint(
        repo_id=LLM_REPO_ID,
        task="text-generation",
        temperature=0.2,
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        max_new_tokens=1024,
    )
)

@tool
def retriever_tool(query: str) -> str:
    """Busca y devuelve información relevante de los documentos de productos de Solvex."""
    print(f"--- Ejecutando Retriever con la consulta: '{query}' ---")
    docs = retriever.invoke(query)
    if not docs:
        return "No se encontró información en los documentos para esta consulta."
    return "\n\n".join([doc.page_content for doc in docs])

# DEFINICIÓN Y COMPILACIÓN DEL GRAFO 
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


tools = [retriever_tool]
tools_dict = {t.name: t for t in tools}

def call_llm(state: AgentState):
    print("--- Llamando al LLM ---")
    messages = state['messages']
    response = llm.invoke(messages)
    print(f"--- Respuesta en crudo del LLM:\n{response.content}\n---")
    return {"messages": [response]}

def take_action(state: AgentState):
    print("--- Tomando Acción ---")
    last_message = state['messages'][-1].content
    try:
        action_data = json.loads(last_message)
        tool_name = action_data.get("tool_name")
        query = action_data.get("query")

        if tool_name in tools_dict:
            result = tools_dict[tool_name].invoke(query)
            tool_message = ToolMessage(content=str(result), name=tool_name, tool_call_id="manual_call")
            return {"messages": [tool_message]}
        else:
            error_message = AIMessage(content=f"Error: La herramienta '{tool_name}' no fue encontrada.")
            return {"messages": [error_message]}
    except json.JSONDecodeError:
        # Si la respuesta no es JSON, es la respuesta final del agente.
        # En este punto, no hacemos nada, ya que el borde `should_continue` la llevará al final.
        return

def should_continue(state: AgentState):
    last_message_content = state['messages'][-1].content
    try:
        # Una forma robusta de verificar si es un JSON con las claves correctas
        data = json.loads(last_message_content)
        if "tool_name" in data and "query" in data:
            return "action"
    except json.JSONDecodeError:
        pass # No es un JSON, por lo tanto, es la respuesta final.
    
    return END

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("action", take_action)
graph.set_entry_point("llm")
graph.add_conditional_edges("llm", should_continue, {"action": "action", END: END})
graph.add_edge("action", "llm")
rag_agent = graph.compile()


print("--- Agente compilado y listo. ---")

# --- 4. SYSTEM PROMPT (PARA SER USADO POR LA API) ---
system_prompt = """
  Eres SolvexBot, un asistente de inteligencia artificial experto en los productos y servicios de la empresa Solvex. Tu única fuente de conocimiento son los documentos de producto que te han sido proporcionados.

  Tu tarea es responder a las preguntas de los usuarios de manera profesional, amable y precisa, simulando una conversación de WhatsApp.

  **Instrucciones de Operación:**
  1.  Cuando un usuario te haga una pregunta sobre un producto, primero debes usar la herramienta 'retriever_tool' para buscar información en los documentos.
  2.  Para usar la herramienta, DEBES responder ÚNICAMENTE con un objeto JSON en el siguiente formato:
      {"tool_name": "retriever_tool", "query": "una pregunta concisa que resuma la duda del usuario"}
  3.  Una vez que recibas la información del 'retriever_tool' (el CONTEXTO), debes formular una respuesta final para el usuario.

  **Reglas para Responder:**
  -   **BASA TU RESPUESTA ESTRICTAMENTE EN EL CONTEXTO PROPORCIONADO.** No utilices ningún conocimiento externo.
  -   Si el contexto no contiene la información necesaria para responder la pregunta, DEBES decir amablemente: "Lo siento, no he podido encontrar esa información específica en los documentos de nuestros productos." NO INVENTES RESPUESTAS.
  -   Si la pregunta del usuario es un saludo o no está relacionada con los productos (ej. "¿cómo estás?"), responde de manera cordial y breve sin usar la herramienta.
  -   Habla siempre en español.
  """