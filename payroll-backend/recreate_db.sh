#!/bin/bash
# Script para recriar o banco de dados completamente

echo "🗑️  Removendo banco de dados antigo..."
rm -f db.sqlite3

echo "📦 Removendo migrations antigas..."
find migrations -type f -name "*.py" ! -name "__init__.py" -delete

echo "🔨 Criando novas migrations..."
./venv/bin/python manage.py makemigrations

echo "🚀 Aplicando migrations..."
./venv/bin/python manage.py migrate




echo "📊 Populando banco de dados com dados de teste..."
echo "yes" | ./venv/bin/python seed_db_script.py

echo "✅ Banco de dados recriado com sucesso!"
