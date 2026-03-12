---
name: gpters-post-publisher
description: Automate publishing a post on gpters.org KLxSodedLeDUiTj board via browser actions: open new post page, fill title/body, add tag "21기 내삶자동화", and publish. Use when asked to draft or publish GPTers 사례 posts, including flows that require the user to complete login manually mid-process.
---

# gpters Post Publisher

Publish GPTers 사례 글 with a deterministic browser workflow that matches the live GPTers editor.

## Required Inputs

Collect these before starting:
- `title`: post title
- `body`: post body (Korean text allowed)

Optional:
- `tag` (default: `21기 내삶자동화`)
- `publish` (`true` by default, `false` for draft-only fill)

## Workflow

1. Open:
- `https://www.gpters.org/new?post_type=KLxSodedLeDUiTj`

2. Detect login requirement:
- If editor is not visible and login UI appears, ask user to log in manually.
- Pause and resume only after user confirms login complete.

3. Snapshot the page and capture stable refs:
- Prefer `browser.snapshot --labels` (AI refs) over plain aria dumps when you need actionable refs for `click`, `type`, and `evaluate`.
- On the live page observed during testing, the important semantics were:
  - title field near `textbox "제목"`
  - body editor as `textbox "Rich-Text Editor"`
  - tag field as `textbox "태그 추가..."`
  - publish button as `button "게시"`

4. Fill post fields:
- Fill the title input with `title`.
- Do **not** paste raw markdown into the body editor.
- Convert markdown or plain draft text into rendered rich text HTML and insert it into the ProseMirror/Tiptap editor so headings/lists/bold are preserved.
- Prefer direct rich-text insertion when the editor is contenteditable. In the tested GPTers editor, the body node was a `DIV.tiptap.ProseMirror.prose` with `contenteditable="true"`, so setting `innerHTML` via browser evaluation worked reliably.
- After insertion, dispatch `input` and `change` events, then re-snapshot to confirm the visible structure contains headings/lists/strong text rather than raw markdown tokens.

5. Add tag:
- Find the tag/chip input area.
- Type the tag text.
- If pressing Enter only opens a suggestion list, click the matching option from the listbox to finalize the chip.
- Verify the combobox now shows the tag as selected text/chip.
- If the dropdown/list is still open, click outside before publishing.

6. Publish:
- If `publish=true`, click the publish/register button.
- If confirmation dialog appears, accept it.

7. Verify completion:
- Confirm navigation to the final post page, not just a toast.
- Return the final URL.

## Why this workflow succeeded

- The GPTers page was already logged in and the full editor was visible, so no auth blocker remained.
- `openclaw browser` CLI commands were available even without a first-class browser tool in the chat tool list.
- `snapshot --labels` exposed stable refs that were directly usable by `click`, `type`, and `evaluate`.
- The title field accepted normal typing.
- The body editor was a live contenteditable ProseMirror node, so direct `innerHTML` insertion preserved headings, lists, and code formatting better than raw text pasting.
- The tag required suggestion selection to become a finalized chip; once selected, the page reflected the tag correctly.
- After clicking `게시`, the page navigated to the final post URL, which confirmed successful publication.

## Error handling and fixes observed during real use

- If `openclaw browser` reports `gateway url override requires explicit credentials`, pass the gateway token explicitly with `--token`.
- If a command like `wait --url 'gpters.org/new'` is interpreted as a gateway URL override and triggers a security error, avoid that form. Use a simple sleep or another non-conflicting wait pattern, then snapshot again.
- If `snapshot --format aria --labels` fails, switch to `snapshot --labels` because labels/efficient mode require AI snapshot format.
- If `evaluate` rejects `--args`, inline the serialized HTML string directly into the evaluation function source instead.
- If pressing Enter in the tag field only opens the dropdown and does not finalize the tag, click the matching suggestion option explicitly, then re-snapshot to confirm the selected tag is present.

## Reliability Rules

- Snapshot before every critical step and after every mutation step.
- Prefer robust refs and semantic labels over CSS selectors.
- After body insertion, confirm rendered structure, not just non-empty text.
- Treat tag selection as a two-step flow: type -> select/confirm -> verify.
- Treat publish success as navigation to the post page with a concrete URL.
- If element labels differ, match semantically (e.g., `제목`, `타이틀`, `내용`, `발행`, `등록`, `게시`).

## Safety

- Never publish without explicit content confirmation when body is empty or placeholder-like.
- If publish button is ambiguous, stop and ask before final click.
- If login/session expires mid-flow, pause and ask user to re-login.

## Output Contract

Return concise status:
- `작성 완료, 발행 완료: <url>`
- or `작성 완료(미발행). 발행 대기 중.`
- or blockers with exact next user action.
