# User House Assignment - Step 3 Development Plan

Sizing note: each stage is scoped to roughly <=1 hour or <=50 lines of net change; split further during implementation if any stage exceeds that.

1. Stage 1 - Introduce account-level house contract (net-new capability)
   - Goal: Add a canonical house field to user accounts so admins can assign houses before first login.
   - Dependencies: Existing `accounts` table, DB init migration helpers, and `app/house.py` normalization constants.
   - Expected changes:
     - Conceptually extend account storage with a required `house` value using existing canonical options.
     - Ensure existing rows are safely backfilled to a deterministic default (`Unassigned`).
     - Extend account read helpers to include `house` in returned user records.
     - Planned signatures:
       - `create_account(initial_username: str, house: str = DEFAULT_HOUSE) -> dict`
       - `update_account_house(account_id: int, house: str) -> dict`
   - Verification approach: Manual DB/API smoke check confirms all listed users have non-empty normalized house values after startup/init.
   - Risks or open questions:
     - Need to avoid breaking existing local DBs during backfill.
     - Keep house normalization behavior identical to project-level house handling.
   - Canonical components/API touched: `app/db_init.py`, `app/db_auth.py`, `app/db.py`, `app/house.py`.

2. Stage 2 - Extend magic-link issuance contract with house assignment
   - Goal: Guarantee account existence and assign house at issuance time for target usernames.
   - Dependencies: Stage 1 account house contract and existing shared magic-link issuance service.
   - Expected changes:
     - Extend issuance flow to resolve/create target account before token creation.
     - Accept a house value in issuance input and apply it immediately to the resolved/created target account.
     - Reuse existing username matching semantics (case-insensitive trim) to prevent duplicates.
     - Return issuance metadata sufficient for admin UX feedback (for example, whether account was newly created and which house was applied).
     - Planned signatures:
       - `issue_magic_link(configured_username: str, issuer_account_id: int, base_url: str) -> dict`
       - Internal helper: `get_or_create_account_for_username(username: str) -> tuple[dict, bool]`
       - `class MagicLinkCreateRequest(BaseModel): configured_username: str, house: str`
   - Verification approach: Manual issuance smoke test for existing vs new usernames; confirm new username appears in users list immediately.
   - Risks or open questions:
     - Duplicate-account risk if normalization is inconsistent across call sites.
     - Updating an existing user's house during issuance is intentional; UI messaging must make this explicit.
   - Canonical components/API touched: `app/magic_link_service.py`, `app/db_auth.py`, `app/api_auth.py`, `scripts/pnl.py`.

3. Stage 3 - Add admin API for user house assignment and extend users payload
   - Goal: Expose house assignment as an explicit admin-only user-management capability.
   - Dependencies: Stage 1 storage and Stage 2 account bootstrap behavior.
   - Expected changes:
     - Extend `GET /api/auth/users` response entries to include `house`.
     - Add admin-only mutation endpoint for house updates on user accounts.
     - Enforce house validation via canonical house normalization rules.
     - Prevent non-admin actors from mutating user house assignments.
     - Planned signatures:
       - `class AdminUserListEntry(...): id, username, created_at, is_admin, house`
       - `PUT /api/auth/users/{account_id}/house`
       - `class AdminUserHouseUpdateRequest(BaseModel): house: str`
   - Verification approach: Manual API checks for admin success, invalid-house rejection, and non-admin `403`.
   - Risks or open questions:
     - House editing is intentionally allowed for admin accounts too; UI copy should avoid implying restrictions that do not exist.
     - Keep response contract stable for existing users page consumers.
   - Canonical components/API touched: `app/schemas.py`, `app/api_auth.py`, `app/auth.py`, `app/db_auth.py`.

4. Stage 4 - Extend Users page from read-only to admin house assignment workflow
   - Goal: Provide in-app house assignment controls in the existing admin users surface.
   - Dependencies: Stage 3 API contract.
   - Expected changes:
     - Add house column with per-user dropdown selector using canonical house options.
     - Wire save/update action to the new admin house update endpoint.
     - Keep clear status/error messaging and preserve existing users list loading behavior.
   - Verification approach: Manual UI smoke: assign house to a placeholder user, refresh, and verify persistence.
   - Risks or open questions:
     - Avoid accidental bulk edits while keeping interactions fast.
     - Keep role/admin indicator clarity while adding editable fields.
   - Canonical components/API touched: `templates/users.html`, `static/js/users.js`, shared `static/css/main.css` table/form patterns.

5. Stage 5 - Add house selector to magic-link generator UI and wire issuance payload
   - Goal: Keep admin tooling consistent across web and CLI issuance paths.
   - Dependencies: Stage 2 issuance behavior and Stage 4 users workflow.
   - Expected changes:
     - Add house dropdown selector to magic-links generation form.
     - When typed username matches an existing account, prefill the house dropdown to that account's current house.
     - Send selected house with `POST /api/auth/magic-links` so assignment happens immediately on generation.
     - Update status messaging to indicate account bootstrap + assigned house outcome.
     - Update `./pnl magic-link` to accept optional/required `--house` so CLI behavior matches web issuance semantics.
   - Verification approach: Manual web + CLI smoke checks confirm clear messaging and unchanged link generation behavior.
   - Risks or open questions:
     - Keep defaults explicit so admins do not unintentionally assign wrong houses.
   - Canonical components/API touched: `templates/magic_links.html`, `static/js/magic-links.js`, `scripts/pnl.py`, `README.md`.

6. Stage 6 - Hide dashboard house selector for non-admin users
   - Goal: Remove house-filter control from dashboard UI for non-admin sessions.
   - Dependencies: Existing session context (`session_is_admin`) and current dashboard filter rendering.
   - Expected changes:
     - Gate house selector rendering/visibility in dashboard to admin sessions only.
     - Ensure non-admin dashboard still loads resident selection without exposing house filter controls.
     - Keep behavior deterministic for bookmarked URLs that include `house` query parameters.
   - Verification approach: Manual smoke as admin vs non-admin confirms selector visible only for admins and dashboard remains functional for both.
   - Risks or open questions:
     - Hiding selector is a UI change only; access scoping by house would be separate feature work.
   - Canonical components/API touched: `templates/index.html`, `static/js/app.js`, `app/main.py` context usage.

7. Stage 7 - Regression coverage and rollout validation
   - Goal: Protect auth/account behavior while introducing this new user-house feature.
   - Dependencies: Stages 1-6 complete.
   - Expected changes:
     - Add focused tests for:
       - magic-link issuance creating placeholder accounts for unknown usernames
       - magic-link issuance pre-filling and applying house for existing usernames
       - user house update authorization/validation
       - users list including house values
       - magic-link redemption linking to the same pre-created account
       - dashboard house selector visibility by admin vs non-admin session
     - Add brief operator docs note describing the new onboarding flow.
   - Verification approach: Run targeted test suites plus one manual end-to-end admin onboarding smoke pass.
   - Risks or open questions:
     - Test setup needs deterministic admin/non-admin fixtures.
     - Ensure no regression in existing magic-link issuance/revocation flows.
   - Canonical components/API touched: `tests/http/` (and/or equivalent auth tests), `README.md`.
