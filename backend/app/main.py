from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import get_connection

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===== PÁGINAS WEB =====

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/waiter", response_class=HTMLResponse)
def waiter_page(request: Request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener categorías
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    # Obtener productos con categoría
    cursor.execute("""
        SELECT p.id, p.name, p.price, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY c.name, p.name
    """)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return templates.TemplateResponse("waiter.html", {
        "request": request,
        "categories": categories,
        "products": products
    })


@app.get("/kitchen", response_class=HTMLResponse)
def kitchen_page(request: Request):
    return templates.TemplateResponse("kitchen.html", {"request": request})

@app.get("/cashier", response_class=HTMLResponse)
def cashier_page(request: Request):
    return templates.TemplateResponse("cashier.html", {"request": request})

# ===== API =====

@app.post("/login")
def login(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, role FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"success": False}

    return {"success": True, "user": user}

@app.get("/tables")
def get_tables():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tables")
    tables = cursor.fetchall()
    conn.close()
    return tables

@app.get("/products")
def get_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.name, p.price, c.name AS category
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
    """)
    products = cursor.fetchall()
    conn.close()
    return products

# Obtener mesas con estado
@app.get("/tables/status")
def get_tables_status():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, number, status FROM tables")
    tables = cursor.fetchall()
    conn.close()
    return tables


#Crear pedido (Enviar pedido)
from fastapi import Body
@app.post("/orders")
def create_order(data: dict = Body(...)):
    table_id = data.get("table_id")
    items = data.get("items")

    conn = get_connection()
    cursor = conn.cursor()

    # crear pedido
    cursor.execute(
        "INSERT INTO orders (table_id, order_type, status) VALUES (%s, 'TABLE', 'CREATED')",
        (table_id,)
    )
    order_id = cursor.lastrowid

    # insertar items
    for item in items:
        cursor.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, price_snapshot)
            SELECT %s, id, %s, price FROM products WHERE id=%s
            """,
            (order_id, item["quantity"], item["product_id"])
        )

    # marcar mesa como ocupada
    cursor.execute("UPDATE tables SET status='OCCUPIED' WHERE id=%s", (table_id,))

    # registrar historial de mesa
    cursor.execute(
        "INSERT INTO order_history (order_id, table_id, occupied_at) VALUES (%s, %s, NOW())",
        (order_id, table_id)
    )

    conn.commit()
    conn.close()

    return {"success": True, "order_id": order_id}



# Obtener productos
@app.get("/products")
def get_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

# Liberar Mesa
@app.post("/tables/{table_id}/free")
def free_table(table_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣Marcar mesa como libre
    cursor.execute("UPDATE tables SET status='FREE' WHERE id=%s", (table_id,))

    #  Obtener último historial de ocupación sin freed_at
    cursor.execute("""
        SELECT id
        FROM order_history
        WHERE table_id = %s AND freed_at IS NULL
        ORDER BY occupied_at DESC
        LIMIT 1
    """, (table_id,))
    last_history = cursor.fetchone()

    if last_history:
        history_id = last_history['id']
        cursor.execute(
            "UPDATE order_history SET freed_at = NOW() WHERE id = %s",
            (history_id,)
        )

    conn.commit()
    conn.close()
    return {"success": True}

