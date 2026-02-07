"""
Serviço de geração de arquivos CSV para folhas de pagamento.
Substitui o antigo ExcelService conforme solicitação de uso de formatos abertos.
"""

import csv
from io import StringIO
from decimal import Decimal
import unicodedata


class CsvService:
    """Serviço para geração de arquivos CSV de folhas de pagamento."""

    def __init__(self):
        self.output = StringIO()
        self.output.write("sep=;\n")
        self.writer = csv.writer(self.output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    @staticmethod
    def _format_currency(value):
        """
        Formata valor Decimal para string em formato brasileiro.
        """
        if value is None:
            return "0,00"

        # Converter para float para formatação
        float_value = float(value)

        # Formatar com separadores brasileiros
        return (
            f"{float_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def generate_payroll_csv(self, payroll):
        """
        Gera um arquivo CSV completo para a folha de pagamento.
        """
        # Cabeçalho
        self.writer.writerow(["FOLHA DE PAGAMENTO"])
        self.writer.writerow([f"Mês de Referência: {payroll.reference_month}"])
        self.writer.writerow([])

        # Dados do Prestador
        self.writer.writerow(["DADOS DO PRESTADOR"])
        self.writer.writerow(["Nome:", payroll.provider.name])
        self.writer.writerow(["Função:", payroll.provider.role])
        self.writer.writerow(
            ["Salário Base Mensal:", self._format_currency(payroll.base_value)]
        )
        self.writer.writerow(
            ["Valor por Hora:", self._format_currency(payroll.hourly_rate)]
        )
        self.writer.writerow([])

        # Proventos
        self.writer.writerow(["PROVENTOS"])
        self.writer.writerow(["Descrição", "Valor"])

        self.writer.writerow(
            [
                "Salário base (após adiantamento)",
                self._format_currency(payroll.remaining_value),
            ]
        )

        if payroll.overtime_hours_50 > 0:
            self.writer.writerow(
                [
                    f"Horas extras 50% ({payroll.overtime_hours_50}h)",
                    self._format_currency(payroll.overtime_amount),
                ]
            )

        if payroll.holiday_hours > 0:
            self.writer.writerow(
                [
                    f"Feriados trabalhados ({payroll.holiday_hours}h)",
                    self._format_currency(payroll.holiday_amount),
                ]
            )

        if payroll.dsr_amount > 0:
            self.writer.writerow(
                [
                    "DSR (Descanso Semanal Remunerado)",
                    self._format_currency(payroll.dsr_amount),
                ]
            )

        if payroll.night_hours > 0:
            self.writer.writerow(
                [
                    f"Adicional noturno ({payroll.night_hours}h)",
                    self._format_currency(payroll.night_shift_amount),
                ]
            )

        self.writer.writerow(
            ["TOTAL PROVENTOS", self._format_currency(payroll.total_earnings)]
        )
        self.writer.writerow([])

        # Descontos
        self.writer.writerow(["DESCONTOS"])
        self.writer.writerow(["Descrição", "Valor"])

        self.writer.writerow(
            [
                f"Adiantamento quinzenal ({float(payroll.advance_value / payroll.base_value * 100):.0f}%)",
                self._format_currency(payroll.advance_value),
            ]
        )

        if payroll.late_minutes > 0:
            self.writer.writerow(
                [
                    f"Atrasos ({payroll.late_minutes} minutos)",
                    self._format_currency(payroll.late_discount),
                ]
            )

        if payroll.absence_hours > 0:
            self.writer.writerow(
                [
                    f"Faltas ({payroll.absence_hours}h)",
                    self._format_currency(payroll.absence_discount),
                ]
            )

        if payroll.vt_discount > 0:
            self.writer.writerow(
                ["Vale transporte", self._format_currency(payroll.vt_discount)]
            )

        if payroll.manual_discounts > 0:
            self.writer.writerow(
                ["Descontos manuais", self._format_currency(payroll.manual_discounts)]
            )

        self.writer.writerow(
            ["TOTAL DESCONTOS", self._format_currency(payroll.total_discounts)]
        )
        self.writer.writerow([])

        # Valor Líquido
        self.writer.writerow(
            ["VALOR LÍQUIDO A PAGAR", self._format_currency(payroll.net_value)]
        )
        self.writer.writerow([])

        # Observações
        if payroll.advance_value > 0:
            self.writer.writerow(
                [
                    f"Nota: Adiantamento de {self._format_currency(payroll.advance_value)} já foi pago anteriormente."
                ]
            )

        if payroll.notes:
            self.writer.writerow(["Observações:", payroll.notes])

        self.writer.writerow([])
        self.writer.writerow(
            ["Documento gerado automaticamente pelo Sistema de Folha de Pagamento PJ"]
        )

        # Retornar valor do StringIO
        return self.output.getvalue().encode(
            "utf-8-sig"
        )  # UTF-8 com BOM para Excel abrir corretamente acentos

    @staticmethod
    def get_filename(payroll):
        """
        Gera nome do arquivo CSV.
        """
        # Normalizar nome do prestador
        provider_name = payroll.provider.name.lower()
        provider_name = unicodedata.normalize("NFKD", provider_name)
        provider_name = provider_name.encode("ascii", "ignore").decode("ascii")
        provider_name = provider_name.replace(" ", "_")

        # Normalizar mês
        month = payroll.reference_month.replace("/", "_")

        return f"folha_{provider_name}_{month}.csv"
