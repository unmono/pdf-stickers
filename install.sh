#!/bin/bash
APP_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PY="python3"

activate_venv() {
  . "$APP_DIR/.venv/bin/activate"
}
exit_prompt() {
  printf "%s. Press any key to exit...\n" "$1"
  read -n 1 -s -r -p ""
  exit "$2"
}

while getopts "p:" opt; do
  case ${opt} in
    p)
      export PY="${OPTARG}"
      ;;
    ?)
      exit_prompt "Invalid argument" 1
      ;;
  esac
done
if ! [ -d "$APP_DIR/.venv" ]; then
  if ! ($PY -m venv "$APP_DIR/.venv" & pidV=$! && wait $pidV); then
   exit_prompt "Failed to setup virtual environment" 1
  fi
fi
if ! (activate_venv && pip install -r "$APP_DIR/requirements.txt"); then
  exit_prompt "Failed to install requirements" 1
fi
exit_prompt "Finished" 0