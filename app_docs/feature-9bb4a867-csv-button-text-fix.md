# CSV Export Button Text Consistency Fix

**ADW ID:** 9bb4a867
**Date:** 2026-04-29
**Specification:** specs/issue-5-adw-9bb4a867-sdlc_planner-fix-csv-button-text.md

## Overview

Fixed an inconsistency where the CSV export button in the "Query Results" section displayed "📊 CSV Export" while the identical button in the "Available Tables" section correctly displayed "📊 CSV". The extra " Export" suffix was removed from the query results button so both buttons now show matching labels.

## What Was Built

- One-line fix in the client-side button label for the query results export button
- Both CSV export buttons now consistently display "📊 CSV"

## Technical Implementation

### Files Modified

- `app/client/src/main.ts`: Removed the " Export" suffix from the query results export button's `innerHTML` assignment

### Key Changes

- **Before**: ``exportButton.innerHTML = `${getDownloadIcon()} Export`;`` → rendered "📊 CSV Export"
- **After**: `exportButton.innerHTML = getDownloadIcon();` → renders "📊 CSV"
- The `getDownloadIcon()` helper (lines 16–18) already returns `'📊 CSV'`; the fix simply stops appending the redundant " Export" text
- The available tables export button at line 340 was already correct and unchanged
- No server-side changes were required; the bug was purely a client-side label issue

## How to Use

1. Start the application (server and client)
2. Upload a CSV file to create an available table
3. Observe the "📊 CSV" button in the "Available Tables" section
4. Execute a SQL query that returns results
5. Observe the "📊 CSV" button in the "Query Results" section — it now matches the Available Tables button

## Configuration

No configuration changes required.

## Testing

- Run the E2E test at `.claude/commands/e2e/test_csv_button_text.md` to verify both buttons display "📊 CSV"
- Run `cd app/client && bun tsc --noEmit` to confirm no TypeScript errors
- Run `cd app/client && bun run build` to confirm the build succeeds
- Run `cd app/server && uv run pytest` to confirm no server-side regressions

## Notes

- The root cause was an extra `" Export"` string appended during initial implementation of the query results button
- The available tables button was always correct and serves as the source of truth for the desired button text
