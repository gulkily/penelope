# Dark Mode - Step 1 Solution Assessment

Problem statement: Users need a low-light friendly theme, but the app currently only offers a light appearance.

Option A: System-driven dark mode only
- Pros: Minimal UI changes, leverages OS preference, lowest ongoing maintenance.
- Cons: No manual override, users cannot choose a different theme per device or context.

Option B: App toggle with stored preference only
- Pros: Clear user control, consistent across sessions, independent of OS setting.
- Cons: Ignores system preference, requires additional UI affordance and state handling.

Option C: System default with optional override
- Pros: Respects OS by default while giving manual control, best user flexibility.
- Cons: Slightly more complexity to manage precedence and persistence.

Recommendation: Option C, because it balances user control with expected system behavior while keeping the experience consistent across devices.
