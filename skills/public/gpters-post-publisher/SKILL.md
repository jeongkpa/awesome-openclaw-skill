---
name: gpters-post-publisher
description: Automate publishing a post on gpters.org KLxSodedLeDUiTj board via browser actions: open new post page, fill title/body, add tag "21기 내삶자동화", and publish. Use when asked to draft or publish GPTers 사례 posts, including flows that require the user to complete login manually mid-process.
---

# gpters Post Publisher

Publish GPTers 사례 글 with this deterministic browser workflow.

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

3. Fill post fields:
- Title input: fill with `title`.
- Body editor: **do not paste raw markdown**.
- Convert markdown to rendered rich text (HTML-like formatted content) and insert into the editor so headings/lists/bold are preserved.
- Preferred method: set editor rich-text content directly (or paste from rendered preview), then verify visible heading/list formatting in snapshot.

4. Add tag:
- Find tag/chip input area.
- Type `21기 내삶자동화` (or provided tag).
- Press **Enter** to finalize the tag chip.
- Verify visible tag chip exists.
- If tag dropdown/list is still open, close it (click outside/editor label area) before publish.

5. Publish:
- If `publish=true`, click publish/register button.
- If confirmation dialog appears, accept it.

6. Verify completion:
- Confirm navigation to post page or success toast.
- Report final URL to user.

## Reliability Rules

- Use `browser.snapshot` with `refs="aria"` before each critical step.
- Prefer robust refs over CSS selectors where possible.
- Re-snapshot after each mutation step (title/body/tag/publish).
- After body insertion, confirm rendered structure (at least one heading/list/strong element visible), not raw markdown tokens.
- If element labels differ, match semantically (e.g., `제목`, `타이틀`, `내용`, `발행`, `등록`, `게시`).

## Safety

- Never publish without explicit content confirmation when body is empty/placeholder.
- If publish button is ambiguous, stop and ask before final click.
- If login/session expires mid-flow, pause and ask user to re-login.

## Output Contract

Return concise status:
- `작성 완료, 발행 완료: <url>`
- or `작성 완료(미발행). 발행 대기 중.`
- or blockers with exact next user action.
