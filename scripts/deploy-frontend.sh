#!/usr/bin/env bash
#
# Одна команда для выкладки фронтенда на прод.
#
# Схема прода: статика раздаётся системным nginx из релизной директории
#   /var/www/prostomark-app/app -> releases/<git-sha>
# под путём /app/ (base='/app/' зашит в vite build). Бэкенд (/api/v1) и docker
# этот скрипт НЕ трогает.
#
# Что делает:
#   1. git fetch + reset --hard origin/<ветка>   (по умолчанию main; отключить --no-pull)
#   2. npm ci && npm run build
#   3. копирует dist/ в releases/<sha>
#   4. атомарно переключает симлинки app + current на новый релиз
#   5. чистит старые релизы (оставляет последние KEEP=5)
#   6. reload nginx (если менялся конфиг — не обязательно для статики; см. --reload)
#
# Использование (на сервере, из корня репозитория):
#   ./scripts/deploy-frontend.sh              # обычная выкладка main
#   ./scripts/deploy-frontend.sh --no-pull    # собрать текущий checkout без git reset
#   ./scripts/deploy-frontend.sh --reload     # ещё и reload nginx
#
# Требует sudo для записи в /var/www (скрипт вызывает sudo сам по мере надобности).

set -euo pipefail

# ── Настройки (можно переопределить через env) ───────────────────────────────
REPO_DIR="${REPO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
WWW_ROOT="${WWW_ROOT:-/var/www/prostomark-app}"
BRANCH="${BRANCH:-main}"
KEEP="${KEEP:-5}"

PULL=1
RELOAD=0
for arg in "$@"; do
  case "$arg" in
    --no-pull) PULL=0 ;;
    --reload)  RELOAD=1 ;;
    *) echo "Неизвестный аргумент: $arg" >&2; exit 2 ;;
  esac
done

log() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

cd "$REPO_DIR"

if [[ "$PULL" -eq 1 ]]; then
  log "git fetch + reset --hard origin/$BRANCH"
  git fetch origin "$BRANCH"
  git reset --hard "origin/$BRANCH"
fi

SHA="$(git rev-parse HEAD)"
log "Коммит: $SHA"

log "Сборка фронтенда (npm ci && npm run build)"
cd "$REPO_DIR/frontend"
npm ci
npm run build   # base=/app/ зашит для production

if [[ ! -f dist/index.html ]]; then
  echo "Ошибка: dist/index.html не найден — сборка не удалась" >&2
  exit 1
fi

REL="$WWW_ROOT/releases/$SHA"
log "Копирую dist -> $REL"
sudo rm -rf "$REL"
sudo mkdir -p "$REL"
sudo cp -a dist/. "$REL"/

log "Переключаю симлинки app + current (атомарно)"
sudo ln -sfn "$REL" "$WWW_ROOT/app.tmp" && sudo mv -Tf "$WWW_ROOT/app.tmp" "$WWW_ROOT/app"
sudo ln -sfn "$REL" "$WWW_ROOT/current.tmp" && sudo mv -Tf "$WWW_ROOT/current.tmp" "$WWW_ROOT/current"

log "Чищу старые релизы (оставляю $KEEP последних)"
# Сохраняем текущий целевой релиз + последние по времени; остальное удаляем.
CURRENT_TARGET="$(readlink -f "$WWW_ROOT/current")"
mapfile -t OLD < <(ls -1dt "$WWW_ROOT"/releases/*/ 2>/dev/null | tail -n +$((KEEP + 1)))
for dir in "${OLD[@]:-}"; do
  [[ -z "$dir" ]] && continue
  [[ "$(readlink -f "$dir")" == "$CURRENT_TARGET" ]] && continue
  sudo rm -rf "$dir"
done

if [[ "$RELOAD" -eq 1 ]]; then
  log "nginx -t && reload"
  sudo nginx -t && sudo systemctl reload nginx
fi

log "Готово. Активный релиз: $(readlink -f "$WWW_ROOT/app")"
echo
echo "Проверка:"
echo "  curl -sI https://app.prostomark.ru/app/ | grep -i cache-control"
echo "  curl -sI https://app.prostomark.ru/app/dashboard | head -1"
