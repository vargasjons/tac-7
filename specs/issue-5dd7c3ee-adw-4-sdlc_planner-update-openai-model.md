# Chore: Update OpenAI Model to gpt-5.4-mini-2026-03-17

## Metadata
issue_number: `5dd7c3ee`
adw_id: `4`
issue_json: `{"number":4,"title":"Support better models for query generation","body":"chore - adw_sdlc_iso\n\nupdate openai model to use gpt-5.4-mini-2026-03-17"}`

## Chore Description
Update the OpenAI model used for SQL query generation and random query generation from `gpt-4.1-2025-04-14` to `gpt-5.4-mini-2026-03-17`. This affects both the LLM processor implementation and the corresponding test assertions that verify the model name used in API calls.

## Relevant Files
Use these files to resolve the chore:

- `app/server/core/llm_processor.py` — Contains two OpenAI API calls that hardcode the model name `gpt-4.1-2025-04-14`: one in `generate_sql_with_openai` (line 44) and one in `generate_random_query_with_openai` (line 184). Both must be updated to `gpt-5.4-mini-2026-03-17`.
- `app/server/tests/core/test_llm_processor.py` — Contains a test assertion on line 44 that verifies the model name passed to the OpenAI API is `gpt-4.1-2025-04-14`. Must be updated to `gpt-5.4-mini-2026-03-17` to match the new model.
- `app_docs/feature-4c768184-model-upgrades.md` — Existing documentation for model upgrades; referenced as context for how previous model changes were made.

## Step by Step Tasks

### Step 1: Update OpenAI model in llm_processor.py
- In `app/server/core/llm_processor.py`, find the `generate_sql_with_openai` function
- Replace `model="gpt-4.1-2025-04-14"` (line ~44) with `model="gpt-5.4-mini-2026-03-17"`
- Find the `generate_random_query_with_openai` function
- Replace `model="gpt-4.1-2025-04-14"` (line ~184) with `model="gpt-5.4-mini-2026-03-17"`

### Step 2: Update test assertion in test_llm_processor.py
- In `app/server/tests/core/test_llm_processor.py`, find `test_generate_sql_with_openai_success`
- Replace `assert call_args[1]['model'] == 'gpt-4.1-2025-04-14'` (line ~44) with `assert call_args[1]['model'] == 'gpt-5.4-mini-2026-03-17'`

### Step 3: Run validation commands
- Execute the validation commands below to confirm all tests pass with zero regressions.

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions

## Notes
- The Anthropic model (`claude-sonnet-4-0`) is not affected by this chore — only the OpenAI model changes.
- The model name `gpt-5.4-mini-2026-03-17` appears in exactly two places in `llm_processor.py` (SQL generation and random query generation) and one place in the test file.
- No API endpoint signatures, environment variables, or other configuration files need to change.
