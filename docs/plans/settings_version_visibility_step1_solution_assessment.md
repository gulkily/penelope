# Settings Version Visibility - Step 1 Solution Assessment

Problem statement: Admins need to quickly confirm which Penelope version is running from the Settings page.

Option A: Show a static app version string from configuration
- Pros: Simple, predictable, and available in all environments.
- Cons: Requires disciplined version updates at release time.

Option B: Show latest git commit SHA/date in Settings
- Pros: Precise build identification and easy troubleshooting correlation.
- Cons: Can be unavailable or inconsistent in packaged deployments.

Option C: Show both release version and build metadata
- Pros: Combines user-friendly versioning with precise technical traceability.
- Cons: Slightly more UI complexity and more metadata to manage.

Recommendation: Option B. Commit SHA/date gives admins exact build identification for support and troubleshooting with minimal setup.
