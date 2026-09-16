#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/4] Validando sintaxe Python..."
python -m compileall -q app tests

echo "[2/4] Validando JavaScript principal..."
if command -v node >/dev/null 2>&1; then
  node --check app/static/js/modules/payment/payment.events.js
  node --check app/static/js/modules/payment/payment.actions.js
  node --check app/static/js/modules/production/production.actions.js
  node --check app/static/js/modules/report/analytics.js
else
  echo "Aviso: Node.js não encontrado; validação JS ignorada."
fi

echo "[3/4] Executando testes automatizados..."
python -m pytest -q

echo "[4/4] Verificação concluída."
echo "WorkFlow estático + testes automatizados: OK"
