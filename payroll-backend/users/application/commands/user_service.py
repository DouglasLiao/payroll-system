"""
Serviço de Usuários, Empresas e Licenças

Este módulo centraliza toda a lógica de negócio de escrita relacionada a:
- Usuários (criação, autenticação, senha, lookup por email/username)
- Empresas (registro, aprovação, rejeição, notificações)
- Assinaturas/Licenças (criação, renovação, troca de plano)
- Configurações de folha (aplicar template)

Seguindo o Django-Styleguide:
- Services são responsáveis por toda a lógica de negócio de escrita
- O Model.save() apenas persiste dados — sem lógica de negócio
- Views apenas orquestram: chamam services/selectors e serializam respostas
- Selectors centralizam as queries de leitura (SELECT)
"""

import logging
import secrets
from datetime import timedelta
from typing import Optional

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from site_manage.models import (
    PayrollConfiguration,
    PayrollMathTemplate,
    Provider,
)
from users.models import (
    Company,
    PasswordResetToken,
    PlanType,
    Subscription,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# EXCEPTIONS
# ==============================================================================


class UserServiceError(Exception):
    """Erro base do UserService."""


class EmailAlreadyExistsError(UserServiceError):
    """Email já cadastrado no sistema."""


class UsernameAlreadyExistsError(UserServiceError):
    """Username já cadastrado no sistema."""


class InvalidPasswordError(UserServiceError):
    """Senha não atende aos requisitos."""


class InvalidTokenError(UserServiceError):
    """Token inválido ou expirado."""


class SubscriptionLimitError(UserServiceError):
    """Limite de prestadores da assinatura atingido."""


class CompanyAlreadyActiveError(UserServiceError):
    """Empresa já está ativa."""


class PayrollConfigError(UserServiceError):
    """Erro na configuração de folha."""


# ==============================================================================
# USER SERVICE
# ==============================================================================


class UserService:
    """
    Serviço responsável pela lógica de negócio de usuários.

    Responsabilidades:
    - Lookup de usuário por email ou username (para login)
    - Verificação de disponibilidade de email
    - Criação de usuários (Customer Admin, Provider)
    - Alteração de senha
    - Reset de senha (geração e confirmação de token)
    - Atualização de preferências de sessão
    """

    @staticmethod
    def get_user_by_email_or_username(*, identifier: str) -> Optional[User]:
        """
        Busca um usuário por email ou username.

        Usado no login para suportar ambos os formatos.

        Args:
            identifier: Email ou username do usuário

        Returns:
            Instância de User ou None se não encontrado
        """
        if "@" in identifier:
            return User.objects.filter(email=identifier).first()
        return User.objects.filter(username=identifier).first()

    @staticmethod
    def email_is_available(*, email: str) -> bool:
        """
        Verifica se um email está disponível para cadastro.

        Args:
            email: Email a verificar

        Returns:
            True se disponível, False se já cadastrado
        """
        return not User.objects.filter(email=email).exists()

    @staticmethod
    def get_company_admins(*, company: Company):
        """
        Retorna todos os Customer Admins de uma empresa.

        Args:
            company: Empresa

        Returns:
            QuerySet de User com role=CUSTOMER_ADMIN
        """
        return User.objects.filter(
            company=company, role=UserRole.CUSTOMER_ADMIN
        ).order_by("username")

    @staticmethod
    @transaction.atomic
    def create_customer_admin(
        *,
        username: str,
        email: str,
        password: str,
        company: Company,
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """
        Cria um Customer Admin para uma empresa existente.

        Args:
            username: Nome de usuário único
            email: Email único do usuário
            password: Senha em texto plano (será hasheada)
            company: Empresa à qual o usuário pertence
            first_name: Primeiro nome (opcional)
            last_name: Sobrenome (opcional)

        Returns:
            Instância de User criada

        Raises:
            EmailAlreadyExistsError: Se o email já estiver cadastrado
            UsernameAlreadyExistsError: Se o username já existir
        """
        if User.objects.filter(email=email).exists():
            raise EmailAlreadyExistsError(f"Email '{email}' já está cadastrado.")

        if User.objects.filter(username=username).exists():
            raise UsernameAlreadyExistsError(f"Username '{username}' já existe.")

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.CUSTOMER_ADMIN,
            company=company,
            is_staff=False,
            is_superuser=False,
        )
        logger.info(
            f"[UserService] Customer Admin criado: {user.username} (empresa: {company.name})"
        )
        return user

    @staticmethod
    def change_password(*, user: User, old_password: str, new_password: str) -> None:
        """
        Altera a senha de um usuário autenticado.

        Args:
            user: Usuário que quer alterar a senha
            old_password: Senha atual em texto plano
            new_password: Nova senha em texto plano

        Raises:
            InvalidPasswordError: Se a senha atual estiver incorreta ou a nova não atender requisitos
        """
        if not user.check_password(old_password):
            raise InvalidPasswordError("Senha atual incorreta.")

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise InvalidPasswordError("; ".join(e.messages))

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        logger.info(f"[UserService] Senha alterada para usuário: {user.username}")

    @staticmethod
    def update_timeout_preference(*, user: User, timeout_seconds: int) -> User:
        """
        Atualiza a preferência de timeout de inatividade do usuário.

        Args:
            user: Usuário a atualizar
            timeout_seconds: Novo valor de timeout (60–3600 segundos)

        Returns:
            Usuário atualizado

        Raises:
            UserServiceError: Se o valor estiver fora do intervalo permitido
        """
        if not (60 <= timeout_seconds <= 3600):
            raise UserServiceError("Timeout deve estar entre 60 e 3600 segundos.")

        user.inactivity_timeout = timeout_seconds
        user.save(update_fields=["inactivity_timeout", "updated_at"])
        logger.info(
            f"[UserService] Timeout atualizado para {timeout_seconds}s: {user.username}"
        )
        return user

    @staticmethod
    def request_password_reset(*, email: str) -> Optional[PasswordResetToken]:
        """
        Gera um token de reset de senha para o email informado.

        Segue o padrão de não revelar se o email existe (segurança).

        Args:
            email: Email do usuário

        Returns:
            Instância de PasswordResetToken se o usuário existir, None caso contrário
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(
                f"[UserService] Reset solicitado para email inexistente: {email}"
            )
            return None

        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)
        token_obj = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at,
        )
        logger.info(f"[UserService] Token de reset gerado para: {user.username}")
        return token_obj

    @staticmethod
    @transaction.atomic
    def confirm_password_reset(*, token: str, new_password: str) -> User:
        """
        Confirma o reset de senha usando o token recebido por email.

        Args:
            token: Token de reset (enviado por email)
            new_password: Nova senha em texto plano

        Returns:
            Usuário com senha atualizada

        Raises:
            InvalidTokenError: Se o token for inválido ou expirado
            InvalidPasswordError: Se a nova senha não atender requisitos
        """
        try:
            token_obj = PasswordResetToken.objects.select_related("user").get(
                token=token
            )
        except PasswordResetToken.DoesNotExist:
            raise InvalidTokenError("Token inválido.")

        if not token_obj.is_valid():
            raise InvalidTokenError("Token expirado ou já utilizado.")

        user = token_obj.user
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise InvalidPasswordError("; ".join(e.messages))

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        token_obj.used = True
        token_obj.used_at = timezone.now()
        token_obj.save(update_fields=["used", "used_at"])

        logger.info(f"[UserService] Senha redefinida via token para: {user.username}")
        return user


# ==============================================================================
# PAYROLL CONFIG SERVICE
# ==============================================================================


class PayrollConfigService:
    """
    Serviço responsável pela lógica de configuração de folha das empresas.

    Responsabilidades:
    - Aplicar um MathTemplate a uma empresa
    """

    @staticmethod
    @transaction.atomic
    def apply_template(
        *, company: Company, template: PayrollMathTemplate
    ) -> PayrollConfiguration:
        """
        Aplica um PayrollMathTemplate à configuração de folha de uma empresa.

        Cria a configuração se não existir.

        Args:
            company: Empresa que receberá a configuração
            template: Template com as regras de cálculo

        Returns:
            PayrollConfiguration atualizada
        """
        config, created = PayrollConfiguration.objects.get_or_create(company=company)

        config.overtime_percentage = template.overtime_percentage
        config.night_shift_percentage = template.night_shift_percentage
        config.holiday_percentage = template.holiday_percentage
        config.advance_percentage = template.advance_percentage
        config.transport_voucher_type = template.transport_voucher_type
        config.business_days_rule = template.business_days_rule
        config.save()

        action = "criada" if created else "atualizada"
        logger.info(
            f"[PayrollConfigService] Config {action} para {company.name} "
            f"usando template '{template.name}'"
        )
        return config


# ==============================================================================
# SUBSCRIPTION SERVICE
# ==============================================================================


class SubscriptionService:
    """
    Serviço responsável pela lógica de negócio de assinaturas.

    Responsabilidades:
    - Criação de assinatura com defaults de plano
    - Renovação e troca de plano
    - Verificação de limites de uso
    """

    @staticmethod
    @transaction.atomic
    def create_subscription(
        *,
        company: Company,
        plan_type: str = PlanType.TRIAL,
        end_date=None,
    ) -> Subscription:
        """
        Cria uma assinatura para uma empresa aplicando os defaults do plano.

        Args:
            company: Empresa que receberá a assinatura
            plan_type: Tipo do plano (TRIAL, BASIC, PRO, ENTERPRISE, UNLIMITED)
            end_date: Data de término (None = vitalício)

        Returns:
            Instância de Subscription criada

        Raises:
            UserServiceError: Se o plano for inválido
        """
        if plan_type not in PlanType.values:
            raise UserServiceError(
                f"Plano inválido: '{plan_type}'. Opções: {PlanType.values}"
            )

        defaults = Subscription.get_plan_defaults(plan_type)
        subscription = Subscription.objects.create(
            company=company,
            plan_type=plan_type,
            max_providers=defaults["max_providers"],
            price=defaults["price"],
            start_date=timezone.now().date(),
            end_date=end_date,
            is_active=True,
        )
        logger.info(
            f"[SubscriptionService] Assinatura criada: {company.name} → {plan_type} "
            f"(max: {defaults['max_providers']} prestadores)"
        )
        return subscription

    @staticmethod
    @transaction.atomic
    def renew_subscription(
        *,
        subscription: Subscription,
        plan_type: Optional[str] = None,
        end_date=None,
    ) -> Subscription:
        """
        Renova ou altera o plano de uma assinatura existente.

        Se plan_type for informado, aplica os novos defaults de preço e limite.
        Se end_date for informado, atualiza a data de término.

        Args:
            subscription: Assinatura a ser renovada
            plan_type: Novo plano (opcional — mantém o atual se não informado)
            end_date: Nova data de término (opcional)

        Returns:
            Assinatura atualizada

        Raises:
            UserServiceError: Se o plano for inválido
        """
        if plan_type:
            if plan_type not in PlanType.values:
                raise UserServiceError(
                    f"Plano inválido: '{plan_type}'. Opções: {PlanType.values}"
                )

            defaults = Subscription.get_plan_defaults(plan_type)
            subscription.plan_type = plan_type
            subscription.max_providers = defaults["max_providers"]
            subscription.price = defaults["price"]

        if end_date is not None:
            subscription.end_date = end_date

        subscription.is_active = True
        subscription.save()

        logger.info(
            f"[SubscriptionService] Assinatura renovada: {subscription.company.name} "
            f"→ {subscription.plan_type}"
        )
        return subscription

    @staticmethod
    def can_add_provider(*, company: Company) -> tuple[bool, str]:
        """
        Verifica se a empresa pode adicionar mais prestadores.

        Args:
            company: Empresa a verificar

        Returns:
            Tupla (pode_adicionar: bool, motivo: str)
        """
        try:
            subscription = company.subscription
        except Subscription.DoesNotExist:
            return False, "Empresa sem assinatura ativa."

        if not subscription.is_active:
            return False, "Assinatura inativa."

        current_count = Provider.objects.filter(company=company).count()
        if current_count >= subscription.max_providers:
            return (
                False,
                f"Limite de {subscription.max_providers} prestadores atingido "
                f"(plano {subscription.get_plan_type_display()}).",
            )

        return True, ""
