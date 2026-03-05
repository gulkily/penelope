# Admin User List Step 1: Solution Assessment

## Problem Statement
Enable admins to view a read-only list of users and whether each user is currently treated as admin.

## Option A: Read-Only Users API + Derive Admin Status from Current Auth Rules
Pros:
- Fastest implementation path.
- No database migration.
- Stays consistent with `auth.is_admin_account` and `MAGIC_LINK_ADMIN_USERNAMES`.

Cons:
- Displayed admin status depends on environment config.
- If `MAGIC_LINK_ADMIN_USERNAMES` is empty, all accounts appear admin (current behavior).

## Option B: Add DB Role Field and Display DB-Backed Admin Status
Pros:
- Stable displayed status independent of `.env`.
- Better foundation if role editing is added later.

Cons:
- Requires schema change and backfill.
- Introduces two possible admin sources unless auth checks are also migrated now.

## Option C: Show List Only (No Admin Status)
Pros:
- Smallest UI/API change.
- Avoids confusion from env-driven admin status.

Cons:
- Does not satisfy the "who is admin" requirement.
- Requires follow-up work immediately.

## Recommendation
Option A is the best fit for this reduced scope. It delivers the requested user list plus admin indicator quickly and safely by reusing existing permission logic, while deferring role-management and schema decisions.
