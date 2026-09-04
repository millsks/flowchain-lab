import sqlite3

with sqlite3.connect("orders.db") as connection:
    connection.execute("DROP TABLE IF EXISTS orders")
    connection.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            status TEXT NOT NULL,
            total_cents INTEGER NOT NULL CHECK(total_cents >= 0)
        )
        """
    )
    connection.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [
            (1001, "Avery", "shipped", 2599),
            (1002, "Blake", "processing", 4200),
            (1003, "Casey", "delivered", 1599),
            (1004, "Dakota", "cancelled", 0),
        ],
    )