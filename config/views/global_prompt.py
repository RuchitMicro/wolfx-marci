from django_api_helper.views import GenericCRUDView
from config.models import GlobalPrompt


class GlobalPromptView(GenericCRUDView):
    model           = GlobalPrompt
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions

    def activate(self, request, pk):
        raise NotImplementedError('Deactivate all other prompts and activate this one.')
