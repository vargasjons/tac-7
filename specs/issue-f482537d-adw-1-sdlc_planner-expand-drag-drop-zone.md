# Feature: Expand Drag-Drop Zone to Full Section Surfaces

## Metadata
issue_number: `f482537d`
adw_id: `1`
issue_json: `{"number":1,"title":"Increase drop zone surface area","body":"/feature\n\nadw_sdlc_iso\n\nlets increase the drop zone surface area. instead of having to click \"upload data\". The user can drag and drop the right on to the upper div or lower div and the ui will update to a 'drop to create table' text. This runs the same usual functionality but enhances the ui to be more user friendly."}`

## Feature Description
Expand the file drag-and-drop target area so users can drop CSV/JSON/JSONL files directly onto the query section (upper div, `#query-section`) or the available-tables section (lower div, `#tables-section`). When a file is dragged over either section, a full-section overlay appears with "Drop to create table" text and a visual highlight. Releasing the file triggers the existing `handleFileUpload()` function — no new backend logic is required. This removes friction from the upload flow by eliminating the need to open the upload modal just to drop a file.

## User Story
As a user of the Natural Language SQL Interface  
I want to drag and drop data files directly onto the main page sections  
So that I can create tables faster without needing to open the upload modal

## Problem Statement
Currently, the only drag-and-drop target is the small `#drop-zone` div inside the upload modal. Users must first click "Upload" to open the modal, then drag their file into the narrow drop zone — two steps when one would suffice. The large empty areas of the query section and tables section go unused as drop targets, making the interface feel less intuitive than modern web applications.

## Solution Statement
Add `dragenter`, `dragover`, `dragleave`, and `drop` event listeners to `#query-section` and `#tables-section`. When a drag enters either section, render a full-section overlay (absolutely positioned inside the section) displaying "Drop to create table" with a visual cue. On drop, pass the file to the existing `handleFileUpload()` function. On drag leave or drop, remove the overlay. No server-side changes are needed.

## Relevant Files

- **`app/client/index.html`** — HTML structure; needs drop-overlay divs added inside `#query-section` and `#tables-section`
- **`app/client/src/main.ts`** — All client-side logic; add `initializeSectionDragDrop()` and wire it up in `DOMContentLoaded`
- **`app/client/src/style.css`** — Styling; needs `position: relative` on section classes plus new overlay styles
- **`app/client/src/types.d.ts`** — Type definitions (read-only reference; no changes expected)
- **`app/client/src/api/client.ts`** — API layer (read-only reference; `uploadFile` is called unchanged)

> Also read `app_docs/feature-cc73faf1-upload-button-text.md` (upload UI conventions), `app_docs/feature-f055c4f8-off-white-background.md` (background color tokens), and `app_docs/feature-6445fc8f-light-sky-blue-background.md` (background palette) before styling the overlay.

> Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand how to create the E2E test file.

### New Files
- **`.claude/commands/e2e/test_expand_drag_drop_zone.md`** — E2E test validating drag-and-drop onto the query and tables sections

## Implementation Plan

### Phase 1: Foundation
Add `position: relative` to `.query-section` and `.tables-section` in `style.css` (required so the absolute-positioned overlay is scoped to each section). Add new CSS rules for the overlay and its dragover state.

### Phase 2: Core Implementation
1. Add a `.drop-overlay` div inside each target section in `index.html` (hidden by default).
2. Implement `initializeSectionDragDrop()` in `main.ts`:
   - Use a per-element drag-counter to handle `dragenter`/`dragleave` correctly across nested child elements.
   - On `dragenter`: increment counter, show overlay.
   - On `dragleave`: decrement counter; when counter reaches 0, hide overlay.
   - On `dragover`: call `e.preventDefault()` to allow the drop.
   - On `drop`: reset counter, hide overlay, extract `e.dataTransfer.files[0]`, call `handleFileUpload(file)`.
3. Call `initializeSectionDragDrop()` from the `DOMContentLoaded` handler alongside existing initializers.

### Phase 3: Integration
- Verify the existing modal drag-drop zone (`#drop-zone`) continues to work unchanged — it runs in its own `initializeFileUpload()` scope.
- Verify `handleFileUpload()` is called identically from both the original modal path and the new section path.
- Verify the TypeScript build passes with zero errors.

## Step by Step Tasks

### Step 1: Create the E2E test file
- Create `.claude/commands/e2e/test_expand_drag_drop_zone.md`
- The test should:
  - Navigate to the app URL
  - Take a screenshot of the initial state showing both sections
  - Simulate a dragover on `#query-section` and verify the overlay appears with "Drop to create table"
  - Take a screenshot of the overlay visible on the query section
  - Simulate a dragover on `#tables-section` and verify the overlay appears there too
  - Take a screenshot of the overlay visible on the tables section
  - Actually upload a file via the drop target on `#query-section` and verify the table appears in Available Tables
  - Take a screenshot of the success state

### Step 2: Add overlay HTML to `app/client/index.html`
- Inside `<section id="query-section" ...>` (line 15), add as the **last child** before `</section>`:
  ```html
  <div class="drop-overlay" id="query-section-drop-overlay">
    <div class="drop-overlay-content">
      <span class="drop-overlay-icon">📂</span>
      <p class="drop-overlay-text">Drop to create table</p>
    </div>
  </div>
  ```
- Inside `<section id="tables-section" ...>` (line 42), add as the **last child** before `</section>`:
  ```html
  <div class="drop-overlay" id="tables-section-drop-overlay">
    <div class="drop-overlay-content">
      <span class="drop-overlay-icon">📂</span>
      <p class="drop-overlay-text">Drop to create table</p>
    </div>
  </div>
  ```

### Step 3: Add CSS to `app/client/src/style.css`
- Add `position: relative` to `.query-section` (after line 62) and `.tables-section` (after line 231)
- Add new CSS rules at the end of the file for:
  - `.drop-overlay` — `position: absolute; inset: 0; display: none; align-items: center; justify-content: center; background: rgba(102, 126, 234, 0.12); border: 3px dashed var(--primary-color); border-radius: 12px; z-index: 10; pointer-events: none;`
  - `.drop-overlay.visible` — `display: flex;`
  - `.drop-overlay-content` — `text-align: center;`
  - `.drop-overlay-icon` — `font-size: 3rem; display: block; margin-bottom: 0.5rem;`
  - `.drop-overlay-text` — `font-size: 1.25rem; font-weight: 600; color: var(--primary-color); margin: 0;`

### Step 4: Add `initializeSectionDragDrop()` to `app/client/src/main.ts`
- Add the function after `initializeFileUpload()` (around line 158):
  ```typescript
  function initializeSectionDragDrop() {
    const targets = [
      document.getElementById('query-section') as HTMLElement,
      document.getElementById('tables-section') as HTMLElement,
    ];

    targets.forEach(section => {
      const overlayId = `${section.id}-drop-overlay`;
      const overlay = document.getElementById(overlayId) as HTMLElement;
      let dragCounter = 0;

      section.addEventListener('dragenter', (e) => {
        if (!e.dataTransfer?.types.includes('Files')) return;
        e.preventDefault();
        dragCounter++;
        overlay.classList.add('visible');
      });

      section.addEventListener('dragleave', () => {
        dragCounter--;
        if (dragCounter <= 0) {
          dragCounter = 0;
          overlay.classList.remove('visible');
        }
      });

      section.addEventListener('dragover', (e) => {
        if (!e.dataTransfer?.types.includes('Files')) return;
        e.preventDefault();
      });

      section.addEventListener('drop', (e) => {
        e.preventDefault();
        dragCounter = 0;
        overlay.classList.remove('visible');
        const files = e.dataTransfer?.files;
        if (files && files.length > 0) {
          handleFileUpload(files[0]);
        }
      });
    });
  }
  ```
- Call `initializeSectionDragDrop()` in the `DOMContentLoaded` handler (after `initializeModal()`, line 10):
  ```typescript
  document.addEventListener('DOMContentLoaded', () => {
    initializeQueryInput();
    initializeFileUpload();
    initializeModal();
    initializeSectionDragDrop();   // <-- add this line
    initializeRandomQueryButton();
    loadDatabaseSchema();
  });
  ```

### Step 5: Run validation commands
- Execute every command listed in the **Validation Commands** section to confirm zero regressions.

## Testing Strategy

### Unit Tests
No new unit tests are required — the only logic added is DOM event wiring and a counter. The existing `handleFileUpload()` function already has implicit coverage via the original drop-zone path.

### Edge Cases
- **Drag with non-file content** (e.g., text drag): Guard with `e.dataTransfer?.types.includes('Files')` so the overlay only activates for file drags.
- **Nested child elements**: Use `dragCounter` per section to prevent the overlay from flickering when the pointer moves over child elements.
- **Multiple files dropped**: Only `files[0]` is passed to `handleFileUpload()` — consistent with the existing modal drop-zone behavior.
- **Drag from one section to another**: Each section has its own independent counter; leaving one resets it without affecting the other.
- **Unsupported file type**: Handled downstream by `handleFileUpload()` / server validation — no changes needed here.
- **Modal drag-drop still works**: Separate `initializeFileUpload()` scope is untouched.

## Acceptance Criteria
- [ ] Dragging a `.csv`, `.json`, or `.jsonl` file over `#query-section` shows the "Drop to create table" overlay
- [ ] Dragging a file over `#tables-section` shows the "Drop to create table" overlay
- [ ] The overlay disappears when the drag leaves the section (without dropping)
- [ ] Dropping a file on either section calls `handleFileUpload()` and creates the table (same behavior as modal drop-zone)
- [ ] The existing Upload button and modal drag-drop zone are unaffected
- [ ] No TypeScript errors (`bun tsc --noEmit` passes)
- [ ] Frontend build succeeds (`bun run build` passes)
- [ ] Server tests pass (`uv run pytest` passes)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

1. Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_expand_drag_drop_zone.md` to validate drag-and-drop functionality works end-to-end.
2. `cd app/server && uv run pytest` — Run server tests to validate zero regressions
3. `cd app/client && bun tsc --noEmit` — Validate TypeScript compiles without errors
4. `cd app/client && bun run build` — Validate frontend builds without errors

## Notes
- `pointer-events: none` on the overlay prevents it from intercepting `dragleave` events from children, which would otherwise cause flickering. The drag-counter approach on the parent section handles nested-element transitions correctly.
- The overlay `z-index: 10` ensures it renders above all section content (textarea, buttons, table items) without conflicting with the modal (`z-index: 1000`).
- No server-side changes are needed; the file upload endpoint (`POST /api/upload`) is unchanged.
- The conditional docs check revealed: `app_docs/feature-cc73faf1-upload-button-text.md` (upload UI), `app_docs/feature-f055c4f8-off-white-background.md` and `app_docs/feature-6445fc8f-light-sky-blue-background.md` (color tokens) should be consulted for visual consistency during implementation.
