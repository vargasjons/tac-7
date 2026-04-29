# OpenAI Model Update to gpt-5.4-mini-2026-03-17

**ADW ID:** 4
**Date:** 2026-04-29
**Specification:** specs/issue-5dd7c3ee-adw-4-sdlc_planner-update-openai-model.md

## Overview

Updated the OpenAI model used for SQL query generation and random query generation from `gpt-4.1-2025-04-14` to `gpt-5.4-mini-2026-03-17`. This is a targeted model version bump affecting only the OpenAI integration; the Anthropic model (`claude-sonnet-4-0`) remains unchanged.

## What Was Built

- Updated OpenAI model in `generate_sql_with_openai` to `gpt-5.4-mini-2026-03-17`
- Updated OpenAI model in `generate_random_query_with_openai` to `gpt-5.4-mini-2026-03-17`
- Updated test assertion to verify the new model name is passed to the API

## Technical Implementation

### Files Modified

- `app/server/core/llm_processor.py`: Changed `model="gpt-4.1-2025-04-14"` to `model="gpt-5.4-mini-2026-03-17"` in two places — `generate_sql_with_openai` (line ~44) and `generate_random_query_with_openai` (line ~184)
- `app/server/tests/core/test_llm_processor.py`: Updated model name assertion in `test_generate_sql_with_openai_success` to match the new model

### Key Changes

- OpenAI model bumped from `gpt-4.1-2025-04-14` to `gpt-5.4-mini-2026-03-17` in both OpenAI API call sites
- Test assertion updated to `'gpt-5.4-mini-2026-03-17'` so CI continues to validate the correct model is used
- No changes to function signatures, API endpoints, environment variables, or the Anthropic integration

## How to Use

The change is transparent to end users. The application automatically uses the new model for:

1. Converting natural language queries to SQL via the OpenAI path
2. Generating random/sample queries for exploration via the OpenAI path

## Configuration

No additional configuration required. The existing environment variable continues to apply:
- `OPENAI_API_KEY` — for OpenAI API access

## Testing

```bash
cd app/server && uv run pytest
```

## Notes

- Only the OpenAI model is affected; the Anthropic model (`claude-sonnet-4-0`) is unchanged.
- The model name appears in exactly two places in `llm_processor.py` and one place in the test file.
- No API endpoint signatures or environment variables changed.
