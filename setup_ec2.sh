#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "배포 실패: line ${LINENO}, command: ${BASH_COMMAND}" >&2' ERR

PROJECT_ROOT="/home/ec2-user/moco"
BACKEND_DIR="/home/ec2-user/moco/backend"
FRONTEND_DIR="/home/ec2-user/moco/frontend"
VENV_DIR="/home/ec2-user/moco/venv"
SERVICE_NAME="moco-gunicorn"
REPO_URL="${1:-${REPO_URL:-git@github.com:hanzeenee/moco.git}}"
PYTHON_SOURCE_VERSION="3.12.9"
NVM_VERSION="v0.40.1"

step() {
  echo
  echo "$1"
}

require_path() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "Required path is missing: $path" >&2
    exit 1
  fi
}

load_env() {
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
}

install_python312_from_source() {
  local src_dir="/usr/local/src/Python-${PYTHON_SOURCE_VERSION}"
  local tarball="/usr/local/src/Python-${PYTHON_SOURCE_VERSION}.tgz"

  if command -v python3.12 >/dev/null 2>&1; then
    return
  fi

  sudo curl -fsSL "https://www.python.org/ftp/python/${PYTHON_SOURCE_VERSION}/Python-${PYTHON_SOURCE_VERSION}.tgz" -o "$tarball"
  sudo tar -xzf "$tarball" -C /usr/local/src
  cd "$src_dir"
  sudo ./configure --enable-optimizations
  sudo make altinstall
}

step "[1/15] Check operating system"
cat /etc/os-release
# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != "amzn" ]]; then
  echo "Unsupported OS. This script supports Amazon Linux 2023 and Amazon Linux 2 only." >&2
  exit 1
fi
if [[ "${VERSION_ID:-}" == "2023" ]]; then
  OS_FAMILY="AL2023"
elif [[ "${VERSION_ID:-}" == "2" ]]; then
  OS_FAMILY="AL2"
else
  echo "Unsupported Amazon Linux version: ${VERSION_ID:-unknown}" >&2
  exit 1
fi

step "[2/15] Install required system packages"
if [[ "$OS_FAMILY" == "AL2023" ]]; then
  sudo dnf install -y git curl wget nginx gcc gcc-c++ make openssl-devel libffi-devel zlib-devel bzip2-devel readline-devel sqlite-devel xz-devel tk-devel tar gzip
  if ! command -v python3.12 >/dev/null 2>&1; then
    sudo dnf install -y python3.12 python3.12-devel || install_python312_from_source
  fi
else
  sudo yum install -y git curl wget nginx gcc gcc-c++ make openssl-devel libffi-devel zlib-devel bzip2-devel readline-devel sqlite-devel xz-devel tk-devel tar gzip
  install_python312_from_source
fi

step "[3/15] Check Python 3.12"
python3.12 --version

step "[4/15] Install Node.js 20 LTS with nvm for ec2-user"
if [[ "$(id -un)" != "ec2-user" ]]; then
  echo "Run this script as ec2-user, not root." >&2
  exit 1
fi
export NVM_DIR="/home/ec2-user/.nvm"
if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
  curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh" | bash
fi
# shellcheck disable=SC1091
source "$NVM_DIR/nvm.sh"
nvm install 20
nvm alias default 20
nvm use 20
node --version
npm --version

step "[5/15] Enable Nginx"
sudo systemctl enable nginx

step "[6/15] Prepare repository"
if [[ -d "$PROJECT_ROOT/.git" ]]; then
  echo "Repository already exists: $PROJECT_ROOT"
else
  if [[ -e "$PROJECT_ROOT" ]]; then
    echo "$PROJECT_ROOT exists but is not a Git repository." >&2
    exit 1
  fi
  git clone "$REPO_URL" "$PROJECT_ROOT"
fi
sudo chown -R ec2-user:ec2-user "$PROJECT_ROOT"
require_path "$BACKEND_DIR/manage.py"
require_path "$BACKEND_DIR/requirements.txt"
require_path "$FRONTEND_DIR/package.json"
require_path "$FRONTEND_DIR/package-lock.json"

step "[7/15] Create Python virtual environment"
if [[ -d "$VENV_DIR" ]]; then
  VENV_VERSION="$("$VENV_DIR/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  if [[ "$VENV_VERSION" != "3.12" ]]; then
    echo "Existing virtualenv uses Python $VENV_VERSION, not 3.12. Stop and recreate it manually if intended." >&2
    exit 1
  fi
else
  python3.12 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" --version

step "[8/15] Install Python requirements"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -r "$BACKEND_DIR/requirements.txt"
"$VENV_DIR/bin/python" -m pip check

step "[9/15] Install Vue dependencies and build"
cd "$FRONTEND_DIR"
npm ci
npm run lint
npm run build
require_path "$BACKEND_DIR/templates/home.html"
require_path "$BACKEND_DIR/static/frontend"

step "[10/15] Check environment file"
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  echo "Missing $PROJECT_ROOT/.env" >&2
  echo "Create it from the example, fill real production values, then rerun:" >&2
  echo "  cp .env.example .env" >&2
  echo "  chmod 600 .env" >&2
  exit 1
fi
chmod 600 "$PROJECT_ROOT/.env"
load_env

step "[11/15] Initialize Django"
cd "$BACKEND_DIR"
"$VENV_DIR/bin/python" manage.py check
"$VENV_DIR/bin/python" manage.py makemigrations --check --dry-run
"$VENV_DIR/bin/python" manage.py migrate --noinput
"$VENV_DIR/bin/python" manage.py collectstatic --noinput

step "[12/15] Install systemd service"
sudo install -m 644 "$PROJECT_ROOT/deploy/moco-gunicorn.service" /etc/systemd/system/moco-gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl is-active --quiet "$SERVICE_NAME"

step "[13/15] Install Nginx configuration"
sudo install -m 644 "$PROJECT_ROOT/deploy/moco.conf" /etc/nginx/conf.d/moco.conf
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl is-active --quiet nginx

step "[14/15] Check services and local HTTP"
sudo systemctl status "$SERVICE_NAME" --no-pager
sudo systemctl status nginx --no-pager
curl -I http://127.0.0.1:8000/
curl -I http://127.0.0.1/
sudo ss -lntp

step "[15/15] Check permissions"
chmod 750 "$PROJECT_ROOT/deploy.sh" "$PROJECT_ROOT/setup_ec2.sh" || true
mkdir -p "$BACKEND_DIR/media"
chmod 755 "$BACKEND_DIR/staticfiles" "$BACKEND_DIR/media" 2>/dev/null || true
HOME_MODE="$(stat -c '%a' /home/ec2-user)"
if [[ "$HOME_MODE" != "711" && "$HOME_MODE" != "755" && "$HOME_MODE" != "751" ]]; then
  echo "/home/ec2-user mode is $HOME_MODE. If Nginx cannot read static/media files, run: chmod 711 /home/ec2-user"
fi

echo
echo "Initial EC2 setup completed at $(date -Is)"
