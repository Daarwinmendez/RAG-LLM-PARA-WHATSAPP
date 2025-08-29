from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage

# Importa el agente ya inicializado y el prompt desde el archivo de configuración
from agente_config import rag_agent, system_prompt

# Inicializa la aplicación FastAPI
app = FastAPI(title="Solvex Bot API", version="1.0")

# Define el modelo de datos para validar la entrada
class QueryRequest(BaseModel):
    user_id: str
    query: str

# Define el endpoint POST /query
@app.post("/query")
async def process_query(request: QueryRequest):
    """
    Recibe una consulta, la procesa con el agente RAG y devuelve la respuesta.
    """
    initial_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=request.query)
    ]
    
    result = rag_agent.invoke({"messages": initial_messages})
    
    final_response = result['messages'][-1].content
    
    return {"user_id": request.user_id, "response": final_response}