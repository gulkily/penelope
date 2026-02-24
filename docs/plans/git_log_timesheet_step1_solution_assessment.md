# Git Log Timesheet - Step 1 Solution Assessment

Problem statement: Developers need a quick, repeatable way to generate a basic estimated-hours timesheet from repository commit history.

Option A: Add a `./pnl` command that summarizes git activity into daily hours by author and date range
- Pros: Fits existing project workflow; easy for developers to run locally; no UI work required.
- Cons: Output stays in terminal/text format unless manually exported; relies on local git data being complete.

Option B: Add an authenticated web page that generates and displays timesheet estimates from git log
- Pros: More discoverable for non-CLI users; easier to review and share in-app.
- Cons: Higher scope (backend + frontend); adds UX and access-control overhead for a basic internal need.

Option C: Add a standalone script in `scripts/` that generates CSV/Markdown timesheet output
- Pros: Simple to build; easy to automate in CI or scheduled jobs; export-friendly for reporting.
- Cons: Separate command path from the main task runner; less discoverable than `./pnl` commands.

Recommendation: Option C. A standalone script keeps this outside the application surface area while still generating practical git-log-based hour estimates and export-friendly output.
