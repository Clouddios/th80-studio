#!/bin/bash
# Gera dist/TH80 Studio.app (arm64, assinatura ad hoc). Requer Instalar.command antes.
cd "$(dirname "$0")" || exit 1
uv pip install --python .venv/bin/python pyinstaller || exit 1
.venv/bin/pyinstaller --noconfirm --clean --windowed --name "TH80 Studio" \
  --osx-bundle-identifier io.github.clouddios.th80studio \
  --icon assets/icon.icns --add-data "via-definition.json:." --add-data "assets/icon-256.png:assets" --add-data "assets/sidebar-logo.png:assets" --distpath dist --workpath build app.py \
  && echo "Pronto: dist/TH80 Studio.app"
