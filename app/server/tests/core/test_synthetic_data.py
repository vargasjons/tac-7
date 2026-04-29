import json
import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from core.synthetic_data_generator import (
    generate_and_insert_data,
    insert_synthetic_rows,
    sample_table_rows,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_conn_with_table(columns: dict | None = None) -> sqlite3.Connection:
    """Create an in-memory SQLite connection with a test table."""
    if columns is None:
        columns = {"id": "INTEGER", "name": "TEXT", "email": "TEXT"}
    conn = sqlite3.connect(":memory:")
    col_defs = ", ".join(f"{c} {t}" for c, t in columns.items())
    conn.execute(f"CREATE TABLE products ({col_defs})")
    conn.execute(
        "INSERT INTO products (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"
    )
    conn.execute(
        "INSERT INTO products (id, name, email) VALUES (2, 'Bob', 'bob@example.com')"
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# sample_table_rows tests
# ---------------------------------------------------------------------------

class TestSampleTableRows:
    def test_returns_list_of_dicts(self):
        conn = make_conn_with_table()
        rows = sample_table_rows(conn, "products", limit=10)
        assert isinstance(rows, list)
        assert all(isinstance(r, dict) for r in rows)
        assert len(rows) == 2

    def test_respects_limit(self):
        conn = make_conn_with_table()
        rows = sample_table_rows(conn, "products", limit=1)
        assert len(rows) == 1

    def test_correct_column_keys(self):
        conn = make_conn_with_table()
        rows = sample_table_rows(conn, "products", limit=10)
        assert set(rows[0].keys()) == {"id", "name", "email"}

    def test_empty_table_returns_empty_list(self):
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE empty_table (id INTEGER, val TEXT)")
        conn.commit()
        rows = sample_table_rows(conn, "empty_table", limit=10)
        assert rows == []


# ---------------------------------------------------------------------------
# insert_synthetic_rows tests
# ---------------------------------------------------------------------------

class TestInsertSyntheticRows:
    def _make_conn(self):
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE products (id INTEGER, name TEXT, email TEXT)")
        conn.commit()
        return conn

    def test_inserts_rows_and_returns_count(self):
        conn = self._make_conn()
        rows = [
            {"id": 10, "name": "Carol", "email": "carol@example.com"},
            {"id": 11, "name": "Dave", "email": "dave@example.com"},
        ]
        count = insert_synthetic_rows(conn, "products", rows, ["id", "name", "email"])
        assert count == 2
        cursor = conn.execute("SELECT COUNT(*) FROM products")
        assert cursor.fetchone()[0] == 2

    def test_filters_unknown_columns(self):
        conn = self._make_conn()
        rows = [{"id": 1, "name": "Eve", "email": "eve@ex.com", "extra_col": "should_be_ignored"}]
        count = insert_synthetic_rows(conn, "products", rows, ["id", "name", "email"])
        assert count == 1
        cursor = conn.execute("SELECT name FROM products")
        assert cursor.fetchone()[0] == "Eve"

    def test_skips_row_with_no_schema_columns(self):
        conn = self._make_conn()
        rows = [{"unknown_col": "value"}]
        count = insert_synthetic_rows(conn, "products", rows, ["id", "name", "email"])
        assert count == 0

    def test_handles_none_values(self):
        conn = self._make_conn()
        rows = [{"id": 5, "name": None, "email": None}]
        count = insert_synthetic_rows(conn, "products", rows, ["id", "name", "email"])
        assert count == 1
        cursor = conn.execute("SELECT name FROM products")
        assert cursor.fetchone()[0] is None

    def test_rejects_invalid_table_name(self):
        from core.sql_security import SQLSecurityError
        conn = sqlite3.connect(":memory:")
        with pytest.raises(SQLSecurityError):
            insert_synthetic_rows(conn, "DROP", [{"id": 1}], ["id"])


# ---------------------------------------------------------------------------
# LLM function tests
# ---------------------------------------------------------------------------

class TestLLMFunctions:
    SCHEMA = {
        "tables": {
            "products": {
                "columns": {"id": "INTEGER", "name": "TEXT"},
                "row_count": 2,
            }
        }
    }
    SAMPLE = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    @patch("core.llm_processor.OpenAI")
    def test_openai_parses_plain_json(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        payload = [{"id": 3, "name": "Carol"}, {"id": 4, "name": "Dave"}]
        mock_client.chat.completions.create.return_value.choices[
            0
        ].message.content = json.dumps(payload)

        from core.llm_processor import generate_synthetic_data_with_openai

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            result = generate_synthetic_data_with_openai(
                "products", self.SCHEMA, self.SAMPLE, 2
            )
        assert result == payload

    @patch("core.llm_processor.OpenAI")
    def test_openai_strips_markdown_fences(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        payload = [{"id": 5, "name": "Eve"}]
        mock_client.chat.completions.create.return_value.choices[
            0
        ].message.content = f"```json\n{json.dumps(payload)}\n```"

        from core.llm_processor import generate_synthetic_data_with_openai

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            result = generate_synthetic_data_with_openai(
                "products", self.SCHEMA, self.SAMPLE, 1
            )
        assert result == payload

    @patch("core.llm_processor.Anthropic")
    def test_anthropic_parses_plain_json(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        payload = [{"id": 6, "name": "Frank"}]
        mock_client.messages.create.return_value.content[
            0
        ].text = json.dumps(payload)

        from core.llm_processor import generate_synthetic_data_with_anthropic

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            result = generate_synthetic_data_with_anthropic(
                "products", self.SCHEMA, self.SAMPLE, 1
            )
        assert result == payload

    def test_router_raises_when_no_keys(self):
        from core.llm_processor import generate_synthetic_data

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(ValueError, match="No LLM API key"):
                generate_synthetic_data("products", self.SCHEMA, self.SAMPLE, 1)

    @patch("core.llm_processor.OpenAI")
    def test_router_prefers_openai(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        payload = [{"id": 7, "name": "Grace"}]
        mock_client.chat.completions.create.return_value.choices[
            0
        ].message.content = json.dumps(payload)

        from core.llm_processor import generate_synthetic_data

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "key", "ANTHROPIC_API_KEY": "key2"},
        ):
            result = generate_synthetic_data("products", self.SCHEMA, self.SAMPLE, 1)
        assert result == payload
        mock_cls.assert_called_once()


# ---------------------------------------------------------------------------
# generate_and_insert_data integration test (mocked LLM + mocked DB path)
# ---------------------------------------------------------------------------

class TestGenerateAndInsertData:
    SCHEMA = {
        "tables": {
            "products": {
                "columns": {"id": "INTEGER", "name": "TEXT"},
                "row_count": 2,
            }
        }
    }

    def _make_db(self, tmp_path):
        db_path = tmp_path / "database.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE products (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO products VALUES (1, 'Alice')")
        conn.commit()
        conn.close()
        return db_path

    def test_inserts_rows_increases_count(self, tmp_path):
        db_path = self._make_db(tmp_path)
        generated = [{"id": 10, "name": "Generated1"}, {"id": 11, "name": "Generated2"}]

        # Create real_conn BEFORE patch so sqlite3.connect is still real
        real_conn = sqlite3.connect(str(db_path))

        with (
            patch("core.synthetic_data_generator.sqlite3.connect", return_value=real_conn),
            patch("core.synthetic_data_generator.check_table_exists", return_value=True),
            patch("core.llm_processor.generate_synthetic_data", return_value=generated),
            patch("core.sql_processor.get_database_schema", return_value=self.SCHEMA),
        ):
            count, rows = generate_and_insert_data("products", row_count=2)

        assert count == 2
        assert rows == generated

        verify_conn = sqlite3.connect(str(db_path))
        cursor = verify_conn.execute("SELECT COUNT(*) FROM products")
        assert cursor.fetchone()[0] == 3
        verify_conn.close()
        real_conn.close()

    def test_missing_table_raises_error(self, tmp_path):
        db_path = self._make_db(tmp_path)
        from core.sql_security import SQLSecurityError

        real_conn = sqlite3.connect(str(db_path))

        with (
            patch("core.synthetic_data_generator.sqlite3.connect", return_value=real_conn),
            patch("core.synthetic_data_generator.check_table_exists", return_value=False),
        ):
            with pytest.raises(SQLSecurityError):
                generate_and_insert_data("nonexistent_table", row_count=2)
        real_conn.close()


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestGenerateDataEndpoint:
    @pytest.fixture
    def client(self):
        from server import app
        return TestClient(app)

    def test_endpoint_success(self, client):
        with (
            patch("server.validate_identifier", return_value=True),
            patch(
                "server.generate_and_insert_data",
                return_value=(5, [{"id": 1, "name": "X"}]),
            ),
        ):
            response = client.post(
                "/api/generate-data",
                json={"table_name": "products", "row_count": 5},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["inserted_count"] == 5
        assert data["table_name"] == "products"
        assert data["error"] is None

    def test_endpoint_invalid_table_returns_error(self, client):
        from core.sql_security import SQLSecurityError

        with patch("server.validate_identifier", side_effect=SQLSecurityError("bad name")):
            response = client.post(
                "/api/generate-data",
                json={"table_name": "DROP", "row_count": 10},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["error"] is not None
        assert data["inserted_count"] == 0

    def test_endpoint_no_llm_key_returns_error(self, client):
        with (
            patch("server.validate_identifier", return_value=True),
            patch(
                "server.generate_and_insert_data",
                side_effect=ValueError("No LLM API key found"),
            ),
        ):
            response = client.post(
                "/api/generate-data",
                json={"table_name": "products", "row_count": 10},
            )
        assert response.status_code == 200
        data = response.json()
        assert "No LLM API key" in data["error"]
        assert data["inserted_count"] == 0
