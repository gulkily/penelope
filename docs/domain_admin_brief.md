# Domain Admin Brief (DNS, TLS, CORS)

This app runs behind a reverse proxy (Nginx or Caddy). The app itself listens on `127.0.0.1:8000`. DNS + TLS terminate at the proxy.

## DNS
Create a subdomain record for the app.
- If pointing directly to a public server IP:
  - Add an `A` record: `app` → `<PUBLIC_IPV4>`
  - Add an `AAAA` record (optional): `app` → `<PUBLIC_IPV6>`
- If pointing to another hostname (load balancer):
  - Add a `CNAME` record: `app` → `<TARGET_HOSTNAME>`

TTL: default/auto is fine. Propagation is usually minutes but can take longer.

## TLS (HTTPS)
We want HTTPS on the subdomain (example `app.example.com`).
- Use a public certificate from Let’s Encrypt (domain required).
- Terminate TLS at the reverse proxy.
- The app itself stays on HTTP (loopback) behind the proxy.

If public HTTPS is not needed (private LAN only), TLS can be omitted or use an internal CA/self-signed cert.

## CORS
If the frontend and API share the same origin (same scheme/host/port), CORS is not required.
If the frontend is served from a different origin, we must allow that origin in FastAPI via `CORSMiddleware`.

## Reverse Proxy Notes (for whoever manages the server)
- Forward to `http://127.0.0.1:8000`.
- Preserve headers: `Host`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Allow request bodies up to 30MB (transcription uploads).
