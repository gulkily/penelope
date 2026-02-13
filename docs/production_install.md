# Production Install (Single Host, SQLite)

This app currently supports SQLite only. Run a single server process on a single host. See `docs/postgres_migration.md` if you need Postgres.

## 1) System prep
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx
```

## 2) App user + directories
```bash
sudo useradd -m -d /srv/penelope -s /bin/bash penelope
sudo mkdir -p /srv/penelope
sudo chown -R penelope:penelope /srv/penelope
```

## 3) Clone + venv + deps
```bash
sudo -u penelope git clone <REPO_URL> /srv/penelope/app
cd /srv/penelope/app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Environment
```bash
cat > /srv/penelope/app/.env <<'EOF'
DATABASE_URL=sqlite:////srv/penelope/data/north_star.db
DEDALUS_API_KEY=your_key_here
LLM_MODEL=openai/gpt-4o-mini
TRANSCRIPTION_UPLOAD_DIR=/srv/penelope/uploads
TRUSTED_HOSTS=beta.penelope.livetheresidency.com,127.0.0.1,localhost
SESSION_COOKIE_SECURE=true
# Optional:
# SESSION_COOKIE_DOMAIN=beta.penelope.livetheresidency.com
# CORS_ALLOW_ORIGINS=
EOF
```

## 5) Data directories
```bash
sudo mkdir -p /srv/penelope/data /srv/penelope/uploads
sudo chown -R penelope:penelope /srv/penelope/data /srv/penelope/uploads
```

## 6) systemd service
Create `/etc/systemd/system/penelope.service`:
```ini
[Unit]
Description=Penelope FastAPI
After=network.target

[Service]
User=penelope
Group=penelope
WorkingDirectory=/srv/penelope/app
EnvironmentFile=/srv/penelope/app/.env
ExecStart=/srv/penelope/app/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips=127.0.0.1
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
```
Enable + start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable penelope
sudo systemctl start penelope
```

## 7) Reverse proxy + TLS (required for public hosting)
Create `/etc/nginx/sites-available/penelope`:
```nginx
server {
    listen 80;
    server_name beta.penelope.livetheresidency.com;

    client_max_body_size 30M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }
}
```

Enable and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/penelope /etc/nginx/sites-enabled/penelope
sudo nginx -t
sudo systemctl reload nginx
```

Issue TLS cert and enable HTTPS redirect:
```bash
sudo certbot --nginx -d beta.penelope.livetheresidency.com
```

If UFW is enabled:
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
```

## 8) Verify
```bash
curl -I http://127.0.0.1:8000/
curl -I https://beta.penelope.livetheresidency.com/
```

## 9) Upgrade via git
```bash
cd /srv/penelope/app
git fetch --all --tags
git pull --ff-only
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart penelope
```

## 10) Backup
Copy `/srv/penelope/data/north_star.db` (stop the service first), or use the Settings page backup download.
