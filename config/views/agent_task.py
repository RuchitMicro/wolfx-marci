from django_api_helper.views import GenericCRUDView
from config.models import AgentTask


class AgentTaskView(GenericCRUDView):
    model               = AgentTask
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
