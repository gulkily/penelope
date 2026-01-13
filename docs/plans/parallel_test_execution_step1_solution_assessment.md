# Parallel Test Execution Step 1: Solution Assessment

Problem statement: Run the full pytest suite in parallel (and repeatedly) against a manually managed server while supporting light load-style pressure.

Option A - Pytest-xdist with a shared manually run app server + shared database
- Pros: Minimal changes; single server process managed by the user; matches “tests never start the server” requirement.
- Cons: Higher risk of flakiness from shared state; load-style pressure can amplify interference.

Option B - Pytest-xdist with isolated app+database per worker
- Pros: Strong isolation; parallelism scales predictably; reduces interference under load-style runs.
- Cons: Requires tests to orchestrate servers, which conflicts with the manual-server requirement.

Option C - External parallel runner (multiple independent pytest processes) each with its own app+database
- Pros: Isolation without deep pytest plugin work; easy to throttle concurrency; flexible load-style concurrency.
- Cons: Process orchestration becomes the test runner’s responsibility; still conflicts with the manual-server requirement.

Recommendation: Option A. It aligns with a manually managed server and keeps the workflow simple, accepting the increased flake risk as the trade-off while adding limited load-style pressure.
