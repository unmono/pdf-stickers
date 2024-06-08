#!/bin/bash
APP_DIR="$(cd "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
activate() {
  . "$APP_DIR/.venv/bin/activate"
}
activate
if ! python3 -c "import tkinter"; then
  echo "Tkinter required but not installed."
else
  cd "$APP_DIR" || exit 1
  echo $$
  setsid -f python3 -m ui
  exit 0
fi