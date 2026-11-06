#!/bin/bash
# Prepara un caso de prueba. Uso: ./caso.sh 1..6   o   ./caso.sh restaurar
set -e
cd "$(dirname "$0")"

# Siempre empezar desde los datos limpios
chmod -R u+rw datos 2>/dev/null || true
rm -rf datos && cp -r datos_copia datos

case "$1" in
  restaurar) echo "Datos restaurados." ;;
  1) mv datos/contactos.dat /tmp/contactos_prueba.dat
     echo "Caso 1: se quitó contactos.dat" ;;
  2) printf 'basura' >> datos/contactos.dat
     echo "Caso 2: 6 bytes extra"; ls -l datos/contactos.dat ;;
  3) sed -i '' 's/Ana López/Ana Lopez /' datos/contactos.dat
     echo "Caso 3: 'Ana López' -> 'Ana Lopez ' (mismo tamaño)"; ls -l datos/contactos.dat ;;
  4) echo 'basura' > datos/indice.json
     echo "Caso 4: índice dañado" ;;
  5) chmod 444 datos/contactos.dat
     echo "Caso 5: solo lectura"; ls -l datos/contactos.dat ;;
  6) chmod 000 datos/contactos.dat
     echo "Caso 6: sin permisos"; ls -l datos/contactos.dat ;;
  *) echo "Uso: ./caso.sh [1-6|restaurar]"; exit 1 ;;
esac