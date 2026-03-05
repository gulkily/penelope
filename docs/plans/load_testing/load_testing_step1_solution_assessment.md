# Load Testing - Step 1 Solution Assessment

Problem statement: The project needs a repeatable way to load test API performance and stability under concurrent usage.

Option A: Locust (Python-based load testing)
- Pros: Fits existing Python tooling, easy to script HTTP user flows, low setup friction.
- Cons: Requires a separate load-test runner and dataset planning.

Option B: k6 (Go-based, JS scripting)
- Pros: Fast, modern CLI with strong metrics output.
- Cons: Adds non-Python tooling, conflicts with the no-npm preference for scripting.

Option C: Simple bash + curl loops
- Pros: Minimal setup, quick to run.
- Cons: Limited concurrency control, poor metrics, not representative of real load.

Recommendation: Option A (Locust) to keep tooling Python-native and enable realistic concurrent user flows with usable metrics.
