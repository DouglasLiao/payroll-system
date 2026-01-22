#!/bin/bash
# Script para recriar o banco de dados completamente

echo "🗑️  Removendo banco de dados antigo..."
rm -f db.sqlite3

echo "📦 Removendo migrations antigas..."
find api/migrations -type f -name "*.py" ! -name "__init__.py" -delete

echo "🔨 Criando novas migrations..."
./venv/bin/python manage.py makemigrations

echo "🚀 Aplicando migrations..."
./venv/bin/python manage.py migrate

echo "👤 Criando superuser..."
echo "from api.models import User; User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')" | ./venv/bin/python manage.py shell

echo "📊 Populando banco de dados com dados de teste..."
./venv/bin/python populate_db.py

echo "✅ Banco de dados recriado com sucesso!"
