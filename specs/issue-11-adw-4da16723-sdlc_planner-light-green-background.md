# Chore: Background color update

## Metadata
issue_number: `11`
adw_id: `4da16723`
issue_json: `{"number":11,"title":"Background color update","body":"/chore - adw_sdlc_ZTE_iso - update the background color to the equivalent light green color"}`

## Chore Description
Update the application's background color from the current light sky blue (`#E0F6FF`) to the equivalent light green color (`#E0FFE0`). The new color mirrors the same luminance and saturation level as the current sky blue but shifts the dominant hue to green, maintaining visual consistency and readability across all application sections.

## Relevant Files
Use these files to resolve the chore:

- `app/client/src/style.css` — Contains the `--background` CSS variable in the `:root` block (line 9) that controls the body background color across the entire application. This is the only file that needs to change.

- `app_docs/feature-6445fc8f-light-sky-blue-background.md` — Documents the prior background color change (off-white → light sky blue `#E0F6FF`). Provides context for the evolution of this variable and confirms the single-file change pattern.

- `app_docs/feature-f055c4f8-off-white-background.md` — Documents the earlier background change (gray-blue → off-white). Confirms the established pattern of updating only the `--background` CSS variable.

## Step by Step Tasks

### Step 1: Update the `--background` CSS variable in `style.css`
- Open `app/client/src/style.css`
- On line 9, change the `--background` variable from `#E0F6FF` to `#E0FFE0`
  - Before: `--background: #E0F6FF;`
  - After:  `--background: #E0FFE0;`
- Save the file — no other CSS changes are needed; all sections (`body`, `.query-section`, `.results-section`, `.tables-section`, modal backgrounds) inherit this variable

### Step 2: Build the frontend to verify no build errors
- Run `cd app/client && bun run build`
- Confirm the build completes without errors

### Step 3: Run validation commands
- Execute all commands listed in the `Validation Commands` section below to confirm zero regressions

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions
- `cd app/client && bun run build` - Build the frontend to confirm no CSS or TypeScript errors introduced by the change

## Notes
- The light green equivalent of `#E0F6FF` (light sky blue) is `#E0FFE0`: both share the same red channel (0xE0 = 224) and sit at the same overall lightness; the sky blue maximises the blue channel (0xFF) while the green equivalent maximises the green channel (0xFF) — making them true chromatic counterparts.
- Only one line in one file changes; the CSS variable system propagates the new color automatically to every component that uses `var(--background)`.
- No server-side changes are required.
- After the change, verify visually that text contrast remains acceptable — the very pale green is in the same brightness range as the current pale blue, so no contrast issues are expected.
