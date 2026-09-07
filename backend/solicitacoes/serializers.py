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

    def validate(self, attrs):
        # Regra: não é permitido reabrir uma solicitação concluída indo
        # diretamente de 'concluida' para 'aberta'.
        if self.instance is not None:
            status_atual = self.instance.status
            status_novo = attrs.get('status', status_atual)
            if status_atual == 'concluida' and status_novo == 'aberta':
                raise serializers.ValidationError({
                    'status': 'Não é permitido reabrir uma solicitação concluída diretamente.'
                })
        return attrs

    def validate_titulo(self, value):
        # Regra: o título não pode ser vazio ou conter apenas espaços.
        # Também normaliza removendo os espaços das pontas antes de salvar.
        titulo = value.strip()
        if not titulo:
            raise serializers.ValidationError(
                'O título não pode ficar vazio ou conter apenas espaços.'
            )
        return titulo


class SolicitacaoDetailSerializer(SolicitacaoSerializer):
    historico = HistoricoStatusSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)

    class Meta(SolicitacaoSerializer.Meta):
        fields = SolicitacaoSerializer.Meta.fields + ['historico', 'comentarios']
