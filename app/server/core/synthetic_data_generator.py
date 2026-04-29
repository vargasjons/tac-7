import sqlite3
from typing import Any, Dict, List, Tuple

from core.sql_security import (
    SQLSecurityError,
    check_table_exists,
    escape_identifier,
    execute_query_safely,
    validate_identifier,
)


def sample_table_rows(
    conn: sqlite3.Connection, table_name: str, limit: int = 10
) -> List[Dict[str, Any]]:
    cursor = execute_query_safely(
        conn,
        "SELECT * FROM {table} ORDER BY RANDOM() LIMIT ?",
        params=(limit,),
        identifier_params={"table": table_name},
    )
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def insert_synthetic_rows(
    conn: sqlite3.Connection,
    table_name: str,
    rows: List[Dict[str, Any]],
    schema_columns: List[str],
) -> int:
    validate_identifier(table_name, "table")
    escaped_table = escape_identifier(table_name)

    inserted = 0
    for row in rows:
        filtered = {k: v for k, v in row.items() if k in schema_columns}
        if not filtered:
            continue

        col_names = list(filtered.keys())
        escaped_cols = ", ".join(escape_identifier(c) for c in col_names)
        placeholders = ", ".join("?" for _ in col_names)
        values = [filtered[c] for c in col_names]

        conn.execute(
            f"INSERT INTO {escaped_table} ({escaped_cols}) VALUES ({placeholders})",
            values,
        )
        inserted += 1

    conn.commit()
    return inserted


def generate_and_insert_data(
    table_name: str, row_count: int = 10
) -> Tuple[int, List[Dict[str, Any]]]:
    from core.llm_processor import generate_synthetic_data
    from core.sql_processor import get_database_schema

    conn = sqlite3.connect("db/database.db")
    try:
        if not check_table_exists(conn, table_name):
            raise SQLSecurityError(f"Table '{table_name}' does not exist")

        sample_rows = sample_table_rows(conn, table_name, limit=10)
        schema_info = get_database_schema()

        generated_rows = generate_synthetic_data(
            table_name, schema_info, sample_rows, row_count
        )

        if not isinstance(generated_rows, list) or not all(
            isinstance(r, dict) for r in generated_rows
        ):
            raise ValueError("LLM returned invalid data: expected a list of objects")

        table_schema = schema_info.get("tables", {}).get(table_name, {})
        schema_columns = [
            c for c in table_schema.get("columns", {}).keys() if c != "index"
        ]

        inserted_count = insert_synthetic_rows(
            conn, table_name, generated_rows, schema_columns
        )
        return inserted_count, generated_rows
    finally:
        conn.close()
