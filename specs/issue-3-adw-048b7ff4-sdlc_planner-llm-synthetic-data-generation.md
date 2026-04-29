# Feature: LLM-Based Synthetic Data Generation for Tables

## Metadata
issue_number: `3`
adw_id: `048b7ff4`
issue_json: `{"number":3,"title":"Table Random Data Generation Based on Schema Using LLMs","body":"Generate synthetic data rows based on existing table patterns and schema\n\n/feature\n\nadw_sdlc_iso\n\nmodel_set heavy\n\nImplement a random data generation feature that creates synthetic data rows based on existing table patterns. Add a new button to the left of the CSV export button in the Available Tables section that triggers LLM-based data generation.\n\nImplementation details:\n\nAdd \"Generate Data\" button with appropriate icon next to each table (left of CSV export)\nWhen clicked, sample 10 random existing rows from the table\nSend sampled data + table schema to LLM with prompt to understand data patterns\nGenerate 10 new synthetic rows that match the patterns and constraints\nInsert generated rows into the table with proper validation\nShow success notification with count of rows added\nThe LLM should analyze:\n\nData types and formats for each column\nValue ranges and distributions\nRelationships between columns\nCommon patterns (emails, phone numbers, addresses, etc.)\nNullable vs required fields\nUpdate the UI to show loading state during generation and handle errors gracefully. The feature should use the existing LLM processor module and respect SQL security constraints.\n\nThis enhances testing and development by allowing users to quickly expand their datasets with realistic synthetic data."}`

## Feature Description
This feature adds LLM-powered synthetic data generation to the Natural Language SQL Interface. Each table in the "Available Tables" sidebar gets a new "Generate Data" button (placed to the left of the existing CSV export button). When clicked, the system samples 10 random rows from the table, sends the sample data along with the full table schema to the configured LLM (OpenAI or Anthropic), and asks it to generate 10 new synthetic rows that match the patterns, formats, value ranges, and constraints of the real data. The generated rows are inserted into the table using secure parameterized queries, and the user receives a success notification. The button shows a loading state during generation and handles errors gracefully.

## User Story
As a developer or data analyst  
I want to generate realistic synthetic rows for any loaded table with one click  
So that I can quickly expand small datasets for testing without manually crafting fake data

## Problem Statement
When users upload small datasets (a few rows), they often need more data to test queries, visualizations, or application features. Manually creating realistic fake rows is tedious and error-prone. There is currently no way within the application to expand an existing table with data that respects the schema, value patterns, and constraints of the original data.

## Solution Statement
Leverage the existing LLM integration (OpenAI/Anthropic dual-provider pattern) to analyze a sample of real table data and generate new synthetic rows that mirror the observed patterns. The feature is surfaced via a single button per table in the Available Tables section, follows all existing SQL security conventions for identifier validation and parameterized inserts, and reuses the established LLM processor module pattern.

## Relevant Files
Use these files to implement the feature:

- `app/server/core/llm_processor.py` — Add three new functions following the existing dual-provider pattern: `generate_synthetic_data_with_openai()`, `generate_synthetic_data_with_anthropic()`, and `generate_synthetic_data()` router function
- `app/server/core/data_models.py` — Add `GenerateDataRequest` (table_name, row_count) and `GenerateDataResponse` (inserted_count, sample_rows, error) Pydantic models
- `app/server/core/sql_security.py` — Use existing `validate_identifier`, `escape_identifier`, `check_table_exists`, and `execute_query_safely` functions; no changes needed
- `app/server/server.py` — Add `POST /api/generate-data` endpoint following existing endpoint patterns; import new models and synthetic data function
- `app/client/src/api/client.ts` — Add `generateTableData(tableName: string): Promise<GenerateDataResponse>` method using existing POST + error handling pattern
- `app/client/src/types.d.ts` — Add `GenerateDataRequest` and `GenerateDataResponse` TypeScript interfaces
- `app/client/src/main.ts` — Add generate data button in `displayTables()` to the left of the export button; add loading state and success/error notification display
- `app/client/src/style.css` — Add styling for the generate data button (`.generate-data-button`) following the existing `export-button` style pattern
- `app/server/tests/core/test_synthetic_data.py` — New unit tests for the synthetic data generator functions
- `app_docs/feature-490eb6b5-one-click-table-exports.md` — Reference: understand export button placement and button styling conventions
- `app_docs/feature-4c768184-model-upgrades.md` — Reference: current model names (gpt-4.1-2025-04-14, claude-sonnet-4-0) and LLM pattern conventions
- `.claude/commands/test_e2e.md` — Read to understand how to structure the E2E test file
- `.claude/commands/e2e/test_basic_query.md` — Read as reference example for E2E test format

### New Files
- `app/server/core/synthetic_data_generator.py` — New module that orchestrates: sampling existing rows, building the LLM prompt, calling the LLM, parsing the JSON response, validating column names against schema, and executing parameterized INSERTs
- `app/server/tests/core/test_synthetic_data.py` — Unit tests covering: sampling, INSERT logic, JSON parsing, error handling, and security validation
- `.claude/commands/e2e/test_synthetic_data_generation.md` — E2E test file validating the full generate-data flow in the browser

## Implementation Plan

### Phase 1: Foundation
Add Pydantic data models and the backend LLM functions following established patterns. No UI changes yet.

### Phase 2: Core Implementation
Build the `synthetic_data_generator.py` module with row sampling, LLM prompt construction, response parsing, schema validation, and secure INSERT execution. Add the FastAPI endpoint. Write unit tests.

### Phase 3: Integration
Wire the new API method into the TypeScript API client, add the generate data button to the table display, implement loading/success/error states in the UI, add button CSS, and create the E2E test file.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add Pydantic Models to data_models.py
- Open `app/server/core/data_models.py`
- Add `GenerateDataRequest` model with fields:
  - `table_name: str` (Field with description)
  - `row_count: int = Field(default=10, ge=1, le=100, description="Number of synthetic rows to generate")`
- Add `GenerateDataResponse` model with fields:
  - `table_name: str`
  - `inserted_count: int`
  - `sample_rows: List[Dict[str, Any]]` (the generated rows that were inserted, for display)
  - `error: Optional[str] = None`

### Step 2: Add LLM Functions to llm_processor.py
- Open `app/server/core/llm_processor.py`
- Add `generate_synthetic_data_with_openai(table_name: str, schema_info: Dict[str, Any], sample_rows: List[Dict[str, Any]], row_count: int) -> List[Dict[str, Any]]`:
  - Build a prompt that includes the table schema (column names + types + nullable), the sample rows formatted as JSON, and asks the LLM to return exactly `row_count` new synthetic rows as a JSON array of objects
  - Instruct the LLM to: match data formats (emails, phone numbers, dates, IDs), respect value ranges from the samples, keep relationships between columns coherent, return ONLY a valid JSON array with no extra text or markdown
  - Use model `gpt-4.1-2025-04-14`, `temperature=0.8`, `max_tokens=2000`
  - Parse the JSON response (strip markdown code fences if present) and return the list of row dicts
- Add `generate_synthetic_data_with_anthropic(table_name: str, schema_info: Dict[str, Any], sample_rows: List[Dict[str, Any]], row_count: int) -> List[Dict[str, Any]]`:
  - Same prompt and logic using `claude-sonnet-4-0`, `temperature=0.8`, `max_tokens=2000`
- Add router `generate_synthetic_data(table_name, schema_info, sample_rows, row_count) -> List[Dict[str, Any]]`:
  - Same priority pattern as existing: OpenAI key first, then Anthropic, else raise ValueError

### Step 3: Create synthetic_data_generator.py Module
- Create `app/server/core/synthetic_data_generator.py`
- Add function `sample_table_rows(conn: sqlite3.Connection, table_name: str, limit: int = 10) -> List[Dict[str, Any]]`:
  - Use `execute_query_safely` with `SELECT * FROM {table} ORDER BY RANDOM() LIMIT ?`, with `identifier_params={'table': table_name}` and `params=(limit,)`
  - Return rows as list of dicts (column name → value)
- Add function `insert_synthetic_rows(conn: sqlite3.Connection, table_name: str, rows: List[Dict[str, Any]], schema_columns: List[str]) -> int`:
  - For each row, filter keys to only those present in `schema_columns` (skip unknown or auto-generated columns like `index`)
  - Validate `table_name` with `validate_identifier`
  - Build a parameterized INSERT: escape each column name with `escape_identifier`, use `?` placeholders for values
  - Execute with `conn.execute()` and `conn.commit()`
  - Return count of successfully inserted rows
- Add main orchestration function `generate_and_insert_data(table_name: str, row_count: int = 10) -> Tuple[int, List[Dict[str, Any]]]`:
  - Open DB connection (following pattern in server.py)
  - Call `check_table_exists(conn, table_name)` to validate table exists
  - Call `sample_table_rows(conn, table_name, limit=10)` to get sample
  - Get schema info via existing `get_database_schema()` function
  - Call `generate_synthetic_data(table_name, schema_info, sample_rows, row_count)` from llm_processor
  - Validate returned rows are a list of dicts
  - Get schema columns (list of column names excluding 'index' auto-column)
  - Call `insert_synthetic_rows(conn, table_name, generated_rows, schema_columns)`
  - Return `(inserted_count, generated_rows)`

### Step 4: Add API Endpoint to server.py
- Open `app/server/server.py`
- Import `GenerateDataRequest` and `GenerateDataResponse` from `core.data_models`
- Import `generate_and_insert_data` from `core.synthetic_data_generator`
- Add endpoint `POST /api/generate-data`:
  ```python
  @app.post("/api/generate-data", response_model=GenerateDataResponse)
  async def generate_table_data(request: GenerateDataRequest) -> GenerateDataResponse:
  ```
  - Validate `request.table_name` with `validate_identifier`
  - Call `generate_and_insert_data(request.table_name, request.row_count)`
  - Return `GenerateDataResponse(table_name=request.table_name, inserted_count=count, sample_rows=rows)`
  - Catch `SQLSecurityError` → return response with error field
  - Catch `ValueError` (no LLM key) → return response with error field
  - Catch generic `Exception` → log full traceback, return response with error field

### Step 5: Create E2E Test File
- Read `.claude/commands/test_e2e.md` to understand the required format
- Read `.claude/commands/e2e/test_basic_query.md` as a format reference
- Create `.claude/commands/e2e/test_synthetic_data_generation.md` with:
  - User story: as a user I want to generate synthetic data for a table so I can expand my dataset
  - Test steps:
    1. Navigate to Application URL and take initial screenshot
    2. Upload a small CSV file (use the existing sample data or upload one with ~5 rows)
    3. Verify the table appears in the Available Tables section
    4. Verify the "Generate Data" button (with sparkle icon) is visible to the left of the CSV export button for that table
    5. Note the initial row count shown in the table info
    6. Click the "Generate Data" button
    7. Verify the button shows a loading state (disabled, text changes)
    8. Wait for generation to complete
    9. Take a screenshot of the success notification
    10. Verify the table row count has increased by 10
    11. Take a screenshot of the updated table info
    12. Run a query to verify the new rows exist in the database
    13. Take a screenshot of the query results showing the new rows
  - Success criteria: button visible, loading state shown, success notification shown, row count increases, new rows queryable

### Step 6: Add TypeScript Types
- Open `app/client/src/types.d.ts`
- Add interface `GenerateDataRequest`:
  - `table_name: string`
  - `row_count?: number`
- Add interface `GenerateDataResponse`:
  - `table_name: string`
  - `inserted_count: number`
  - `sample_rows: Record<string, any>[]`
  - `error?: string`

### Step 7: Add API Method to client.ts
- Open `app/client/src/api/client.ts`
- Add method `generateTableData(tableName: string): Promise<GenerateDataResponse>`:
  - POST to `/api/generate-data` with body `{ table_name: tableName, row_count: 10 }`
  - Follow existing error handling pattern: check `!response.ok`, parse JSON, return typed response
  - Throw on HTTP error with message from response body

### Step 8: Add Button and UI Logic to main.ts
- Open `app/client/src/main.ts`
- In `displayTables()`, inside the `tables.forEach` block, before creating the `exportButton`:
  - Create `generateButton` element:
    - `className = 'generate-data-button'`
    - `innerHTML = '✨'` (sparkle/magic wand emoji as icon, consistent with existing emoji UI patterns)
    - `title = 'Generate synthetic data rows using AI'`
  - Add `onclick` handler:
    - Disable the button and set `innerHTML = '⏳'` for loading state
    - Call `await api.generateTableData(table.name)`
    - On success: re-enable button, reset `innerHTML = '✨'`, call `loadDatabaseSchema()` to refresh row count, show success notification (e.g., "Generated X new rows for {tableName}")
    - On error: re-enable button, reset icon, call `displayError('Failed to generate data: ' + error.message)`
    - Wrap in try/catch
  - Prepend `generateButton` to `buttonsContainer` before `exportButton` (so order is: [Generate] [Export CSV] [Remove ×])
- Add a `displaySuccess(message: string)` helper function if it does not already exist (following the pattern of `displayError`)

### Step 9: Add CSS Styling
- Open `app/client/src/style.css`
- Add `.generate-data-button` styles following the `.export-button` / `.table-export-button` pattern:
  - Similar size and shape to export button
  - Distinct visual appearance (e.g., light purple or teal background to differentiate from export)
  - Hover and disabled states
  - Consistent border-radius and padding with sibling buttons

### Step 10: Write Unit Tests
- Create `app/server/tests/core/test_synthetic_data.py`
- Test `sample_table_rows`:
  - Verifies correct SQL is used (mock execute_query_safely)
  - Returns list of dicts with correct keys
- Test `insert_synthetic_rows`:
  - Inserts with correct parameterized query
  - Skips unknown columns not in schema
  - Returns correct inserted count
  - Validates table_name via validate_identifier
- Test `generate_and_insert_data` (integration-style with in-memory SQLite):
  - Creates a test table, calls function, verifies row count increases
  - Handles missing LLM key gracefully (mock LLM function)
- Test the API endpoint:
  - POST /api/generate-data with valid table_name returns 200 with inserted_count
  - POST with invalid table_name returns response with error field
  - Mock `generate_and_insert_data` for isolation

### Step 11: Validate
- Run all validation commands listed in the Validation Commands section

## Testing Strategy

### Unit Tests
- `test_sample_table_rows`: verifies RANDOM() LIMIT query is used, rows returned as dicts
- `test_insert_synthetic_rows_filters_unknown_columns`: only schema columns are inserted
- `test_insert_synthetic_rows_uses_parameterized_query`: no string interpolation of values
- `test_generate_and_insert_data_with_mock_llm`: end-to-end with in-memory SQLite and mocked LLM call
- `test_api_endpoint_generate_data_success`: FastAPI TestClient POST returns 200
- `test_api_endpoint_invalid_table_returns_error`: SQL keyword table name returns error field
- `test_llm_functions_parse_json_with_code_fences`: ensures markdown stripping works

### Edge Cases
- Table has only 1 existing row (sample with fewer rows than limit)
- Table has no rows (empty table) — LLM must rely on schema alone; send schema-only prompt
- LLM returns JSON with extra columns not in schema — filtered by insert_synthetic_rows
- LLM returns malformed JSON — caught and returned as error response
- No LLM API key configured — graceful error message shown to user
- Table name that passes validation but has no rows edge case
- Row values that include None/null for nullable columns
- Very long string values — no truncation, insert as-is

## Acceptance Criteria
- A "Generate Data" button (✨ icon) appears for each table in the Available Tables section, to the left of the CSV export button
- Clicking the button disables it and shows ⏳ loading indicator while generation is in progress
- After generation completes successfully, the table row count in the sidebar updates (increased by ~10)
- A success notification is shown indicating how many rows were inserted
- On error (no API key, malformed LLM response, security violation), the button re-enables and an error notification is shown
- Generated rows match the data patterns of the original table (correct formats, value ranges)
- All existing tests continue to pass with zero regressions
- The new `/api/generate-data` endpoint validates table names using the existing SQL security module
- INSERT statements use parameterized queries (no SQL injection risk)
- The feature works with both OpenAI and Anthropic API keys using the existing priority routing

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_synthetic_data_generation.md` to validate the end-to-end flow in the browser
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run TypeScript type check to validate no type errors
- `cd app/client && bun run build` - Run frontend build to validate the feature builds without errors

## Notes
- The LLM prompt must explicitly instruct the model to return ONLY a valid JSON array (no markdown fences, no explanations) since the response is parsed programmatically; include JSON stripping as a safety net identical to the existing SQL markdown cleanup in llm_processor.py
- The `index` column (SQLite rowid alias added by pandas `to_sql`) should be excluded from the INSERT column list since it is auto-incremented; filter any column named `index` from the schema columns before building the INSERT
- Temperature 0.8 is appropriate for synthetic data (matches the random query generator) to get variety in generated values
- The button placement follows the existing convention established in `feature-490eb6b5`: new action buttons are prepended to the buttons container to appear to the left of existing controls
- No new Python packages are required — openai and anthropic SDKs are already installed; json parsing uses the standard library
- For tables with zero existing rows, modify the prompt to ask the LLM to generate rows based purely on the schema (column names and types), since there are no sample rows to learn patterns from
- Row count is capped at 100 via the Pydantic `le=100` validator to prevent runaway LLM token usage and very large INSERTs
- The `displaySuccess()` helper should follow the same DOM pattern as the existing `displayError()` function for visual consistency
