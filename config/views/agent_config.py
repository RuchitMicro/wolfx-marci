from django_api_helper.views import GenericCRUDView
from config.models import AgentConfig


class AgentConfigView(GenericCRUDView):
    model               = AgentConfig
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
