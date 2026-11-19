#!/bin/bash
# Cria .venv com Python 3.12 + Tcl/Tk (via uv) e instala as dependências.
cd "$(dirname "$0")" || exit 1
if ! command -v uv >/dev/null 2>&1; then
  echo "Instale o uv primeiro: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt \
  && echo "Instalação concluída. Abra Abrir.command para iniciar." \
  || { echo "A instalação falhou. Confira as mensagens acima."; exit 1; }
