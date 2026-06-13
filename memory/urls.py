from django.urls import path
from .views import (
    ConversationLogView,
    EpisodicMemoryView,
    EntityMemoryView,
    PersonEntityView,
)

urlpatterns = [
    path('conversation-logs/',  ConversationLogView.as_view(),  name='conversation-log-list'),
    path('episodic-memories/',  EpisodicMemoryView.as_view(),   name='episodic-memory-list'),
    path('entity-memories/',    EntityMemoryView.as_view(),     name='entity-memory-list'),
    path('person-entities/',    PersonEntityView.as_view(),     name='person-entity-list'),
]
