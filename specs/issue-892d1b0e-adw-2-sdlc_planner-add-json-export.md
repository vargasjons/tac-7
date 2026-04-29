# Feature: Add JSON Export

## Metadata
issue_number: `892d1b0e`
adw_id: `2`
issue_json: `{"number":2,"title":"Add json export","body":"feature - adw_sdlc_iso - update to support table and query result 'json' export. Similar to our csv export but specifically built for json export."}`

## Feature Description
Add JSON export functionality to the Natural Language SQL Interface application, allowing users to download table data and query results as formatted JSON files. This mirrors the existing CSV export feature but outputs valid, human-readable JSON instead of comma-separated values. JSON export is valuable for users who need to consume data programmatically, integrate results with other APIs, or prefer a structured format that preserves data types.

## User Story
As a user of the SQL query interface,
I want to export table data and query results as JSON files,
So that I can consume structured data programmatically, integrate with APIs, or share results in a universally-readable format that preserves data types.

## Problem Statement
The application currently supports CSV export for both full tables and query results. However, CSV is a lossy format that does not distinguish between data types (all values become strings) and requires additional parsing to work with programmatically. Users who need to pass query results to other systems or want to preserve numeric and boolean types have no native export option for this.

## Solution Statement
Add two new backend API endpoints (`POST /api/export/table-json` and `POST /api/export/query-json`) backed by utility functions in `export_utils.py` that serialize data to formatted JSON. Add corresponding client API functions and UI export buttons alongside the existing CSV buttons, following the exact same pattern already established for CSV exports.

## Relevant Files
Use these files to implement the feature:

- **`app/server/core/export_utils.py`** — Add `generate_json_from_data()` and `generate_json_from_table()` utility functions, mirroring the existing CSV utility functions.
- **`app/server/server.py`** — Add `POST /api/export/table-json` and `POST /api/export/query-json` FastAPI endpoints, following the same structure as the existing CSV export endpoints.
- **`app/server/core/data_models.py`** — Add `JsonExportRequest` and `QueryJsonExportRequest` Pydantic models (or reuse existing models if they are identical in shape).
- **`app/server/tests/test_export_utils.py`** — Add unit tests for the new JSON utility functions, mirroring the existing CSV tests.
- **`app/client/src/api/client.ts`** — Add `exportTableAsJson()` and `exportQueryResultsAsJson()` API client functions, following the existing CSV download pattern.
- **`app/client/src/main.ts`** — Add JSON export buttons to the query results toolbar and to each table card, positioned alongside the existing CSV export buttons.
- **`app/client/src/types.d.ts`** — Review for any type updates needed for the new export actions.
- **`.claude/commands/test_e2e.md`** — Read to understand how to create an E2E test file.
- **`.claude/commands/e2e/test_basic_query.md`** — Read as a reference E2E test format example.
- **`.claude/commands/e2e/test_export_functionality.md`** — Read as the primary reference for the JSON export E2E test format.

### New Files
- **`.claude/commands/e2e/test_json_export_functionality.md`** — New E2E test file that validates JSON export for both table and query result exports, including file download verification and JSON content validation.

## Implementation Plan

### Phase 1: Foundation
Add the core utility functions and Pydantic models needed before the endpoints and UI can be built. This ensures the data layer is correct and testable in isolation.

### Phase 2: Core Implementation
Implement the FastAPI endpoints and the client-side API functions. Add unit tests. Ensure the download flow (blob → URL → anchor click → cleanup) works identically to CSV.

### Phase 3: Integration
Wire the new client functions to new UI buttons in `main.ts`, positioned logically next to the existing CSV buttons. Create the E2E test file and run all validation commands.

## Step by Step Tasks

### Step 1: Add JSON utility functions to `export_utils.py`
- In `app/server/core/export_utils.py`, add `generate_json_from_data(data: List[Dict], columns: List[str]) -> bytes` that serializes the data list to a pretty-printed JSON array (indent=2) and returns UTF-8 encoded bytes.
- Add `generate_json_from_table(conn: sqlite3.Connection, table_name: str) -> bytes` that reads the full table into a pandas DataFrame, converts it to a list of dicts via `df.to_dict(orient='records')`, and serializes with `json.dumps(..., indent=2, default=str)` (using `default=str` to handle non-serializable types like dates).
- Import `json` at the top of the file if not already imported.

### Step 2: Add Pydantic models to `data_models.py`
- In `app/server/core/data_models.py`, add `JsonExportRequest(BaseModel)` with field `table_name: str` (same shape as `ExportRequest`, reuse if identical, otherwise add separately for clarity).
- Add `QueryJsonExportRequest(BaseModel)` with fields `data: List[Dict[str, Any]]` and `columns: List[str]` (same shape as `QueryExportRequest`).
- If models are identical in shape to existing ones, document clearly that they are intentionally separate for future divergence (e.g., JSON-specific options like pretty-print indent level).

### Step 3: Add API endpoints to `server.py`
- In `app/server/server.py`, add `POST /api/export/table-json` endpoint that:
  - Accepts `JsonExportRequest` body
  - Validates `table_name` with `sql_security.validate_identifier()`
  - Checks table existence with `sql_security.check_table_exists()`
  - Calls `generate_json_from_table()` from `export_utils`
  - Returns a `Response` with `media_type="application/json"` and `Content-Disposition: attachment; filename="{table_name}.json"`
- Add `POST /api/export/query-json` endpoint that:
  - Accepts `QueryJsonExportRequest` body
  - Calls `generate_json_from_data()` from `export_utils`
  - Returns a `Response` with `media_type="application/json"` and `Content-Disposition: attachment; filename="query_results.json"`

### Step 4: Add unit tests for JSON utility functions
- In `app/server/tests/test_export_utils.py`, add a test class or grouped tests for JSON export mirroring the existing CSV tests:
  - `test_generate_json_from_data_empty()` — empty data returns `[]` JSON
  - `test_generate_json_from_data_basic()` — verifies column names and values are correct
  - `test_generate_json_from_data_types()` — int, float, string, bool, None round-trip correctly
  - `test_generate_json_from_data_unicode()` — emoji, Chinese characters, accented letters survive
  - `test_generate_json_from_table_basic()` — reads a SQLite table and returns correct JSON
  - `test_generate_json_from_table_empty()` — empty table returns `[]`
  - `test_generate_json_from_data_special_chars()` — strings containing `"`, `\n`, `\t` are properly escaped in the JSON output
- Run `cd app/server && uv run pytest tests/test_export_utils.py -v` to confirm all tests pass.

### Step 5: Create E2E test file
- Read `.claude/commands/test_e2e.md` to understand the E2E test runner format.
- Read `.claude/commands/e2e/test_export_functionality.md` as the primary reference.
- Create `.claude/commands/e2e/test_json_export_functionality.md` with the following test steps:
  1. Navigate to the application and verify it loads.
  2. Upload or select a sample dataset.
  3. Run a natural language query that returns results.
  4. Click the "JSON Export" button on the query results panel.
  5. Verify a `.json` file is downloaded.
  6. Verify the downloaded file is valid JSON (array of objects).
  7. Verify column names appear as keys in each JSON object.
  8. Click the "JSON Export" button on a table card.
  9. Verify a `.json` file named after the table is downloaded.
  10. Take screenshots at key steps to prove functionality.

### Step 6: Add client API functions to `api/client.ts`
- In `app/client/src/api/client.ts`, add `exportTableAsJson(tableName: string): Promise<void>` that:
  - POSTs to `/api/export/table-json` with body `{ table_name: tableName }`
  - Extracts the filename from the `Content-Disposition` response header (default: `${tableName}.json`)
  - Creates a Blob with type `application/json`, creates an object URL, triggers download via an anchor click, and revokes the URL.
- Add `exportQueryResultsAsJson(data: Record<string, unknown>[], columns: string[]): Promise<void>` that:
  - POSTs to `/api/export/query-json` with body `{ data, columns }`
  - Follows the same blob-download pattern with filename `query_results.json`.

### Step 7: Add JSON export buttons to `main.ts`
- In `app/client/src/main.ts`, locate where the CSV export button is rendered for query results and add a sibling "JSON Export" button immediately after it, calling `exportQueryResultsAsJson()`.
- Locate where the CSV export button is rendered for each table card and add a sibling "JSON Export" button calling `exportTableAsJson(tableName)`.
- Match the existing button styling (class names, icon, label pattern). Use a label like `⬇ JSON` or `Export JSON` consistent with the existing CSV button label style.
- Ensure the button is only shown when data is available (same condition as the CSV button).

### Step 8: Run validation commands
- Execute all validation commands listed in the `Validation Commands` section below in order.
- Fix any failures before marking the feature complete.

## Testing Strategy

### Unit Tests
- Mirror all existing CSV export tests with JSON-specific assertions.
- Key assertions: valid JSON structure (`json.loads()` succeeds), array of objects format, correct column-to-key mapping, correct data type preservation (int stays int, bool stays bool, None becomes null).
- Test edge cases: empty dataset, single row, Unicode, special characters within strings.

### Edge Cases
- Empty query results → should produce `[]` JSON array (not an error)
- Empty table → should produce `[]` JSON array
- Table with non-serializable types (e.g., Python `datetime`) → `default=str` in `json.dumps` ensures graceful handling
- Very large result sets → pandas handles chunking; JSON may be large but should not crash
- Column names with special characters → verified via `validate_identifier()` on table names; query column names come from the DB schema
- Null/None values → serialize as JSON `null`
- Numeric strings that look like numbers → preserve as strings if they are strings in the DB

## Acceptance Criteria
- [ ] `POST /api/export/table-json` returns a valid JSON file download with the table name as filename when given a valid table name.
- [ ] `POST /api/export/query-json` returns a valid JSON file download named `query_results.json` when given data and columns.
- [ ] Both endpoints return appropriate errors for invalid/non-existent table names (consistent with CSV endpoint behavior).
- [ ] Client-side "JSON Export" button appears on query results panel and triggers download of `query_results.json`.
- [ ] Client-side "JSON Export" button appears on each table card and triggers download of `{tableName}.json`.
- [ ] Downloaded JSON files are valid JSON arrays of objects.
- [ ] Data types are preserved: integers remain integers, booleans remain booleans, nulls become JSON null.
- [ ] All existing CSV export functionality is unaffected (zero regressions).
- [ ] All new unit tests pass.
- [ ] `uv run pytest` passes with zero failures.
- [ ] `bun tsc --noEmit` passes with zero type errors.
- [ ] `bun run build` completes successfully.
- [ ] E2E test validates the full JSON export flow with screenshots.

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_json_export_functionality.md` to validate JSON export functionality end-to-end with screenshots.
- `cd app/server && uv run pytest` — Run all server tests to validate the feature works with zero regressions.
- `cd app/client && bun tsc --noEmit` — Run TypeScript type checking to validate the feature works with zero regressions.
- `cd app/client && bun run build` — Run frontend build to validate the feature works with zero regressions.

## Notes
- The `default=str` argument in `json.dumps()` is important for handling SQLite types that Python's `json` module cannot serialize by default (e.g., `datetime.date`, `decimal.Decimal`). This matches user expectations: non-standard types become their string representation.
- JSON export does not require any new Python dependencies — `json` is part of the standard library and `pandas` is already installed.
- Future enhancement: could expose a `?indent` query parameter or request body field to allow compact (no indentation) vs. pretty-printed JSON, useful for very large exports.
- Future enhancement: JSONL (JSON Lines) format — one JSON object per line — is already supported by `file_processor.py` for uploads; could be offered as an export option too.
- The existing `ExportRequest` and `QueryExportRequest` models in `data_models.py` have identical shapes to what JSON export needs. They can be reused directly, or separate models can be created for clarity. Prefer separate models to allow future divergence (e.g., a `pretty_print: bool = True` field for JSON-specific options).
