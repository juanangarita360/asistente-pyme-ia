"""
Prueba de búsqueda semántica (RAG) sobre la tabla `documentos`.

Flujo:
    1. El usuario hace una pregunta en lenguaje natural
    2. Convertimos la pregunta en un embedding (mismo modelo que usamos para indexar)
    3. Buscamos en pgvector los documentos más parecidos (similitud coseno)
    4. Le pasamos esos documentos como contexto al LLM (Gemini) para que responda

Requisitos:
    pip install google-genai psycopg2-binary python-dotenv
"""

import os
import time

import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1536
LLM_MODEL = "gemini-flash-latest"  # alias que siempre apunta al Flash estable más reciente
TOP_K = 2  # cuántos documentos recuperar como contexto

client = genai.Client(api_key=GEMINI_API_KEY)


def generar_embedding(texto: str) -> list[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    return result.embeddings[0].values


def vector_a_string(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


def buscar_documentos_similares(pregunta: str, cur, top_k: int = TOP_K):
    """Busca los documentos más parecidos a la pregunta usando similitud coseno."""
    vector_pregunta = vector_a_string(generar_embedding(pregunta))

    # El operador <=> de pgvector calcula distancia coseno (menor = más parecido)
    cur.execute(
        """
        SELECT titulo, contenido, embedding <=> %s AS distancia
        FROM documentos
        ORDER BY distancia ASC
        LIMIT %s
        """,
        (vector_pregunta, top_k),
    )
    return cur.fetchall()


def llamar_con_reintentos(func, *args, intentos=3, espera_inicial=2, **kwargs):
    """Reintenta una llamada a la API con backoff exponencial si el servidor está saturado (503)."""
    for intento in range(intentos):
        try:
            return func(*args, **kwargs)
        except ServerError as e:
            if intento == intentos - 1:
                raise
            espera = espera_inicial * (2 ** intento)
            print(f"   ⚠️  Servidor ocupado, reintentando en {espera}s...")
            time.sleep(espera)


def generar_respuesta(pregunta: str, documentos_contexto: list) -> str:
    """Genera una respuesta usando el LLM, dado el contexto recuperado."""
    contexto = "\n\n".join(
        f"### {titulo}\n{contenido}" for titulo, contenido, _ in documentos_contexto
    )

    prompt = f"""Eres un asistente de atención al cliente de una tienda de ropa.
Responde la pregunta del usuario basándote ÚNICAMENTE en el siguiente contexto.
Si el contexto no tiene la respuesta, dilo claramente en vez de inventar información.

Contexto:
{contexto}

Pregunta del usuario: {pregunta}

Respuesta:"""

    response = llamar_con_reintentos(
        client.models.generate_content,
        model=LLM_MODEL,
        contents=prompt,
    )
    return response.text


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    preguntas_prueba = [
        "¿Cuánto tiempo tengo para devolver una prenda?",
        "¿Hacen envíos gratis?",
        "¿Puedo pagar contra entrega?",
    ]

    try:
        for pregunta in preguntas_prueba:
            print(f"\n{'='*60}")
            print(f"❓ Pregunta: {pregunta}")

            docs = buscar_documentos_similares(pregunta, cur)
            print(f"📄 Documentos recuperados: {[d[0] for d in docs]}")

            respuesta = generar_respuesta(pregunta, docs)
            print(f"🤖 Respuesta: {respuesta}")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
