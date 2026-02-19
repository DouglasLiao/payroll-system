import io
import logging
import csv
from decimal import Decimal
from datetime import datetime

from site_manage.models import Payroll

logger = logging.getLogger(__name__)


class ReportService:
    def generate_monthly_summary(self, company_id, reference_month):
        """
        Gera um relatório CSV com o resumo das folhas de pagamento de um mês específico.
        """
        logger.info(
            f"Iniciando geracao de relatorio CSV para empresa {company_id} e mes {reference_month}"
        )

        if not reference_month:
            logger.error("Mes de referencia nao fornecido")
            raise ValueError("Mês de referência não fornecido")

        try:
            ref_date = datetime.strptime(reference_month, "%m/%Y")
            now = datetime.now()
            current_month_start = datetime(now.year, now.month, 1)

            if ref_date >= current_month_start:
                logger.warning(
                    f"Tentativa de gerar relatorio para mes nao encerrado: {reference_month}"
                )
                raise ValueError(
                    "Relatórios só podem ser gerados para meses encerrados."
                )
        except ValueError as e:
            if "Relatórios" in str(e):
                raise
            logger.error(f"Erro de formato de data: {e}")
            raise ValueError("Formato de data inválido. Use MM/YYYY")

        # 1. Buscar dados
        payrolls = (
            Payroll.objects.filter(
                provider__company_id=company_id, reference_month=reference_month
            )
            .select_related("provider")
            .order_by("provider__name")
        )

        count = payrolls.count()
        logger.info(f"Encontrados {count} payrolls para o periodo")

        if count == 0:
            logger.warning("Nenhum dado encontrado para o periodo")

        # 2. Criar Buffer CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        # 3. Cabeçalho
        headers = [
            "Prestador",
            "Função",
            "Mês Ref.",
            "Status",
            "Valor Base",
            "Proventos",
            "Descontos",
            "Valor Líquido",
            "Pago Em",
        ]
        writer.writerow(headers)

        # 4. Dados
        total_gross = Decimal("0.00")
        total_earnings = Decimal("0.00")
        total_discounts = Decimal("0.00")
        total_net = Decimal("0.00")

        for payroll in payrolls:
            # Acumular totais
            total_gross += payroll.base_value
            total_earnings += payroll.total_earnings
            total_discounts += payroll.total_discounts
            total_net += payroll.net_value

            # Format values
            base_str = f"{payroll.base_value:.2f}".replace(".", ",")
            earn_str = f"{payroll.total_earnings:.2f}".replace(".", ",")
            disc_str = f"{payroll.total_discounts:.2f}".replace(".", ",")
            net_str = f"{payroll.net_value:.2f}".replace(".", ",")
            paid_at = payroll.paid_at.strftime("%d/%m/%Y") if payroll.paid_at else "-"

            writer.writerow(
                [
                    payroll.provider.name,
                    payroll.provider.role,
                    payroll.reference_month,
                    payroll.get_status_display(),
                    base_str,
                    earn_str,
                    disc_str,
                    net_str,
                    paid_at,
                ]
            )

        # 5. Linha de Totais
        writer.writerow([])  # Empty line
        writer.writerow(
            [
                "TOTAIS",
                "",
                "",
                "",
                f"{total_gross:.2f}".replace(".", ","),
                f"{total_earnings:.2f}".replace(".", ","),
                f"{total_discounts:.2f}".replace(".", ","),
                f"{total_net:.2f}".replace(".", ","),
                "",
            ]
        )

        # 6. Retornar Buffer Bytes
        # Convert StringIO to BytesIO for consistency with previous return type
        bytes_output = io.BytesIO()
        bytes_output.write(output.getvalue().encode("utf-8-sig"))  # BOM for Excel
        bytes_output.seek(0)
        return bytes_output

    def get_filename(self, reference_month):
        month_str = reference_month.replace("/", "-")
        return f"relatorio_mensal_{month_str}.csv"
