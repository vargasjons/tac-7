# Bug: "CSV" texts don't match

## Metadata
issue_number: `5`
adw_id: `9bb4a867`
issue_json: `{"number":5,"title":"\"CSV\" texts don't match","body":"bug - adw_patch_iso - Under available tables section the csv export button has the correct \"CSV\".\nUpdate the query result section csv export button text should match this."}`

## Bug Description
The CSV export button in the "Query Results" section displays "📊 CSV Export" while the CSV export button in the "Available Tables" section correctly displays "📊 CSV". The two export buttons use inconsistent text labels, with the query result button appending the extra word " Export" after the shared `getDownloadIcon()` return value.

**Actual behavior**: Query results export button shows "📊 CSV Export"
**Expected behavior**: Query results export button should show "📊 CSV" (matching the available tables export button)

## Problem Statement
In `app/client/src/main.ts`, the query results export button (line 242) constructs its label using a template literal that appends " Export" to the icon: `` `${getDownloadIcon()} Export` ``. The available tables export button (line 340) simply calls `getDownloadIcon()` directly. This inconsistency causes mismatched button labels between the two sections.

## Solution Statement
Remove the " Export" suffix from the query results export button's `innerHTML` assignment so it uses `getDownloadIcon()` directly, matching the available tables section button text.

## Steps to Reproduce
1. Start the application (server and client)
2. Upload a CSV file to create an available table
3. Observe the CSV export button label in the "Available Tables" section — it shows "📊 CSV"
4. Execute a SQL query that returns results
5. Observe the CSV export button label in the "Query Results" section — it shows "📊 CSV Export"
6. Note the mismatch between the two button labels

## Root Cause Analysis
In `app/client/src/main.ts`:

- `getDownloadIcon()` (line 16-18) returns the string `'📊 CSV'`
- **Available Tables button** (line 340): `exportButton.innerHTML = getDownloadIcon();` → renders "📊 CSV" ✅
- **Query Results button** (line 242): ``exportButton.innerHTML = `${getDownloadIcon()} Export`;`` → renders "📊 CSV Export" ❌

The query results button was given an extra " Export" label during implementation, creating the inconsistency. The fix is a one-line change.

## Relevant Files
Use these files to fix the bug:

- `app/client/src/main.ts` — Contains both export button implementations. The query results export button at line 242 appends " Export" to `getDownloadIcon()`, causing the mismatch with the available tables button at line 340.
- `app_docs/feature-490eb6b5-one-click-table-exports.md` — Feature documentation for the CSV export feature, describing the intended button behavior for both sections.
- `.claude/commands/e2e/test_basic_query.md` — Reference for understanding how to create E2E test files.
- `.claude/commands/test_e2e.md` — Instructions for running E2E tests.

### New Files
- `.claude/commands/e2e/test_csv_button_text.md` — New E2E test file to validate that both CSV export buttons display consistent text.

## Step by Step Tasks

### 1. Fix the query results export button text in main.ts
- Open `app/client/src/main.ts`
- Locate line 242: ``exportButton.innerHTML = `${getDownloadIcon()} Export`;``
- Change it to: `exportButton.innerHTML = getDownloadIcon();`
- This makes the query results export button text match the available tables export button text ("📊 CSV")

### 2. Create an E2E test file to validate the fix
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand how to create an E2E test file
- Create a new E2E test file at `.claude/commands/e2e/test_csv_button_text.md` that:
  - Navigates to the application
  - Uploads a CSV file to create an available table
  - Verifies the available tables export button text is "📊 CSV"
  - Executes a SQL query that returns results
  - Verifies the query results export button text is also "📊 CSV" (not "📊 CSV Export")
  - Takes a screenshot showing both buttons with matching text

### 3. Run Validation Commands
- Execute all validation commands listed in the Validation Commands section to confirm the fix works and no regressions are introduced.

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute your new E2E `.claude/commands/e2e/test_csv_button_text.md` test file to validate this functionality works.
- `cd app/server && uv run pytest` - Run server tests to validate the bug is fixed with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the bug is fixed with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the bug is fixed with zero regressions

## Notes
- The change is a single-line fix in `app/client/src/main.ts` (line 242).
- No server-side changes are needed; the bug is purely in the client-side button label.
- The `getDownloadIcon()` helper function already returns the correct text "📊 CSV" — both buttons just need to use it consistently without additional appended text.
- Per `app_docs/feature-490eb6b5-one-click-table-exports.md`, the query results button was originally documented as showing "⬇ Export", but the current implementation uses "📊 CSV" for the available tables button — the source of truth for the desired text is the available tables button as stated in the bug report.
