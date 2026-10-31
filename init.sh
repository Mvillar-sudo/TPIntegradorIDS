#!/bin/bash

# =============================================================================
# Script de inicialización - Centro Médico Salud Integral
# Instala las dependencias del proyecto y prepara el entorno de desarrollo.
# =============================================================================

echo "=== Iniciando instalación del proyecto Centro Médico Salud Integral ==="

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias de Python
echo "Instalando dependencias..."
pip install -r requirements.txt

# Crear archivo .env a partir del template si no existe
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Archivo .env creado a partir de .env.example."
        echo "Configura las variables de entorno en .env antes de iniciar el servidor."
    fi
fi

echo ""
echo "=== Instalación completada ==="
echo "Para activar el entorno virtual:  source .venv/bin/activate"
echo "Para crear la base de datos:      sudo mariadb -u root < database/schema.sql"
echo "Para cargar datos de prueba:      sudo mariadb -u root < database/seeds.sql"
echo "Para iniciar el backend:          cd backend && python app.py"
