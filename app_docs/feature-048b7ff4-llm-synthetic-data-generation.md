# LLM Synthetic Data Generation for Tables

**ADW ID:** 048b7ff4
**Date:** 2026-04-29
**Specification:** specs/issue-3-adw-048b7ff4-sdlc_planner-llm-synthetic-data-generation.md

## Overview

This feature adds a one-click AI-powered synthetic data generation capability to the Natural Language SQL Interface. Each table in the Available Tables sidebar gains a "Generate Data" button (✨) that samples existing rows, sends them with the schema to the configured LLM (OpenAI or Anthropic), and inserts 10 realistic synthetic rows that match the table's patterns and constraints.

## What Was Built

- **Generate Data button (✨)** — appears per-table in the Available Tables sidebar, to the left of the CSV export button
- **Loading state** — button disables and shows ⏳ while generation is in progress
- **Success notification** — auto-dismissing banner displays the count of inserted rows after completion
- **Error handling** — graceful display if no LLM key is configured, if the LLM returns malformed JSON, or if a security violation occurs
- **`POST /api/generate-data` endpoint** — FastAPI endpoint that validates the table name, invokes the synthetic data pipeline, and returns the inserted count plus generated rows
- **`synthetic_data_generator.py` module** — orchestrates row sampling, LLM call, JSON parsing, schema validation, and secure parameterized INSERTs
- **Dual-provider LLM support** — OpenAI (`gpt-4.1-2025-04-14`) preferred; falls back to Anthropic (`claude-sonnet-4-0`) using the existing priority routing pattern
- **Unit test suite** — 331-line test file covering sampling, insert logic, JSON parsing, security validation, and API endpoint behavior

## Technical Implementation

### Files Modified

- `app/server/core/llm_processor.py`: Added `_build_synthetic_data_prompt()`, `_parse_json_response()`, `generate_synthetic_data_with_openai()`, `generate_synthetic_data_with_anthropic()`, and `generate_synthetic_data()` router following the existing dual-provider pattern
- `app/server/core/data_models.py`: Added `GenerateDataRequest` (table_name, row_count 1–100) and `GenerateDataResponse` (table_name, inserted_count, sample_rows, error) Pydantic models
- `app/server/server.py`: Added `POST /api/generate-data` endpoint; imports new models and `generate_and_insert_data`
- `app/client/src/api/client.ts`: Added `generateTableData(tableName)` method — POSTs to `/generate-data` with `row_count: 10`, follows existing error handling pattern
- `app/client/src/types.d.ts`: Added `GenerateDataRequest` and `GenerateDataResponse` TypeScript interfaces
- `app/client/src/main.ts`: Added generate button creation and `displaySuccess()` helper in `displayTables()`; button is prepended so it renders to the left of export and remove buttons
- `app/client/src/style.css`: Added `.generate-data-button` styles with hover (purple tint) and disabled states matching sibling button conventions

### New Files

- `app/server/core/synthetic_data_generator.py`: Three functions — `sample_table_rows()` (random LIMIT query via `execute_query_safely`), `insert_synthetic_rows()` (parameterized INSERT, filters unknown columns, validates identifier), `generate_and_insert_data()` (main orchestrator)
- `app/server/tests/core/test_synthetic_data.py`: Unit tests for sampling, insert filtering, parameterized queries, API endpoint success/error, and JSON fence stripping

### Key Changes

- The LLM prompt instructs the model to return **only a raw JSON array** with no markdown fences; a `_parse_json_response()` safety net strips any accidental code fences before `json.loads()`
- The `index` column (SQLite rowid alias added by pandas `to_sql`) is explicitly excluded from the INSERT column list to avoid constraint violations on auto-incremented rows
- All table name inputs pass through `validate_identifier` and `escape_identifier` from the existing `sql_security` module — no SQL injection risk
- Row count is capped at 100 via the Pydantic `le=100` validator to prevent runaway LLM token usage
- `displaySuccess()` inserts a transient banner into the tables section (auto-removes after 4 s), mirroring the `displayError()` DOM pattern

## How to Use

1. Upload a CSV or JSON file via the "Upload Data" button to create a table
2. The table appears in the **Available Tables** sidebar with three buttons: ✨ Generate Data | Export CSV | ×
3. Click ✨ to trigger synthetic data generation — the button shows ⏳ while the LLM works
4. When complete, a green success banner appears (e.g., "Generated 10 new rows for 'customers'") and the row count in the sidebar refreshes automatically
5. Run a SQL query (e.g., `SELECT * FROM customers ORDER BY id DESC LIMIT 10`) to inspect the generated rows

## Configuration

No new configuration is required. The feature uses the same LLM API key environment variables already configured for SQL generation:

| Variable | Provider |
|---|---|
| `OPENAI_API_KEY` | OpenAI (`gpt-4.1-2025-04-14`) — checked first |
| `ANTHROPIC_API_KEY` | Anthropic (`claude-sonnet-4-0`) — fallback |

If neither key is set, clicking the button shows an error: "No LLM API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY".

## Testing

```bash
# Run server unit tests (includes test_synthetic_data.py)
cd app/server && uv run pytest

# TypeScript type check
cd app/client && bun tsc --noEmit

# Frontend build
cd app/client && bun run build
```

Key unit test cases in `app/server/tests/core/test_synthetic_data.py`:
- `TestSampleTableRows` — verifies RANDOM LIMIT query, correct column keys, empty table handling
- `TestInsertSyntheticRows` — verifies unknown column filtering, parameterized values, identifier validation
- `TestGenerateAndInsertData` — end-to-end with in-memory SQLite and mocked LLM call
- `TestApiEndpoint` — FastAPI TestClient POST returns 200 with `inserted_count`; invalid table name returns response with `error` field

## Notes

- For tables with **zero existing rows**, the LLM prompt omits sample data and asks the model to generate rows based purely on the schema (column names and types)
- Temperature 0.8 matches the existing random query generator setting, producing varied but realistic values
- The button placement (prepend to container) follows the convention established in `feature-490eb6b5`: new action buttons appear to the left of existing controls
- No new Python packages are needed — `openai` and `anthropic` SDKs are already installed; JSON parsing uses the standard library
