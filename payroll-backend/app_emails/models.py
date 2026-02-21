import uuid

from django.db import models

from users.models import Company


class EmailTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nome do Template"
    )
    subject = models.CharField(max_length=255, verbose_name="Assunto")
    html_content = models.TextField(verbose_name="Conteúdo HTML")
    text_content = models.TextField(
        blank=True, null=True, verbose_name="Conteúdo Texto"
    )
    variables = models.JSONField(
        blank=True, null=True, verbose_name="Variáveis Esperadas"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template de E-mail"
        verbose_name_plural = "Templates de E-mail"

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("sent", "Enviado"),
        ("failed", "Falhou"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template",
    )
    to_email = models.EmailField(verbose_name="Destinatário")
    subject = models.CharField(max_length=255, verbose_name="Assunto")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Status"
    )

    error_message = models.TextField(
        blank=True, null=True, verbose_name="Mensagem de Erro"
    )
    context = models.JSONField(blank=True, null=True, verbose_name="Contexto")

    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Enviado em")
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional linking to tenant/company if needed for multi-tenancy visibility
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Log de E-mail"
        verbose_name_plural = "Logs de E-mail"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.to_email} - {self.subject} ({self.status})"
