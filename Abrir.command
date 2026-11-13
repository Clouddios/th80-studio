#!/bin/bash
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
  echo "Execute Instalar.command antes de abrir o app."
  exit 1
fi
exec .venv/bin/python app.py
