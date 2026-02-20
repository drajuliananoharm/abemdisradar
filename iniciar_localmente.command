#!/bin/bash
cd "$(dirname "$0")"
echo "Iniciando um servidor local para visualizar o Radar de Editais..."
echo "O seu navegador padrão abrirá automaticamente."
sleep 1
open "http://localhost:8000"
python3 -m http.server 8000
