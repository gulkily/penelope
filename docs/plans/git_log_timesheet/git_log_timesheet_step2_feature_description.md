# Git Log Timesheet - Step 2 Feature Description

Problem: Developers need a faster way to create a basic timesheet estimate from commit history without manually reconstructing hours worked. The solution should stay outside the application and run as a standalone script.

User stories:
- As a developer, I want to generate estimated hours from git history so that I can prepare weekly timesheets quickly.
- As a developer, I want to filter by date range and author so that I can produce timesheets for a specific reporting period.
- As a team lead, I want export-friendly output so that timesheet data can be shared in common reporting formats.

Core requirements:
- Provide a standalone script under `scripts/` and keep the feature out of FastAPI routes, templates, and static UI.
- Generate daily estimated hours plus a date-range total based on git log activity.
- Support date-range filtering and author filtering to scope the report.
- Use a deterministic, documented estimation rule so repeated runs over the same git history produce the same totals.
- Provide readable terminal output and at least one export-friendly output format.

Shared component inventory:
- Existing UI/API surfaces: none; no current app page or endpoint renders timesheet data, and this feature intentionally does not add one.
- Existing canonical data source to reuse: repository commit history from git log.
- Existing extension point to reuse: script conventions in `scripts/` and developer documentation in `README.md`/`AGENTS.md` for command discoverability.
- New component needed: a dedicated timesheet script, because the requirement is explicitly non-application tooling.

Simple user flow:
1. Developer runs the timesheet script with a date range (and optional author/filter flags).
2. Script reads git history for the requested scope.
3. Script applies the estimation rule and computes per-day hours and total hours.
4. Script prints a summary and optionally writes export-friendly output.

Success criteria:
- Running one script command returns a report with daily estimated hours and a total for the requested date range.
- Running the command twice against unchanged git history returns identical totals.
- The report can be consumed directly in terminal output and exported for external timesheet use.
- No new application UI/API surface is introduced.
