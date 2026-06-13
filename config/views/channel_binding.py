from django_api_helper.views import GenericCRUDView
from config.models import ChannelBinding


class ChannelBindingView(GenericCRUDView):
    model               = ChannelBinding
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
