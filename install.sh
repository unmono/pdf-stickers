#!/bin/bash
RED='\e[31m'
GREEN='\e[32m'
ENDCOLOR='\e[0m'

APP_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PY="python3"

activate_venv() {
  . "$APP_DIR/.venv/bin/activate"
}
exit_prompt() {
  if [ "$2" == 0 ]; then
    MSG_TYPE="${GREEN}Success: ${ENDCOLOR}"
  else
    MSG_TYPE="${RED}Fail: ${ENDCOLOR}"
  fi
  echo -e "${MSG_TYPE}${1}. Press any key to exit...\n"
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
  $PY -m venv "$APP_DIR/.venv" & PID_V=$!
  wait $PID_V
  if [ ! -f "$APP_DIR/.venv/bin/activate" ]; then
    exit_prompt "Failed to setup virtual environment" 1
  fi
fi
if ! (activate_venv && pip install -r "$APP_DIR/requirements.txt"); then
  exit_prompt "Failed to install requirements" 1
fi
exit_prompt "Finished" 0