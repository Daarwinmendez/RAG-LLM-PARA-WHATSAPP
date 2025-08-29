import pytest
from agente_config import retriever_tool

def test_recuperacion_de_informacion_relevante():
    """
    Prueba que la herramienta retriever devuelve contenido relevante para una consulta.
    NOTA: Esto asume que tienes un PDF que habla sobre "garantía".
    """
    # Arrange
    query = "¿Qué garantía tienen los productos?"
    
    # Act
    resultado = retriever_tool.invoke(query)
    
    # Assert
    assert isinstance(resultado, str)
    assert "garantía" in resultado.lower()
    assert "no se encontró información" not in resultado.lower()

def test_recuperacion_sin_informacion():
    """Prueba que el retriever maneja bien una consulta sin resultados."""
    # Arrange
    query = "información sobre recetas de cocina"
    
    # Act
    resultado = retriever_tool.invoke(query)
    
    # Assert
    assert "no se encontró información" in resultado.lower()