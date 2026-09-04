import re
import sqlite3
import sys
from dataclasses import asdict, dataclass

COMMAND = re.compile(r"^(?:order:)?(?P<order_id>\d+)$")

@dataclass(frozen=True)
class Order:
    order_id: int
    customer_name: str
    status: str
    total_cents: int


def parse_command(text: str) -> int:
    match = COMMAND.fullmatch(text.strip())
    if not match:
        raise ValueError("Expected an order ID such as 1002")
    return int(match.group("order_id"))


def lookup_order(order_id: int, database_path: str = "orders.db") -> Order | None:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT order_id, customer_name, status, total_cents "
            "FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()
    return Order(*row) if row else None


def format_money(order: dict, key: str) -> dict:
    order[key] = f"${order[key] / 100:.2f}"
    return order


def handle(text: str) -> dict:
    order_id = parse_command(text)
    order = lookup_order(order_id)
    if order is None:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order": format_money(asdict(order), 'total_cents')}


if __name__ == "__main__":
    args = sys.argv[1:]
    order_id = args[0] if args else "1002"
    print(handle(f"order:{order_id}"))
