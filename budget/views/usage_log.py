from django_api_helper.views import GenericCRUDView
from budget.models import TokenUsageLog


class TokenUsageLogView(GenericCRUDView):
    model               = TokenUsageLog
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
