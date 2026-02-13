# Interview Questions Template — Step 1 Solution Assessment

## Problem Statement
The interview questions currently live in an image (`screenshot/questions_from_architect_for_review.jpeg`), and we need them as a maintainable text template plus a practical way to review them during live interviews.

## Option A — Text Template File Only (Markdown/TXT in Repo)
- Pros:
  - Fastest path and lowest implementation risk.
  - Version-controlled edits and easy collaboration.
  - No backend or UI changes required.
- Cons:
  - Review experience during interviews depends on external tools/editor tabs.
  - Not integrated with the app workflow while recording.

## Option B — Text Template File + Read-Only In-App Interview Guide View
- Pros:
  - Keeps the source of truth as a text file while enabling in-app review during interviews.
  - Improves interviewer workflow (single app context).
  - Still avoids database schema changes.
- Cons:
  - Requires lightweight backend/template wiring.
  - Needs small UX decisions (where to access the guide, basic formatting rules).

## Option C — Database-Backed Question Bank with In-App Viewer/Editor
- Pros:
  - Full in-app management and potential role-based updates later.
  - Could support multiple interview templates in the future.
- Cons:
  - Highest complexity and maintenance cost.
  - Requires schema/API/admin UX work that exceeds the immediate need.

## Recommendation
Option B. It satisfies both requirements directly: a durable text template source plus a convenient in-app review surface during interviews, without introducing database migrations or unnecessary scope.
