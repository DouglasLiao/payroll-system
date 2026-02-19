import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.template.loader import render_to_string

from site_manage.models import PayrollConfiguration
from users.models import (
    Company,
    PlanType,
    Subscription,
    User,
    UserRole,
)
from services.user_service import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    CompanyAlreadyActiveError,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# COMPANY SERVICE
# ==============================================================================


class CompanyService:
    """
    Serviço responsável pela lógica de negócio de empresas.

    Responsabilidades:
    - Registro de nova empresa (com config e assinatura trial)
    - Aprovação de empresa pendente
    - Rejeição de empresa
    - Alternância de status ativo/inativo
    - Notificações de email relacionadas ao ciclo de vida da empresa
    """

    @staticmethod
    @transaction.atomic
    def register_company(
        *,
        company_name: str,
        company_cnpj: str,
        company_phone: str = "",
        admin_username: str,
        admin_email: str,
        admin_password: str,
        admin_first_name: str = "",
        admin_last_name: str = "",
    ) -> tuple[Company, User]:
        """
        Registra uma nova empresa com seu Customer Admin e assinatura Trial.

        Cria atomicamente:
        1. Company (is_active=False, aguardando aprovação)
        2. PayrollConfiguration (defaults do sistema)
        3. Subscription (plano TRIAL, 90 dias)
        4. User (role=CUSTOMER_ADMIN)

        Args:
            company_name: Nome da empresa
            company_cnpj: CNPJ da empresa
            company_phone: Telefone (opcional)
            admin_username: Username do administrador
            admin_email: Email do administrador
            admin_password: Senha do administrador
            admin_first_name: Primeiro nome (opcional)
            admin_last_name: Sobrenome (opcional)

        Returns:
            Tupla (Company, User) criados

        Raises:
            EmailAlreadyExistsError: Se o email já estiver cadastrado
            UsernameAlreadyExistsError: Se o username já existir
        """
        if User.objects.filter(email=admin_email).exists():
            raise EmailAlreadyExistsError(f"Email '{admin_email}' já está cadastrado.")

        if User.objects.filter(username=admin_username).exists():
            raise UsernameAlreadyExistsError(f"Username '{admin_username}' já existe.")

        # 1. Empresa (inativa até aprovação)
        company = Company.objects.create(
            name=company_name,
            cnpj=company_cnpj,
            email=admin_email,
            phone=company_phone,
            is_active=False,
        )

        # 2. Configuração de folha com defaults
        PayrollConfiguration.objects.create(company=company)

        # 3. Assinatura Trial (90 dias)
        trial_defaults = Subscription.get_plan_defaults(PlanType.TRIAL)
        Subscription.objects.create(
            company=company,
            plan_type=PlanType.TRIAL,
            max_providers=trial_defaults.get("max_providers", 5),
            price=trial_defaults.get("price", 0),
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90),
            is_active=True,
        )

        # 4. Customer Admin
        user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name,
            role=UserRole.CUSTOMER_ADMIN,
            company=company,
        )

        logger.info(
            f"[CompanyService] Empresa registrada: {company.name} (CNPJ: {company.cnpj}) "
            f"| Admin: {user.username}"
        )
        return company, user

    @staticmethod
    @transaction.atomic
    def approve_company(*, company: Company) -> Company:
        """
        Aprova uma empresa pendente, ativando-a e sua assinatura.

        Args:
            company: Empresa a ser aprovada

        Returns:
            Empresa atualizada

        Raises:
            CompanyAlreadyActiveError: Se a empresa já estiver ativa
        """
        if company.is_active:
            raise CompanyAlreadyActiveError(f"Empresa '{company.name}' já está ativa.")

        company.is_active = True
        company.save(update_fields=["is_active", "updated_at"])

        # Ativa assinatura existente ou cria uma nova
        try:
            subscription = company.subscription
            if not subscription.is_active:
                subscription.is_active = True
                subscription.start_date = timezone.now().date()
                subscription.save(
                    update_fields=["is_active", "start_date", "updated_at"]
                )
        except Subscription.DoesNotExist:
            trial_defaults = Subscription.get_plan_defaults(PlanType.TRIAL)
            Subscription.objects.create(
                company=company,
                plan_type=PlanType.TRIAL,
                max_providers=trial_defaults.get("max_providers", 5),
                price=trial_defaults.get("price", 0),
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timedelta(days=90),
                is_active=True,
            )

        # Garante que a configuração de folha existe
        if not hasattr(company, "payroll_config"):
            PayrollConfiguration.objects.create(company=company)

        logger.info(f"[CompanyService] Empresa aprovada: {company.name}")
        return company

    @staticmethod
    def toggle_company_status(*, company: Company) -> Company:
        """
        Alterna o status ativo/inativo de uma empresa.

        Args:
            company: Empresa a ter o status alternado

        Returns:
            Empresa com status atualizado
        """
        company.is_active = not company.is_active
        company.save(update_fields=["is_active", "updated_at"])
        status_str = "ativada" if company.is_active else "desativada"
        logger.info(f"[CompanyService] Empresa {status_str}: {company.name}")
        return company

    @staticmethod
    @transaction.atomic
    def reject_company(*, company: Company) -> str:
        """
        Rejeita e remove permanentemente uma empresa e todos os seus dados.

        Args:
            company: Empresa a ser rejeitada

        Returns:
            Nome da empresa removida (para uso em mensagens de resposta)
        """
        company_name = company.name
        company.delete()
        logger.info(f"[CompanyService] Empresa rejeitada e removida: {company_name}")
        return company_name

    @staticmethod
    def notify_registration(*, company: Company, user: User) -> None:
        """
        Notifica Super Admins e o novo usuário após registro.
        Best-effort: erros de email são apenas logados.
        """
        try:
            from app_emails.services import EmailSender

            sender = EmailSender()
            super_admins = User.objects.filter(role=UserRole.SUPER_ADMIN).values_list(
                "email", flat=True
            )
            for admin_email in super_admins:
                if admin_email:
                    sender.send_email(
                        to_email=admin_email,
                        subject=f"Novo Cadastro (Pendente): {company.name}",
                        text_content=(
                            f"Novo cadastro aguardando aprovação:\n\n"
                            f"Empresa: {company.name} (CNPJ: {company.cnpj})\n"
                            f"Usuário: {user.username} ({user.email})"
                        ),
                        html_content=(
                            f"<h2>Novo Cadastro (Pendente)</h2>"
                            f"<p><strong>Empresa:</strong> {company.name} — CNPJ: {company.cnpj}</p>"
                            f"<p><strong>Usuário:</strong> {user.username} ({user.email})</p>"
                        ),
                    )
            sender.send_email(
                to_email=user.email,
                subject="Cadastro Recebido - Aguardando Aprovação",
                text_content=(
                    f"Olá {user.first_name},\n\nRecebemos seu cadastro para {company.name}.\n"
                    f"Aguardando aprovação. Você será notificado por email."
                ),
                html_content=(
                    f"<h2>Cadastro Recebido!</h2>"
                    f"<p>Olá <strong>{user.first_name}</strong>,</p>"
                    f"<p>Seu cadastro para <strong>{company.name}</strong> está aguardando aprovação.</p>"
                ),
            )
        except Exception as e:
            logger.error(
                f"[CompanyService.notify_registration] Falha ao enviar email: {e}"
            )

    @staticmethod
    def notify_approval(*, company: Company) -> None:
        """
        Notifica o Customer Admin após aprovação da empresa.
        Best-effort: erros de email são apenas logados.
        """
        try:
            from app_emails.services import EmailSender

            admin_user = company.users.filter(role=UserRole.CUSTOMER_ADMIN).first()
            if admin_user and admin_user.email:
                EmailSender().send_email(
                    to_email=admin_user.email,
                    subject=f"Cadastro Aprovado! - {company.name}",
                    text_content=(
                        f"Olá {admin_user.first_name},\n\n"
                        f"O cadastro da empresa {company.name} foi aprovado!\n"
                        f"Você já pode acessar o sistema."
                    ),
                    html_content=render_to_string(
                        "emails/company_approved.html",
                        {
                            "first_name": admin_user.first_name,
                            "company_name": company.name,
                            "login_url": "http://localhost:5173/login",  # TODO: get from settings
                        },
                    ),
                )
        except Exception as e:
            logger.error(f"[CompanyService.notify_approval] Falha ao enviar email: {e}")

    @staticmethod
    def notify_rejection(*, company: Company) -> None:
        """
        Notifica o Customer Admin antes da rejeição da empresa.
        Best-effort: erros de email são apenas logados.
        """
        try:
            from app_emails.services import EmailSender

            admin_user = company.users.filter(role=UserRole.CUSTOMER_ADMIN).first()
            if admin_user and admin_user.email:
                EmailSender().send_email(
                    to_email=admin_user.email,
                    subject=f"Cadastro Reprovado - {company.name}",
                    text_content=(
                        f"Olá {admin_user.first_name},\n\n"
                        f"O cadastro da empresa {company.name} não foi aprovado."
                    ),
                    html_content=render_to_string(
                        "emails/company_rejected.html",
                        {
                            "first_name": admin_user.first_name,
                            "company_name": company.name,
                        },
                    ),
                )
        except Exception as e:
            logger.error(
                f"[CompanyService.notify_rejection] Falha ao enviar email: {e}"
            )
