# Concurrency Estimate (Current Architecture)

## Short answer
With the current setup (single-process uvicorn, sync endpoints, SQLite), expect **dozens of concurrent active editors** comfortably and **hundreds of mostly-idle sessions**. Writes are the limiting factor.

## Assumptions
- Single uvicorn worker.
- Sync handlers; each worker handles one request at a time.
- SQLite file storage; concurrent writes serialize.
- Typical local request times:
  - Reads: ~10–30ms
  - Writes: ~20–50ms

## Throughput estimate (per worker)
- Reads: ~20–100 req/s (1 / 0.05s to 1 / 0.01s)
- Writes: ~10–40 req/s (1 / 0.1s to 1 / 0.025s)

## Translate to sessions
Using Little’s Law: **Concurrency ≈ Arrival rate × Service time**.

If an active user does ~1 action every 5 seconds (0.2 req/s):
- 20 req/s ÷ 0.2 req/s ≈ 100 active sessions.

If users drag the progress slider (debounced at 250ms, ~4 writes/sec each):
- 10 concurrent draggers → ~40 writes/sec, which is near the upper comfortable limit for SQLite.

## Practical envelope
- Active editors: ~20–50 at once before latency spikes.
- Passive viewers: hundreds (idle sessions generate little load).

## Next step for a firm number
Run a load test that simulates:
- Read-heavy traffic (project list/detail)
- Write bursts (add/edit/delete, progress slider)
