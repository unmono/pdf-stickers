#!/bin/bash
APP_DIR="$(cd "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
activate() {
  . "$APP_DIR/.venv/bin/activate"
}
activate
cd "$APP_DIR" || exit 1
setsid -f python3 -m ui
exit 0