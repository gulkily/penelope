# User House Assignment - Step 1 Solution Assessment

## Problem Statement
Admins need to assign houses to non-admin user accounts immediately, including brand-new users at magic-link issuance time.

## Option A: Keep Account Creation Deferred Until First Magic-Link Login
Pros:
- No schema/API expansion.
- Smallest short-term change to current flow.

Cons:
- Does not satisfy immediate assignment requirement.
- Admins still cannot assign houses before first login.
- Creates operational ambiguity for pre-onboarding workflows.

## Option B: Pre-Create Placeholder Accounts on Magic-Link Issuance + Persist House on Accounts
Pros:
- Directly satisfies the requirement: account exists as soon as link is issued.
- Enables immediate admin house assignment in the existing users management surface.
- Keeps identity and house ownership in one durable account record.

Cons:
- Requires a small schema update for account-level house storage.
- Adds one more admin-editable user attribute to maintain.

## Option C: Add Separate House-Mapping Layer (Not Stored on Account Rows)
Pros:
- Avoids modifying the core accounts table directly.
- Can support historical or multi-house assignment models later.

Cons:
- More moving parts for a simple current need.
- Higher risk of account/house drift between records.
- Slower to deliver and harder to reason about operationally.

## Recommendation
Option B. It is the smallest approach that fully meets the requirement: create placeholder users at magic-link generation and allow admins to assign house immediately, while keeping user identity and house assignment coherent.
