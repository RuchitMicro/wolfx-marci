from django_api_helper.views import GenericCRUDView
from memory.models import ConversationLog


class ConversationLogView(GenericCRUDView):
    model               = ConversationLog
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
