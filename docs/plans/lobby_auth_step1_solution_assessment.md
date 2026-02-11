# Lobby Auth Step 1: Solution Assessment

## Problem Statement
Add client-generated keypairs, a username prompt, and a lobby-based approval flow (with recorded approvals) before users can access the app.

## Discovery Notes
See `docs/plans/lobby_auth_discovery_notes.md` for the detailed Q&A and constraints captured during discovery.

## Option A: WebCrypto Keypairs + Server-Managed Lobby
Pros:
- No third-party crypto dependency; uses built-in browser WebCrypto.
- Server can verify signatures and manage a clear lobby/approval queue.
- Easy to link multiple keys to one account later.

Cons:
- WebCrypto algorithm support varies (Ed25519 not universal).
- Requires new endpoints and server-side key verification logic.

## Option B: OpenPGP.js Keypairs + Server PGP Verification
Pros:
- Mirrors the Pollyanna approach closely.
- Rich key metadata (user IDs) out of the box.

Cons:
- Heavier client bundle and slower keygen.
- Requires PGP tooling or library server-side.

## Option C: Keypairs + Invite Codes (No Live Lobby)
Pros:
- Simpler to implement (no real-time lobby).
- Works well for private deployments.

Cons:
- Doesn’t match “another user lets them in” requirement.
- Less visibility into waiting users.

## Recommendation
Option A best matches the requirements: browser keypairs, username prompt, and a live lobby queue where authenticated users approve a 6-digit code with approvals recorded server-side. It keeps dependencies light and preserves flexibility for linking multiple keys to a single identity later.
