from django_api_helper.views import GenericCRUDView
from memory.models import EntityMemory


class EntityMemoryView(GenericCRUDView):
    model               = EntityMemory
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
