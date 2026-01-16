"""
Comando Django para popular o banco de dados com dados de teste.

Cria 50+ prestadores PJ e folhas de pagamento de 2020 até 2026.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random
from datetime import datetime
from api.models import Provider, Payroll, PayrollStatus
from services.payroll_service import PayrollService


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fictícios de prestadores e folhas de pagamento'
    
    # Nomes brasileiros fictícios
    FIRST_NAMES = [
        'João', 'Maria', 'José', 'Ana', 'Pedro', 'Carlos', 'Paulo', 'Lucas',
        'Mariana', 'Juliana', 'Rafael', 'Gabriel', 'Fernanda', 'Beatriz',
        'Felipe', 'Bruno', 'Amanda', 'Camila', 'Diego', 'Thiago', 'Rodrigo',
        'Larissa', 'Tatiana', 'Marcelo', 'Ricardo', 'Renata', 'Cristina',
        'Fernando', 'Gustavo', 'Henrique', 'Isabella', 'Julia', 'Leonardo',
        'Marcos', 'Patricia', 'Roberta', 'Sergio', 'Vanessa', 'William',
        'André', 'Bruna', 'Carolina', 'Daniel', 'Eduardo', 'Fabiana',
        'Guilherme', 'Heloisa', 'Igor', 'Jessica', 'Kevin', 'Leticia'
    ]
    
    LAST_NAMES = [
        'Silva', 'Santos', 'Souza', 'Oliveira', 'Lima', 'Pereira', 'Costa',
        'Rodrigues', 'Almeida', 'Nascimento', 'Araújo', 'Melo', 'Barbosa',
        'Ribeiro', 'Martins', 'Carvalho', 'Rocha', 'Ferreira', 'Gomes',
        'Dias', 'Castro', 'Pinto', 'Teixeira', 'Monteiro', 'Cardoso',
        'Mendes', 'Nunes', 'Moreira', 'Ramos', 'Cavalcanti', 'Correia'
    ]
    
    ROLES = [
        'Desenvolvedor Backend',
        'Desenvolvedor Frontend',
        'Desenvolvedor Full Stack',
        'Designer UX/UI',
        'Analista de Dados',
        'Engenheiro DevOps',
        'Gerente de Projetos',
        'Analista de Sistemas',
        'Arquiteto de Software',
        'Cientista de Dados',
        'Analista de QA',
        'Product Manager',
        'Scrum Master',
        'Tech Lead',
        'Consultor de TI'
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--providers',
            type=int,
            default=50,
            help='Número de prestadores a criar (padrão: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa dados existentes antes de popular'
        )
    
    def handle(self, *args, **options):
        num_providers = options['providers']
        clear_data = options['clear']
        
        if clear_data:
            self.stdout.write(self.style.WARNING('Limpando dados existentes...'))
            Payroll.objects.all().delete()
            Provider.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Dados limpos!'))
        
        self.stdout.write(
            self.style.SUCCESS(f'Criando {num_providers} prestadores...')
        )
        
        providers = self.create_providers(num_providers)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {len(providers)} prestadores criados!')
        )
        
        self.stdout.write(
            self.style.SUCCESS('Criando folhas de pagamento (2020-2026)...')
        )
        
        total_payrolls = self.create_payrolls(providers)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {total_payrolls} folhas de pagamento criadas!')
        )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Banco de dados populado com sucesso!')
        )
        
        # Estatísticas
        self.show_statistics()
    
    def create_providers(self, count):
        """Cria prestadores fictícios."""
        providers = []
        used_names = set()
        
        for i in range(count):
            # Gerar nome único
            while True:
                first = random.choice(self.FIRST_NAMES)
                last = random.choice(self.LAST_NAMES)
                name = f"{first} {last}"
                if name not in used_names:
                    used_names.add(name)
                    break
            
            # Valores variados (R$ 1.500 a R$ 15.000)
            monthly_value = Decimal(random.randint(1500, 15000))
            
            # Carga horária (160h, 176h ou 220h)
            monthly_hours = random.choice([160, 176, 220])
            
            # Adiantamento (30%, 40% ou 50%)
            advance_percentage = Decimal(random.choice([30, 40, 50]))
            
            # Vale transporte (R$ 0 a R$ 300)
            vt_value = Decimal(random.randint(0, 300))
            
            # Alguns sem adiantamento
            advance_enabled = random.random() > 0.1  # 90% com adiantamento
            
            provider = Provider.objects.create(
                name=name,
                role=random.choice(self.ROLES),
                monthly_value=monthly_value,
                monthly_hours=monthly_hours,
                advance_enabled=advance_enabled,
                advance_percentage=advance_percentage,
                vt_value=vt_value,
                payment_method=random.choice(['PIX', 'TED', 'TRANSFER']),
                pix_key=f"{first.lower()}.{last.lower()}@email.com",
                email=f"{first.lower()}.{last.lower()}@empresa.com.br"
            )
            
            providers.append(provider)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Criados {i + 1}/{count} prestadores...')
        
        return providers
    
    def create_payrolls(self, providers):
        """Cria folhas de pagamento de 2020 até janeiro/2026."""
        service = PayrollService()
        total = 0
        
        # Anos e meses
        start_year = 2020
        end_year = 2026
        end_month = 1  # Janeiro de 2026
        
        for provider in providers:
            # Cada prestador tem um histórico diferente
            # Alguns começaram em 2020, outros depois
            start_year_provider = random.randint(2020, 2024)
            
            for year in range(start_year_provider, end_year + 1):
                # Determinar até que mês criar neste ano
                if year == end_year:
                    max_month = end_month
                else:
                    max_month = 12
                
                for month in range(1, max_month + 1):
                    reference_month = f"{month:02d}/{year}"
                    
                    # Nem todo mês tem folha (simular ausências)
                    if random.random() < 0.05:  # 5% de chance de não ter folha
                        continue
                    
                    try:
                        # Gerar dados variáveis realistas
                        overtime_hours = Decimal(random.randint(0, 40))
                        holiday_hours = Decimal(random.randint(0, 16))
                        night_hours = Decimal(random.randint(0, 30))
                        late_minutes = random.randint(0, 120)
                        absence_hours = Decimal(random.randint(0, 16))
                        manual_discounts = Decimal(0)
                        
                        # Criar folha
                        payroll = service.create_payroll(
                            provider_id=provider.id,
                            reference_month=reference_month,
                            overtime_hours_50=overtime_hours,
                            holiday_hours=holiday_hours,
                            night_hours=night_hours,
                            late_minutes=late_minutes,
                            absence_hours=absence_hours,
                            manual_discounts=manual_discounts,
                            notes=None
                        )
                        
                        # Definir status baseado na data
                        if year < 2025:
                            # Folhas antigas: 80% pagas, 20% fechadas
                            if random.random() < 0.8:
                                payroll.status = PayrollStatus.PAID
                                payroll.closed_at = datetime(year, month, 28)
                                payroll.paid_at = datetime(year, month, 30)
                            else:
                                payroll.status = PayrollStatus.CLOSED
                                payroll.closed_at = datetime(year, month, 28)
                        elif year == 2025:
                            # 2025: mix de pagas e fechadas
                            if random.random() < 0.6:
                                payroll.status = PayrollStatus.PAID
                                payroll.closed_at = datetime(year, month, 28)
                                payroll.paid_at = datetime(year, month, 30)
                            elif random.random() < 0.8:
                                payroll.status = PayrollStatus.CLOSED
                                payroll.closed_at = datetime(year, month, 28)
                            # else: DRAFT
                        else:
                            # 2026: maioria em draft
                            if random.random() < 0.2:
                                payroll.status = PayrollStatus.CLOSED
                                payroll.closed_at = datetime(2026, 1, 28)
                            # else: DRAFT
                        
                        payroll.save()
                        total += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Erro ao criar folha {reference_month} para {provider.name}: {e}'
                            )
                        )
            
            # Progresso
            if (providers.index(provider) + 1) % 10 == 0:
                self.stdout.write(
                    f'  Processados {providers.index(provider) + 1}/{len(providers)} prestadores...'
                )
        
        return total
    
    def show_statistics(self):
        """Mostra estatísticas dos dados criados."""
        total_providers = Provider.objects.count()
        total_payrolls = Payroll.objects.count()
        
        draft = Payroll.objects.filter(status=PayrollStatus.DRAFT).count()
        closed = Payroll.objects.filter(status=PayrollStatus.CLOSED).count()
        paid = Payroll.objects.filter(status=PayrollStatus.PAID).count()
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('ESTATÍSTICAS'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'Prestadores:          {total_providers}')
        self.stdout.write(f'Folhas de pagamento:  {total_payrolls}')
        self.stdout.write(f'  - DRAFT (Rascunho): {draft}')
        self.stdout.write(f'  - CLOSED (Fechada): {closed}')
        self.stdout.write(f'  - PAID (Paga):      {paid}')
        self.stdout.write('=' * 50 + '\n')
