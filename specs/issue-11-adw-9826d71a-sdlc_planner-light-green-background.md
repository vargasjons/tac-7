# Chore: Light Green Background Color Update

## Metadata
issue_number: `11`
adw_id: `9826d71a`
issue_json: `{"number":11,"title":"Background color update","body":"/chore - adw_sdlc_ZTE_iso - update the background color to the equivalent light green color"}`

## Chore Description
Update the application's background color from the current light sky blue (`#E0F6FF`) to an equivalent light green color. The "equivalent" means maintaining the same visual weight, lightness, and saturation level but shifting the hue from blue to green. The direct equivalent of `#E0F6FF` in light green is `#E0FFE0` (same luminosity, green-dominant instead of blue-dominant). This follows the same single-variable CSS change pattern established by the previous background color updates in this project.

## Relevant Files

- `app/client/src/style.css` — The only file that needs to change. The `--background` CSS variable on line 9 controls the entire application's background color. Updating it here propagates to the `body` background and all sections that inherit from it.
- `app_docs/feature-6445fc8f-light-sky-blue-background.md` — Documents the previous background color change (off-white → light sky blue `#E0F6FF`), confirming the pattern and current value.
- `app_docs/feature-f055c4f8-off-white-background.md` — Documents the earlier background color change, confirming the single-variable CSS approach used throughout this project.

### New Files
- `app_docs/feature-9826d71a-light-green-background.md` — Feature documentation describing this background color update, following the existing `app_docs/` convention.

## Step by Step Tasks

### Step 1: Update the CSS background variable
- Open `app/client/src/style.css`
- On line 9, change `--background: #E0F6FF;` to `--background: #E0FFE0;`
  - `#E0FFE0` is the direct equivalent of `#E0F6FF`: same red channel (E0=224), max green channel (FF=255) instead of max blue, same blue reduction (E0=224 instead of FF)
  - Both colors have the same perceived lightness (~94%) and saturation, differing only in hue (blue → green)
- No other CSS changes are required — all sections (query, results, tables, modals) use `var(--background)` through the `body` rule

### Step 2: Create feature documentation
- Create `app_docs/feature-9826d71a-light-green-background.md` following the format of `app_docs/feature-6445fc8f-light-sky-blue-background.md`
- Document: ADW ID (`9826d71a`), date, overview, what was built, technical implementation (file modified, key change), how to use, configuration, testing steps, and notes

### Step 3: Run validation commands
- Execute all commands listed in the `Validation Commands` section to confirm zero regressions

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions
- `cd app/client && bun run build` - Build the frontend to ensure the CSS change compiles without errors

## Notes
- The color history for this project: `#f5f7fa` (light gray-blue) → `#fafafa` (off-white) → `#E0F6FF` (light sky blue) → `#E0FFE0` (light green)
- Only `app/client/src/style.css` line 9 needs to change — no JavaScript, no server-side files, no other CSS selectors
- The `--background` variable is consumed by `body { background: var(--background); }` which cascades everywhere; no targeted section updates are needed
- All existing text colors and UI element colors maintain sufficient contrast against `#E0FFE0` (a very light green at ~94% lightness)
