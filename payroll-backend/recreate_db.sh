#!/bin/bash
# Script para recriar o banco de dados completamente

echo "🗑️  Removendo banco de dados antigo..."
rm -f db.sqlite3

echo "📦 Removendo migrations antigas..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/.venv/*" -delete

echo "🔨 Criando novas migrations..."
echo "🔨 Criando novas migrations..."
./.venv/bin/python manage.py makemigrations users site_manage app_emails

echo "🚀 Aplicando migrations..."
./.venv/bin/python manage.py migrate




echo "📊 Populando banco de dados com dados de teste..."
echo "yes" | ./.venv/bin/python seed_db_script.py

echo "✅ Banco de dados recriado com sucesso!"
