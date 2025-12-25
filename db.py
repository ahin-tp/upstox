import sqlite3

# ===============================
# DB connection
# ===============================
conn = sqlite3.connect("orders.db", check_same_thread=False)
conn.row_factory = sqlite3.Row   # ⭐ IMPORTANT
cursor = conn.cursor()

# ===============================
# TABLE
# ===============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument TEXT NOT NULL,
    qty INTEGER NOT NULL,
    trigger REAL NOT NULL,
    limit_price REAL NOT NULL,
    stop_loss REAL NOT NULL,

    entry_order_id TEXT,
    sl_order_id TEXT,

    status TEXT DEFAULT 'PENDING'
)
""")
conn.commit()

# ===============================
# ADD ORDER (from UI)
# ===============================
def add_order(data):
    cursor.execute("""
        INSERT INTO orders (
            instrument, qty, trigger, limit_price, stop_loss
        ) VALUES (?, ?, ?, ?, ?)
    """, data)
    conn.commit()

# ===============================
# FETCH PENDING ORDERS (scheduler)
# ===============================
def get_pending_orders():
    cursor.execute("""
        SELECT *
        FROM orders
        WHERE status = 'PENDING'
    """)
    return cursor.fetchall()

# ===============================
# SAVE UPSTOX ORDER IDS
# ===============================
def save_order_ids(db_id, entry_id, sl_id):
    cursor.execute("""
        UPDATE orders
        SET entry_order_id = ?, sl_order_id = ?, status = 'EXECUTED'
        WHERE id = ?
    """, (entry_id, sl_id, db_id))
    conn.commit()

# ===============================
# MARK CANCELLED
# ===============================
def mark_cancelled(db_id):
    cursor.execute("""
        UPDATE orders
        SET status = 'CANCELLED'
        WHERE id = ?
    """, (db_id,))
    conn.commit()

# ===============================
# MARK EXITED
# ===============================
def mark_exited(db_id):
    cursor.execute("""
        UPDATE orders
        SET status = 'EXITED'
        WHERE id = ?
    """, (db_id,))
    conn.commit()

# ===============================
# HELPERS FOR UI ACTIONS
# ===============================
def get_order_by_id(db_id):
    cursor.execute("""
        SELECT *
        FROM orders
        WHERE id = ?
    """, (db_id,))
    return cursor.fetchone()

def get_all_orders():
    cursor.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
    """)
    return cursor.fetchall()
