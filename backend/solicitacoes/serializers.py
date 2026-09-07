from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Solicitacao, HistoricoStatus, Comentario


class ComentarioSerializer(serializers.ModelSerializer):
    autor_nome = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = ['id', 'texto', 'autor', 'autor_nome', 'criado_em']
        read_only_fields = ['autor', 'criado_em']

    def get_autor_nome(self, obj):
        # NOTE: isso dispara uma query por comentário quando serializado em lista.
        return User.objects.get(pk=obj.autor_id).username


class HistoricoStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoStatus
        fields = ['id', 'status_anterior', 'status_novo', 'alterado_por', 'alterado_em']


class SolicitacaoSerializer(serializers.ModelSerializer):
    autor_nome = serializers.CharField(source='autor.username', read_only=True)

    class Meta:
        model = Solicitacao
        fields = [
            'id', 'titulo', 'descricao', 'status', 'prioridade',
            'autor', 'autor_nome', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['autor', 'criado_em', 'atualizado_em']

    # NOTE: não há validação de tamanho mínimo/vazio para "titulo" além do
    # que o Django já garante por padrão (blank=False implícito no CharField).
    # Verificar se isso é suficiente para as regras de negócio pedidas.


class SolicitacaoDetailSerializer(SolicitacaoSerializer):
    historico = HistoricoStatusSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)

    class Meta(SolicitacaoSerializer.Meta):
        fields = SolicitacaoSerializer.Meta.fields + ['historico', 'comentarios']
