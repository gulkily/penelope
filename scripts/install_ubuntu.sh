#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

prompt() {
  local message="$1"
  local default="${2:-}"
  local value=""
  if [[ -n "${default}" ]]; then
    read -rp "${message} [${default}]: " value
    echo "${value:-$default}"
  else
    read -rp "${message}: " value
    echo "${value}"
  fi
}

prompt_secret() {
  local message="$1"
  local value=""
  read -rsp "${message} (leave blank to skip): " value
  echo
  echo "${value}"
}

confirm() {
  local message="$1"
  local default="${2:-y}"
  local prompt_suffix="[y/N]"
  if [[ "${default}" == "y" ]]; then
    prompt_suffix="[Y/n]"
  fi
  local value=""
  read -rp "${message} ${prompt_suffix}: " value
  value="${value:-$default}"
  [[ "${value}" =~ ^[Yy]$ ]]
}

ensure_sudo() {
  if ! command -v sudo >/dev/null 2>&1; then
    echo "This script requires sudo for system package installation."
    exit 1
  fi
}

ensure_dir() {
  local path="$1"
  if mkdir -p "${path}" 2>/dev/null; then
    return 0
  fi
  ensure_sudo
  sudo mkdir -p "${path}"
  sudo chown -R "${USER}:${USER}" "${path}"
}

check_os() {
  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    if [[ "${ID:-}" != "ubuntu" && "${ID_LIKE:-}" != *ubuntu* ]]; then
      echo "Warning: This script is intended for Ubuntu. Detected: ${ID:-unknown}."
      if ! confirm "Continue anyway?" "n"; then
        exit 1
      fi
    fi
  fi
}

install_system_packages() {
  ensure_sudo
  sudo apt-get update
  sudo apt-get install -y python3 python3-venv python3-pip git
}

clone_or_use_repo() {
  local app_dir=""

  if [[ -d "${REPO_ROOT}/.git" ]] && confirm "Use the current repo at ${REPO_ROOT}?" "y"; then
    app_dir="${REPO_ROOT}"
  else
    local repo_url=""
    while [[ -z "${repo_url}" ]]; do
      repo_url="$(prompt "Git repo URL")"
    done
    local default_dir="${HOME}/penelope/app"
    app_dir="$(prompt "Install directory" "${default_dir}")"
    ensure_dir "${app_dir%/*}"

    if [[ -d "${app_dir}/.git" ]]; then
      echo "Repo already exists at ${app_dir}."
      if confirm "Pull latest changes?" "y"; then
        git -C "${app_dir}" fetch --all --tags
        git -C "${app_dir}" pull --ff-only
      fi
    else
      if [[ -d "${app_dir}" && -n "$(ls -A "${app_dir}" 2>/dev/null || true)" ]]; then
        echo "Directory ${app_dir} is not empty."
        if ! confirm "Continue and clone into it?" "n"; then
          exit 1
        fi
      fi
      git clone "${repo_url}" "${app_dir}"
    fi
  fi

  echo "${app_dir}"
}

setup_venv() {
  local app_dir="$1"
  if [[ ! -d "${app_dir}/.venv" ]]; then
    python3 -m venv "${app_dir}/.venv"
  fi
  # shellcheck disable=SC1090
  source "${app_dir}/.venv/bin/activate"
  python3 -m pip install -r "${app_dir}/requirements.txt"
}

write_env_file() {
  local app_dir="$1"
  local env_path="${app_dir}/.env"
  if [[ -f "${env_path}" ]] && ! confirm "Overwrite existing .env?" "n"; then
    return 0
  fi

  local default_db_url="sqlite:///${app_dir}/data/north_star.db"
  local database_url
  database_url="$(prompt "DATABASE_URL" "${default_db_url}")"
  local dedalus_api_key
  dedalus_api_key="$(prompt_secret "DEDALUS_API_KEY")"
  local llm_model
  llm_model="$(prompt "LLM_MODEL" "openai/gpt-4o-mini")"
  local upload_dir
  upload_dir="$(prompt "TRANSCRIPTION_UPLOAD_DIR" "${app_dir}/uploads")"

  {
    echo "DATABASE_URL=${database_url}"
    if [[ -n "${dedalus_api_key}" ]]; then
      echo "DEDALUS_API_KEY=${dedalus_api_key}"
    fi
    if [[ -n "${llm_model}" ]]; then
      echo "LLM_MODEL=${llm_model}"
    fi
    if [[ -n "${upload_dir}" ]]; then
      echo "TRANSCRIPTION_UPLOAD_DIR=${upload_dir}"
    fi
  } > "${env_path}"

  echo "${upload_dir}"
}

create_service() {
  local app_dir="$1"
  local service_name="$2"
  local service_path="/etc/systemd/system/${service_name}.service"

  ensure_sudo
  sudo tee "${service_path}" >/dev/null <<EOF
[Unit]
Description=Penelope FastAPI
After=network.target

[Service]
User=${USER}
Group=${USER}
WorkingDirectory=${app_dir}
EnvironmentFile=${app_dir}/.env
ExecStart=${app_dir}/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable "${service_name}"
  sudo systemctl start "${service_name}"
}

main() {
  check_os

  if confirm "Install/upgrade system packages (python3, venv, pip, git)?" "y"; then
    install_system_packages
  fi

  local app_dir
  app_dir="$(clone_or_use_repo)"

  ensure_dir "${app_dir}/data"
  ensure_dir "${app_dir}/uploads"

  setup_venv "${app_dir}"

  local upload_dir=""
  if confirm "Create or update .env?" "y"; then
    upload_dir="$(write_env_file "${app_dir}")"
    if [[ -n "${upload_dir}" ]]; then
      ensure_dir "${upload_dir}"
    fi
  fi

  if confirm "Create and start a systemd service?" "n"; then
    local service_name
    service_name="$(prompt "Service name" "penelope")"
    create_service "${app_dir}" "${service_name}"
  else
    echo "Setup complete."
    echo "To run locally:"
    echo "  cd ${app_dir}"
    echo "  source .venv/bin/activate"
    echo "  ./start.sh"
  fi
}

main "$@"
