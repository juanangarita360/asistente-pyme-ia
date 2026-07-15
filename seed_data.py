"""
Script para generar datos de ejemplo (tienda de ropa) e insertarlos
en la base de datos de Supabase.

Requisitos:
    pip install faker psycopg2-binary python-dotenv

Antes de correr:
    1. Crea un archivo .env en la misma carpeta con:
       DATABASE_URL=postgresql://postgres.xxxx:TU_PASSWORD@aws-1-sa-east-1.pooler.supabase.com:5432/postgres
    2. Corre: python seed_data.py
"""

import os
import random
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
fake = Faker("es_CO")  # nombres/ciudades en español, estilo Colombia

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Falta DATABASE_URL en el archivo .env")

# ---------------------------------------------------------------------
# Datos base de la tienda de ropa
# ---------------------------------------------------------------------

CATEGORIAS = ["Camisetas", "Pantalones", "Vestidos", "Chaquetas", "Zapatos", "Accesorios"]

PRODUCTOS_BASE = [
    ("Camiseta básica algodón", "Camisetas", 45000),
    ("Camiseta estampada", "Camisetas", 55000),
    ("Jean slim fit", "Pantalones", 120000),
    ("Pantalón jogger", "Pantalones", 95000),
    ("Vestido casual", "Vestidos", 130000),
    ("Vestido de fiesta", "Vestidos", 250000),
    ("Chaqueta de cuero", "Chaquetas", 320000),
    ("Chaqueta impermeable", "Chaquetas", 180000),
    ("Tenis urbanos", "Zapatos", 210000),
    ("Botas de cuero", "Zapatos", 280000),
    ("Gorra", "Accesorios", 35000),
    ("Cinturón de cuero", "Accesorios", 60000),
    ("Bufanda", "Accesorios", 40000),
    ("Sudadera con capota", "Chaquetas", 110000),
    ("Falda casual", "Vestidos", 85000),
]

CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Neiva", "Pereira"]

DOCUMENTOS = [
    (
        "Política de devoluciones",
        "Los clientes pueden solicitar la devolución de una prenda dentro de los "
        "30 días calendario posteriores a la compra, siempre que el producto "
        "conserve sus etiquetas originales y no muestre signos de uso. Las "
        "devoluciones por talla incorrecta no generan costo adicional. El "
        "reembolso se procesa en un plazo máximo de 10 días hábiles.",
    ),
    (
        "Política de envíos",
        "Realizamos envíos a todo el país a través de transportadoras aliadas. "
        "El tiempo estimado de entrega es de 3 a 5 días hábiles en ciudades "
        "principales y de 5 a 8 días hábiles en municipios apartados. El envío "
        "es gratuito para compras superiores a $150.000 COP.",
    ),
    (
        "Guía de tallas",
        "Nuestras prendas manejan tallas estándar colombianas (XS a XXL). "
        "Recomendamos revisar la tabla de medidas en cada producto antes de "
        "comprar, ya que algunas prendas como vestidos y chaquetas pueden "
        "tener un ajuste diferente al de camisetas básicas.",
    ),
    (
        "Métodos de pago",
        "Aceptamos pagos con tarjeta de crédito, débito, PSE y pago contra "
        "entrega en ciudades principales. Todos los pagos en línea son "
        "procesados de forma segura a través de nuestra pasarela de pagos.",
    ),
    (
        "Programa de fidelización",
        "Por cada compra, el cliente acumula puntos que puede redimir en "
        "futuras compras. Los clientes frecuentes reciben descuentos "
        "exclusivos y acceso anticipado a nuevas colecciones.",
    ),
]

N_CLIENTES = 40
N_VENTAS = 150
MESES_HISTORIAL = 3


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def seed_clientes(cur):
    print(f"Insertando {N_CLIENTES} clientes...")
    ids = []
    for _ in range(N_CLIENTES):
        nombre = fake.name()
        email = fake.email()
        ciudad = random.choice(CIUDADES)
        fecha_registro = fake.date_between(start_date="-1y", end_date="today")
        cur.execute(
            """
            INSERT INTO clientes (nombre, email, ciudad, fecha_registro)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (nombre, email, ciudad, fecha_registro),
        )
        ids.append(cur.fetchone()[0])
    return ids


def seed_productos(cur):
    print(f"Insertando {len(PRODUCTOS_BASE)} productos...")
    ids = []
    for nombre, categoria, precio in PRODUCTOS_BASE:
        stock = random.randint(5, 80)
        cur.execute(
            """
            INSERT INTO productos (nombre, categoria, precio, stock)
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (nombre, categoria, precio, stock),
        )
        ids.append((cur.fetchone()[0], precio))
    return ids


def seed_ventas(cur, cliente_ids, producto_ids):
    print(f"Insertando {N_VENTAS} ventas con su detalle...")
    hoy = datetime.now()
    inicio = hoy - timedelta(days=30 * MESES_HISTORIAL)

    for _ in range(N_VENTAS):
        cliente_id = random.choice(cliente_ids)
        dias_random = random.randint(0, (hoy - inicio).days)
        fecha_venta = (inicio + timedelta(days=dias_random)).date()

        n_items = random.randint(1, 4)
        items = random.sample(producto_ids, k=min(n_items, len(producto_ids)))

        total = 0
        detalle = []
        for producto_id, precio in items:
            cantidad = random.randint(1, 3)
            subtotal = precio * cantidad
            total += subtotal
            detalle.append((producto_id, cantidad, precio))

        cur.execute(
            """
            INSERT INTO ventas (cliente_id, fecha, total)
            VALUES (%s, %s, %s) RETURNING id
            """,
            (cliente_id, fecha_venta, total),
        )
        venta_id = cur.fetchone()[0]

        for producto_id, cantidad, precio_unitario in detalle:
            cur.execute(
                """
                INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
                """,
                (venta_id, producto_id, cantidad, precio_unitario),
            )


def seed_documentos(cur):
    print(f"Insertando {len(DOCUMENTOS)} documentos (sin embedding todavía)...")
    # El embedding se genera en la Fase 3 (RAG), aquí queda en NULL por ahora.
    for titulo, contenido in DOCUMENTOS:
        cur.execute(
            """
            INSERT INTO documentos (titulo, contenido)
            VALUES (%s, %s)
            """,
            (titulo, contenido),
        )


def main():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cliente_ids = seed_clientes(cur)
        producto_ids = seed_productos(cur)
        seed_ventas(cur, cliente_ids, producto_ids)
        seed_documentos(cur)
        conn.commit()
        print("\n✅ Datos de ejemplo insertados correctamente.")
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error, se revirtieron los cambios: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()