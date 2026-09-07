from rest_framework import permissions


class IsAutorOrReadOnly(permissions.BasePermission):
    """Leitura liberada para qualquer usuário autenticado; edição e exclusão
    permitidas apenas para o autor da solicitação.

    Regra de negócio: "um usuário só pode editar ou excluir suas próprias
    solicitações".
    """

    message = 'Você só pode editar ou excluir solicitações de sua autoria.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.autor_id == request.user.id
