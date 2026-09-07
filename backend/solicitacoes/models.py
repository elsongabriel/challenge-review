from django.conf import settings
from django.db import models


STATUS_CHOICES = [
    ('aberta', 'Aberta'),
    ('em_andamento', 'Em andamento'),
    ('concluida', 'Concluída'),
    ('cancelada', 'Cancelada'),
]

PRIORIDADE_CHOICES = [
    ('baixa', 'Baixa'),
    ('media', 'Média'),
    ('alta', 'Alta'),
]


class Solicitacao(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitacoes')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    # Soft delete: quando preenchido, a solicitação foi "excluída" mas
    # permanece no banco. null = solicitação ativa.
    excluido_em = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.titulo


class HistoricoStatus(models.Model):
    solicitacao = models.ForeignKey(Solicitacao, on_delete=models.CASCADE, related_name='historico')
    status_anterior = models.CharField(max_length=20, choices=STATUS_CHOICES)
    status_novo = models.CharField(max_length=20, choices=STATUS_CHOICES)
    alterado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    alterado_em = models.DateTimeField(auto_now_add=True)


class Comentario(models.Model):
    solicitacao = models.ForeignKey(Solicitacao, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
