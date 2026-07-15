"""
Script para generar embeddings de los documentos (tabla `documentos`)
usando la API de Gemini y guardarlos en la columna `embedding` (pgvector).

Requisitos:
    pip install google-genai psycopg2-binary python-dotenv

Antes de correr, asegúrate de que tu .env tenga:
    DATABASE_URL=postgresql://...
    GEMINI_API_KEY=AIza...
"""

import os

import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DATABASE_URL:
    raise ValueError("Falta DATABASE_URL en el archivo .env")
if not GEMINI_API_KEY:
    raise ValueError("Falta GEMINI_API_KEY en el archivo .env")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1536  # debe coincidir con VECTOR(1536) en la tabla documentos

client = genai.Client(api_key=GEMINI_API_KEY)


def generar_embedding(texto: str) -> list[float]:
    """Genera el vector de embedding para un texto usando Gemini, con 1536 dimensiones."""
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    return result.embeddings[0].values


def vector_a_string(vector: list[float]) -> str:
    """Convierte una lista de floats al formato que espera pgvector: '[0.1,0.2,...]'."""
    return "[" + ",".join(str(v) for v in vector) + "]"


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, titulo, contenido FROM documentos WHERE embedding IS NULL")
        documentos = cur.fetchall()

        if not documentos:
            print("No hay documentos pendientes de embedding (todos ya lo tienen, o la tabla está vacía).")
            return

        print(f"Generando embeddings para {len(documentos)} documentos...\n")

        for doc_id, titulo, contenido in documentos:
            print(f"  → {titulo}")
            # Combinamos título + contenido para que el embedding capture mejor el contexto
            texto_completo = f"{titulo}\n\n{contenido}"
            vector = generar_embedding(texto_completo)
            vector_str = vector_a_string(vector)

            cur.execute(
                "UPDATE documentos SET embedding = %s WHERE id = %s",
                (vector_str, doc_id),
            )

        conn.commit()
        print(f"\n✅ Embeddings generados y guardados para {len(documentos)} documentos.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error, se revirtieron los cambios: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
