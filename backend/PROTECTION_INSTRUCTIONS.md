# Instruções para Aplicar as Proteções aos ViewSets

## Objetivo

Proteger os endpoints existentes (Providers, Payrolls, Dashboard) com:

- Filtros por empresa (multi-tenancy)
- Permissões baseadas em roles
- Isolamento de dados entre empresas

## Arquivos Criados

### 1. `protected_views.py`

Contém as versões protegidas dos ViewSets:

- `ProtectedProviderViewSet`
- `ProtectedPayrollViewSet`
- `ProtectedDashboardView`

## Como Aplicar

### Opção 1: Substituir em views.py (Recomendado)

Abra `api/views.py` e substitua:

```python
# ANTES
class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all().order_by("name")
    serializer_class = ProviderSerializer

# DEPOIS
class ProviderViewSet(viewsets.ModelViewSet):
    """ViewSet protegido para Providers"""
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticated, IsCustomerAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SUPER_ADMIN':
            return Provider.objects.all().order_by('name')
        elif user.role == 'CUSTOMER_ADMIN':
            return Provider.objects.filter(company=user.company).order_by('name')
        elif user.role == 'PROVIDER':
            if hasattr(user, 'provider_profile'):
                return Provider.objects.filter(id=user.provider_profile.id)
            return Provider.objects.none()
        return Provider.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'CUSTOMER_ADMIN':
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()
```

### Opção 2: Importar de protected_views.py

Em `api/urls.py`, altere os imports:

```python
# ANTES
from .views import ProviderViewSet, PayrollViewSet, DashboardView

# DEPOIS
from .protected_views import (
    ProtectedProviderViewSet as ProviderViewSet,
    ProtectedPayrollViewSet as PayrollViewSet,
    ProtectedDashboardView as DashboardView
)
```

## Verificação

Após aplicar, teste:

```bash
# 1. Verificar sistema
python manage.py check

# 2. Iniciar servidor
python manage.py runserver

# 3. Testar endpoints (precisa estar autenticado)
curl -X GET http://localhost:8000/api/providers/ \
  -H "Cookie: access_token=YOUR_TOKEN"
```

## Comportamento Esperado

### Super Admin

- Vê TODOS os providers/payrolls de TODAS as empresas

### Customer Admin

- Vê apenas providers/payrolls da SUA empresa
- Pode criar/editar/deletar providers da sua empresa
- Tem acesso ao dashboard com estatísticas da sua empresa

### Provider

- Vê apenas SEU próprio perfil
- Vê apenas SEUS próprios payrolls
- NÃO tem acesso ao dashboard
