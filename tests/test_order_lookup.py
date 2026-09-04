import sqlite3

import pytest

from langchain_pipeline import pipeline
from order_lookup import handle, lookup_order, parse_command


def test_parse_command_accepts_known_format():
    assert parse_command("order:1002") == 1002


def test_parse_command_accepts_bare_order_id():
    assert parse_command("1002") == 1002


def test_parse_command_rejects_unknown_format():
    with pytest.raises(ValueError, match="Expected an order ID"):
        parse_command("where is 1002?")


def test_missing_order_has_stable_response(tmp_path):
    database = tmp_path / "empty.db"
    with sqlite3.connect(database) as connection:
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

    assert lookup_order(1002, str(database)) is None


def test_found_order_formats_money(tmp_path, monkeypatch):
    database = tmp_path / "orders.db"
    with sqlite3.connect(database) as connection:
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
        connection.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (1002, "Blake", "processing", 4200))

    monkeypatch.chdir(tmp_path)
    assert handle("order:1002") == {
        "found": True,
        "order": {
            "order_id": 1002,
            "customer_name": "Blake",
            "status": "processing",
            "total_cents": "$42.00",
        },
    }


def test_handle_reports_missing_order(tmp_path, monkeypatch):
    database = tmp_path / "orders.db"
    with sqlite3.connect(database) as connection:
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

    monkeypatch.chdir(tmp_path)
    assert handle("order:9999") == {"found": False, "order_id": 9999}


def test_pipeline_passes_parsed_order_id_to_lookup(tmp_path, monkeypatch):
    database = tmp_path / "orders.db"
    with sqlite3.connect(database) as connection:
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
        connection.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (1002, "Blake", "processing", 4200))

    monkeypatch.chdir(tmp_path)
    assert pipeline.invoke("1002") == {
        "found": True,
        "order": {
            "order_id": 1002,
            "customer_name": "Blake",
            "status": "processing",
            "total_cents": 4200,
        },
    }


def test_pipeline_handles_health_check():
    assert pipeline.invoke("health") == {"status": "ok"}
