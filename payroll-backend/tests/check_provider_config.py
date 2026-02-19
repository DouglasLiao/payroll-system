import os
import sys
from decimal import Decimal
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from site_manage.models import Provider, Payroll, PayrollItem, ItemType


def check_provider():
    print("=" * 60)
    print("🕵️  CHECAGEM DE CONFIGURAÇÃO DE PRESTADOR")
    print("=" * 60)

    try:
        # Tentar buscar por nome "Douglas" ou "Liao"
        providers = Provider.objects.filter(name__icontains="Douglas")

        if not providers.exists():
            print("❌ Nenhum prestador com nome 'Douglas' encontrado.")
            return

        for p in providers:
            print(f"\n[Prestador ID: {p.id}] {p.name}")
            print(f"  - VT Habilitado (vt_enabled): {p.vt_enabled}")
            print(f"  - Tarifa (vt_fare): {p.vt_fare}")
            print(f"  - Viagens/Dia (vt_trips_per_day): {p.vt_trips_per_day}")

            # Verificar se tem folha recente
            payrolls = Payroll.objects.filter(provider=p).order_by("-created_at")[:1]
            if payrolls.exists():
                last_payroll = payrolls.first()
                print(f"  - Última Folha: {last_payroll.reference_month}")
                print(f"    - absence_days: {last_payroll.absence_days}")
                print(f"    - vt_value: {last_payroll.vt_value}")
                print(f"    - total_discounts: {last_payroll.total_discounts}")

                # Check items
                items = last_payroll.items.filter(
                    type=ItemType.DEBIT, description__icontains="VT"
                )
                if items.exists():
                    for item in items:
                        print(
                            f"    - Item VT encontrado: {item.description} = {item.amount}"
                        )
                else:
                    print(f"    - ⚠️ NENHUM ITEM DE VT ENCONTRADO NA ULTIMA FOLHA.")
            else:
                print("  - Nenhuma folha encontrada.")

            if not p.vt_enabled:
                print(
                    f"  ⚠️ ALERTA: VT está DESABILITADO. O cálculo de estorno não será feito."
                )
            elif p.vt_trips_per_day == 0:
                print(f"  ⚠️ ALERTA: Viagens por dia é ZERO. O cálculo retornará 0.")

    except Exception as e:
        print(f"Erro ao verificar: {e}")


if __name__ == "__main__":
    check_provider()
