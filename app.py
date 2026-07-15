"""
API Flask para el asistente inteligente de la tienda de ropa.

Endpoints:
    GET  /salud       -> verifica que la API y la base de datos estén activas
    POST /preguntar    -> recibe {"pregunta": "..."} y devuelve {"respuesta": "..."}

Requisitos:
    pip install flask flask-cors psycopg2-binary python-dotenv google-genai langgraph
"""

import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from agente import construir_agente, preguntar

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)  # permite que el frontend (otro origen) consuma esta API

# Conexión y agente se crean una sola vez al arrancar la app (no en cada request)
_conn = psycopg2.connect(DATABASE_URL)
_cur = _conn.cursor()
_agente = construir_agente(_cur)


@app.route("/salud", methods=["GET"])
def salud():
    return jsonify({"status": "ok"})


@app.route("/preguntar", methods=["POST"])
def endpoint_preguntar():
    data = request.get_json(silent=True)

    if not data or "pregunta" not in data:
        return jsonify({"error": "Falta el campo 'pregunta' en el cuerpo JSON"}), 400

    pregunta = data["pregunta"].strip()

    if not pregunta:
        return jsonify({"error": "La pregunta no puede estar vacía"}), 400

    if len(pregunta) > 500:
        return jsonify({"error": "La pregunta es demasiado larga (máximo 500 caracteres)"}), 400

    try:
        _conn.rollback()  # limpia cualquier transacción fallida anterior antes de continuar
        respuesta = preguntar(_agente, pregunta)
        return jsonify({"pregunta": pregunta, "respuesta": respuesta})
    except Exception as e:
        _conn.rollback()
        app.logger.error(f"Error procesando pregunta: {e}")
        return jsonify({"error": "Ocurrió un error procesando tu pregunta. Intenta de nuevo."}), 500


if __name__ == "__main__":
    # Lee el puerto dinámico asignado por el servidor o usa el 5000 por defecto en local
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' expone la API para que pueda ser consumida externamente (como por tu frontend en Vite)
    app.run(host="0.0.0.0", port=port, debug=False)