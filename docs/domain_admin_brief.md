# Domain Admin Brief (DNS, TLS, CORS)

Target public hostname: `beta.penelope.livetheresidency.com`

This app should run behind a reverse proxy (Nginx or Caddy). The app itself listens on `127.0.0.1:8000`. DNS + TLS terminate at the proxy.

## DNS
Create records for `beta.penelope`.
- If pointing directly to your server IP:
  - `A` record: `beta.penelope` → `<PUBLIC_IPV4>`
  - `AAAA` record (optional): `beta.penelope` → `<PUBLIC_IPV6>`
- If pointing to another hostname (load balancer):
  - `CNAME` record: `beta.penelope` → `<TARGET_HOSTNAME>`

TTL: default/auto is fine. Propagation is usually minutes but can take longer.

## TLS (HTTPS)
We want HTTPS on `beta.penelope.livetheresidency.com`.
- Use a public certificate from Let’s Encrypt (domain required).
- Terminate TLS at the reverse proxy.
- The app itself stays on HTTP (loopback) behind the proxy.

## App Config for Public Host
Set these in `.env` on the server:
- `TRUSTED_HOSTS=beta.penelope.livetheresidency.com,127.0.0.1,localhost`
- `SESSION_COOKIE_SECURE=true`
- Optional: `SESSION_COOKIE_DOMAIN=beta.penelope.livetheresidency.com`

## CORS
If the frontend and API share the same origin (same scheme/host/port), CORS is not required.
If the frontend is served from a different origin, set `CORS_ALLOW_ORIGINS` in `.env` (comma-separated origins).

## Reverse Proxy Notes (for whoever manages the server)
- Forward to `http://127.0.0.1:8000`.
- Preserve headers: `Host`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Allow request bodies up to 30MB (transcription uploads).
