from django.contrib import admin
from .models import Solicitacao, HistoricoStatus, Comentario

admin.site.register(Solicitacao)
admin.site.register(HistoricoStatus)
admin.site.register(Comentario)
