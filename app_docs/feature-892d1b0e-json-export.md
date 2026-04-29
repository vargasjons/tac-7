# JSON Export Feature

**ADW ID:** 892d1b0e (adw-2)
**Date:** 2026-04-29
**Specification:** specs/issue-892d1b0e-adw-2-sdlc_planner-add-json-export.md

## Overview

Adds JSON export functionality for both full tables and query results, complementing the existing CSV export. Users can download data as pretty-printed JSON arrays of objects, which preserves data types (integers, booleans, nulls) that CSV flattens to strings. The feature follows the exact same pattern as CSV export across the full stack.

## What Was Built

- `generate_json_from_data()` utility — serializes query result rows to a JSON array of objects
- `generate_json_from_table()` utility — reads a SQLite table via pandas and serializes to JSON
- `POST /api/export/table-json` endpoint — downloads a named table as `{table_name}.json`
- `POST /api/export/query-json` endpoint — downloads query results as `query_results.json`
- `JsonExportRequest` and `QueryJsonExportRequest` Pydantic models
- `exportTableAsJson()` and `exportQueryResultsAsJson()` TypeScript API client functions
- JSON export buttons on both the query results panel and each table card in the UI
- Unit tests for all new JSON utility functions (7 test cases)

## Technical Implementation

### Files Modified

- `app/server/core/export_utils.py`: Added `generate_json_from_data()` and `generate_json_from_table()` using `json.dumps(indent=2, default=str)`
- `app/server/server.py`: Added `POST /api/export/table-json` and `POST /api/export/query-json` FastAPI endpoints with security validation
- `app/server/core/data_models.py`: Added `JsonExportRequest` and `QueryJsonExportRequest` Pydantic models (intentionally separate from CSV models for future divergence)
- `app/client/src/api/client.ts`: Added `exportTableAsJson()` and `exportQueryResultsAsJson()` using the same blob-download pattern as CSV
- `app/client/src/main.ts`: Added JSON export buttons on the query results toolbar and each table card header
- `app/server/tests/test_export_utils.py`: Added `TestJsonExportUtils` class with 7 unit tests

### Key Changes

- `json.dumps(indent=2, default=str)` is used throughout — `default=str` handles SQLite types like `datetime` that the stdlib `json` module cannot serialize natively
- The `generate_json_from_table()` utility performs its own existence check (raises `ValueError`) in addition to the endpoint-level `check_table_exists()` guard in `server.py`
- JSON models (`JsonExportRequest`, `QueryJsonExportRequest`) are structurally identical to the CSV models today but kept separate to allow future JSON-specific options (e.g., `pretty_print: bool`, JSONL format)
- The `Content-Disposition` header is parsed client-side to extract the server-provided filename before falling back to a default, matching the table-JSON endpoint behavior
- No new Python dependencies — `json` is stdlib, `pandas` was already present

## How to Use

1. Upload a CSV, JSON, or JSONL file through the upload button to load a table.
2. To export a full table: click the **⬇ JSON** button on the table card header (next to the CSV download icon).
3. To export query results: run a natural language query, then click **⬇ JSON** in the results toolbar (next to the **Export** CSV button).
4. The browser downloads a `.json` file containing a pretty-printed JSON array of objects, one object per row.

## Configuration

No configuration required. The feature uses the same SQLite database (`db/database.db`) and security validation (`validate_identifier`, `check_table_exists`) as the existing CSV endpoints.

## Testing

Run the server unit tests:

```bash
cd app/server && uv run pytest tests/test_export_utils.py -v
```

The `TestJsonExportUtils` class covers:
- Empty data → `[]`
- Basic rows with correct keys and values
- Type round-trip (int, float, str, bool, None)
- Unicode (emoji, CJK, accented characters)
- Special characters (quotes, newlines, tabs)
- Table read from SQLite (in-memory DB)
- Empty table
- Non-existent table raises `ValueError`

## Notes

- `default=str` in `json.dumps` converts non-JSON-serializable types (e.g., `datetime.date`, `decimal.Decimal`) to their string representation rather than raising an error.
- Future enhancement: expose `pretty_print: bool = True` on `QueryJsonExportRequest` / `JsonExportRequest` to allow compact JSON for large exports.
- Future enhancement: JSONL (one object per line) format — `file_processor.py` already supports JSONL upload; export could mirror that.
- All existing CSV export functionality is unaffected.
