---
name: gpters-post-publisher
description: Automate drafting and publishing GPTers 사례 posts on gpters.org via browser actions. Use when asked to write, fill, or publish a GPTers 사례글, especially on the KLxSodedLeDUiTj board flow. Handles title entry, rich-text body insertion into the live ProseMirror editor, tag selection for "21기 내삶자동화", login-paused resume flows, and final publish verification by URL.
---

# gpters Post Publisher

Publish GPTers 사례 글 with a deterministic browser workflow that matches the live GPTers editor.

## Quick-start usage

Use this skill when the user asks for any of the following:
- "지피터스 사례글 초안 작성해줘"
- "이 글 지피터스에 올려줘"
- "GPTers 사례 게시판에 발행해줘"
- "로그인하면 이어서 발행해줘"

Collect and normalize these inputs before acting:
- required: `title`
- required: `body`
- optional: `tag` (default `21기 내삶자동화`)
- optional: `publish` (`true` by default)

If the user provides only a rough draft, first turn it into publishable Korean prose with clear section structure, then continue with the browser workflow.

## Required Inputs

Collect these before starting:
- `title`: post title
- `body`: post body (Korean text allowed)

Optional:
- `tag` (default: `21기 내삶자동화`)
- `publish` (`true` by default, `false` for draft-only fill)

## Workflow

1. Open the new-post page:
- `https://www.gpters.org/new?post_type=KLxSodedLeDUiTj`
- If the current session does not expose a first-class browser tool, use `exec` to run `openclaw browser ...` CLI commands instead.

2. Confirm page readiness:
- Start the managed browser profile if needed.
- Open the page.
- Snapshot immediately to determine whether the editor is visible, whether login is required, and which refs are stable.

Example CLI pattern:
- `openclaw browser --browser-profile openclaw status`
- `openclaw browser --browser-profile openclaw start`
- `openclaw browser --browser-profile openclaw open 'https://www.gpters.org/new?post_type=KLxSodedLeDUiTj'`
- `openclaw browser --browser-profile openclaw snapshot --labels --limit 220`

3. Detect login requirement:
- If editor is not visible and login UI appears, ask user to log in manually.
- Pause and resume only after user confirms login complete.

4. Snapshot the page and capture stable refs:
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

## Example execution pattern

1. Draft or normalize the post content into a clear Korean 사례글 structure.
2. Open GPTers new-post page and snapshot with labels.
3. Fill title.
4. Insert rendered rich-text HTML into the live editor.
5. Add and confirm the tag.
6. Publish.
7. Verify the final URL and report it.

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
