#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "배포 실패: line ${LINENO}, command: ${BASH_COMMAND}" >&2' ERR

PROJECT_ROOT="/home/ec2-user/moco"
BACKEND_DIR="/home/ec2-user/moco/backend"
FRONTEND_DIR="/home/ec2-user/moco/frontend"
VENV_DIR="/home/ec2-user/moco/venv"
SERVICE_NAME="moco-gunicorn"

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

health_head() {
  local url="$1"
  curl --fail --silent --show-error --location --max-redirs 3 --head "$url" >/dev/null
}

step "[1/14] Check execution user"
if [[ "$(id -un)" != "ec2-user" ]]; then
  echo "This script should be run as ec2-user. Use sudo only for service commands." >&2
  exit 1
fi

step "[2/14] Check project paths"
require_path "$PROJECT_ROOT/.git"
require_path "$BACKEND_DIR/manage.py"
require_path "$BACKEND_DIR/requirements.txt"
require_path "$FRONTEND_DIR/package.json"
require_path "$FRONTEND_DIR/package-lock.json"
require_path "$VENV_DIR/bin/python"
require_path "$PROJECT_ROOT/.env"

step "[3/14] Check Git status and pull"
cd "$PROJECT_ROOT"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Deployment stopped because the server working tree has local changes." >&2
  git status --short >&2
  exit 1
fi
CURRENT_BRANCH="$(git branch --show-current)"
if [[ -z "$CURRENT_BRANCH" ]]; then
  echo "Deployment stopped because the current Git branch could not be detected." >&2
  exit 1
fi
git pull --ff-only origin "$CURRENT_BRANCH"
CURRENT_COMMIT="$(git rev-parse HEAD)"

step "[4/14] Activate Python virtual environment"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python --version
load_env

step "[5/14] Install Python packages"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "$BACKEND_DIR/requirements.txt"
python -m pip check

step "[6/14] Run Django preflight checks"
cd "$BACKEND_DIR"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan

step "[7/14] Apply database migrations"
python manage.py migrate --noinput

step "[8/14] Install Vue packages"
cd "$FRONTEND_DIR"
node --version
npm --version
npm ci

step "[9/14] Lint and build Vue"
npm run lint
npm run build
require_path "$BACKEND_DIR/templates/home.html"
require_path "$BACKEND_DIR/static/frontend"

step "[10/14] Collect Django static files"
cd "$BACKEND_DIR"
python manage.py collectstatic --noinput

step "[11/14] Restart Gunicorn"
sudo systemctl restart "$SERVICE_NAME"
if ! sudo systemctl is-active --quiet "$SERVICE_NAME"; then
  sudo journalctl -u "$SERVICE_NAME" -n 100 --no-pager >&2
  exit 1
fi

step "[12/14] Validate and reload Nginx"
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl is-active --quiet nginx

step "[13/14] Run local health checks"
health_head "http://127.0.0.1:8000/"
health_head "http://127.0.0.1/"

step "[14/14] Deployment complete"
echo "Commit: $CURRENT_COMMIT"
echo "Branch: $CURRENT_BRANCH"
echo "Gunicorn status: $(sudo systemctl is-active "$SERVICE_NAME")"
echo "Nginx status: $(sudo systemctl is-active nginx)"
echo "Completed at: $(date -Is)"
