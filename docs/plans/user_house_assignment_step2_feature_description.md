# User House Assignment - Step 2 Feature Description

## Problem
Magic-link issuance currently does not guarantee an account exists until first login, which blocks immediate house assignment for newly onboarded community architects.  
Admins need a flow where they can assign houses to non-admin users right away during onboarding.

## User Stories
- As an admin, I want to assign a house to any non-admin user so that community architect ownership is clear.
- As an admin, I want a placeholder account created when I issue a magic link for a new username so that I can manage that user before first login.
- As an admin, I want to view and update user house assignment in the existing admin user tools so that onboarding and corrections are fast.
- As a community architect, I want my account already tied to the correct house when I first sign in so that my context is correct immediately.

## Core Requirements
- Issuing a magic link must ensure a matching account record exists at issuance time (reuse existing account or create a new placeholder account).
- Admin-only user management must support assigning and updating house for non-admin accounts.
- House values for user assignment must use the existing canonical house options and reject unsupported values.
- Newly created placeholder users must be assignable to a house immediately, without waiting for magic-link redemption.
- Existing auth boundaries must remain intact (only admins can issue links or change other users' house assignments).

## Shared Component Inventory
- `templates/magic_links.html` + `static/js/magic-links.js`: extend the canonical admin magic-link issuance flow to ensure unknown usernames result in immediate managed accounts.
- `POST /api/auth/magic-links` in `app/api_auth.py`: extend existing canonical issuance endpoint so account-creation behavior is consistent for all web-admin issuance.
- `app/magic_link_service.py`: reuse/extend the shared issuance service so account bootstrap behavior remains centralized.
- `scripts/pnl.py` (`./pnl magic-link`): extend CLI issuance path so terminal-based admin issuance follows the same account-bootstrap behavior.
- `templates/users.html` + `static/js/users.js` + `GET /api/auth/users` in `app/api_auth.py`: extend current canonical user-management surface from read-only listing to include house assignment controls for admins.
- `app/house.py`: reuse canonical house normalization/allowed-values source to keep project and user house semantics aligned.

## Simple User Flow
1. Admin opens Magic Login Links and issues a link for a username.
2. If the username is new, the system creates a placeholder account immediately.
3. Admin opens Users and assigns or updates that user's house.
4. User opens the magic link and signs in with the already-created account and assigned house.

## Success Criteria
- Issuing a magic link for an unknown username creates exactly one new user account that appears immediately in Users.
- Admin can assign/update house for a non-admin user, and the value persists after refresh/reload.
- Invalid house assignment attempts are rejected with clear errors and do not change stored user house.
- Non-admin users cannot update other users' house assignments.
- A placeholder account created at issuance is the same account used when the recipient later redeems the magic link.
