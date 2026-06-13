#!/bin/bash
set -euo pipefail

APP="memory"

rm -f $APP/models.py $APP/views.py

mkdir -p $APP/models
mkdir -p $APP/views

# ── models/__init__.py ──
cat > $APP/models/__init__.py << 'EOF'
from .conversation_log  import ConversationLog
from .episodic_memory   import EpisodicMemory
from .entity_memory     import EntityMemory
from .person_entity     import PersonEntity

__all__ = [
    'ConversationLog',
    'EpisodicMemory',
    'EntityMemory',
    'PersonEntity',
]
EOF

# ── models/conversation_log.py ──
cat > $APP/models/conversation_log.py << 'EOF'
from django.db import models


class ConversationLog(models.Model):
    """
    Layer 1 — Short-term in-session conversation history.
    One row per message exchanged in a channel session.
    """
    ROLE_CHOICES = [
        ('user',      'User'),
        ('assistant', 'Assistant'),
    ]

    channel_id      = models.CharField(max_length=100, help_text='WhatsApp group ID or Slack channel ID.')
    sender          = models.CharField(max_length=100, blank=True, help_text='Sender phone number.')
    sender_name     = models.CharField(max_length=100, blank=True, help_text='Resolved display name.')
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message         = models.TextField()
    intent          = models.CharField(max_length=50, blank=True, help_text='Classified intent of this message.')
    tool_calls      = models.JSONField(default=list, help_text='Tools called during this turn.')
    tokens_used     = models.IntegerField(default=0)
    sql_used        = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Conversation Log'
        verbose_name_plural = 'Conversation Logs'
        ordering            = ['created_at']
        indexes             = [
            models.Index(fields=['channel_id', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        return f'[{self.role}] {self.channel_id} — {self.created_at:%d %b %Y %H:%M}'

    @classmethod
    def get_recent(cls, channel_id: str, window: int = 10):
        raise NotImplementedError('Return the last N messages for this channel ordered by created_at.')

    @classmethod
    def get_recent_for_sender(cls, channel_id: str, sender: str, window: int = 5):
        raise NotImplementedError('Return the last N messages from this specific sender in this channel.')
EOF

# ── models/episodic_memory.py ──
cat > $APP/models/episodic_memory.py << 'EOF'
from django.db import models


class EpisodicMemory(models.Model):
    """
    Layer 2 — Medium-term summarised past sessions.
    Created by a background Celery task after each conversation ends.
    Summarises key points, decisions, and context from a session.
    """
    channel_id      = models.CharField(max_length=100)
    sender          = models.CharField(max_length=100, blank=True, help_text='Phone number if user-scoped, empty if group-scoped.')
    scope           = models.CharField(max_length=20, choices=[
        ('group',   'Group'),
        ('user',    'User'),
    ], default='group')
    summary         = models.TextField(help_text='LLM-generated summary of the session.')
    key_entities    = models.JSONField(default=list, help_text='Company names, person names mentioned.')
    key_decisions   = models.JSONField(default=list, help_text='Decisions or action items from the session.')
    session_start   = models.DateTimeField()
    session_end     = models.DateTimeField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Episodic Memory'
        verbose_name_plural = 'Episodic Memories'
        ordering            = ['-session_end']
        indexes             = [
            models.Index(fields=['channel_id', 'scope']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f'Episode {self.channel_id} — {self.session_end:%d %b %Y}'

    @classmethod
    def get_recent_for_channel(cls, channel_id: str, limit: int = 5):
        raise NotImplementedError('Return recent episodic memories for this channel.')

    @classmethod
    def get_recent_for_sender(cls, sender: str, limit: int = 3):
        raise NotImplementedError('Return recent episodic memories for this sender across all channels.')

    @classmethod
    def create_from_conversation(cls, channel_id: str, sender: str, messages: list):
        raise NotImplementedError('Summarise a list of ConversationLog messages and create an EpisodicMemory record.')
EOF

# ── models/entity_memory.py ──
cat > $APP/models/entity_memory.py << 'EOF'
from django.db import models


class EntityMemory(models.Model):
    """
    Layer 3+4 — Long-term semantic memory with pgvector embeddings.
    Stores research, insights, and knowledge about companies and industries.
    Public facts are global scope. Pipeline context is group-scoped.
    """
    ENTITY_TYPES = [
        ('company',     'Company'),
        ('industry',    'Industry'),
        ('topic',       'Topic'),
        ('insight',     'Strategic Insight'),
    ]

    SCOPE_CHOICES = [
        ('global',  'Global — accessible to all agents'),
        ('group',   'Group — accessible within specific channel only'),
    ]

    entity_type     = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_name     = models.CharField(max_length=200, db_index=True)
    scope           = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='global')
    scope_id        = models.CharField(max_length=100, blank=True, help_text='channel_id if group-scoped.')
    known_facts     = models.JSONField(default=dict, help_text='Structured facts: founded, size, HQ, product, etc.')
    raw_notes       = models.TextField(blank=True, help_text='Unstructured research notes.')
    embedding       = models.JSONField(default=list, help_text='pgvector embedding — 1536 dimensions. Replace with VectorField when pgvector installed.')
    confidence      = models.FloatField(default=1.0, help_text='How fresh and reliable this data is. Decays over time.')
    source          = models.CharField(max_length=50, blank=True, help_text='web, linkedin, apollo, crm, manual.')
    last_researched = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Entity Memory'
        verbose_name_plural = 'Entity Memories'
        ordering            = ['-updated_at']
        indexes             = [
            models.Index(fields=['entity_type', 'entity_name']),
            models.Index(fields=['scope', 'scope_id']),
        ]

    def __str__(self):
        return f'{self.entity_type}: {self.entity_name} ({self.scope})'

    def is_stale(self, staleness_days: int = 7) -> bool:
        raise NotImplementedError('Return True if last_researched is older than staleness_days.')

    def decay_confidence(self):
        raise NotImplementedError('Reduce confidence score based on time since last_researched.')

    @classmethod
    def search(cls, query_embedding: list, scope: str = 'global', scope_id: str = '', top_k: int = 5):
        raise NotImplementedError('pgvector similarity search. Return top_k most relevant EntityMemory records.')

    @classmethod
    def get_or_create_for_entity(cls, entity_type: str, entity_name: str, scope: str = 'global', scope_id: str = ''):
        raise NotImplementedError('Return existing EntityMemory or create a new empty one.')
EOF

# ── models/person_entity.py ──
cat > $APP/models/person_entity.py << 'EOF'
from django.db import models


class PersonEntity(models.Model):
    """
    Identity resolution and person knowledge base.
    Auto-created on first contact via pushname from wweb-mcp.
    Stores team members, community members, and external contacts.
    """
    TRUST_LEVELS = [
        ('unknown',     'Unknown — new contact'),
        ('member',      'Regular member'),
        ('trusted',     'Trusted — manually elevated'),
        ('team',        'WOLFx team member'),
        ('blocked',     'Blocked — ignore all messages'),
    ]

    phone_number    = models.CharField(max_length=50, unique=True)
    whatsapp_name   = models.CharField(max_length=100, blank=True, help_text='pushname from wweb-mcp. Auto-populated.')
    real_name       = models.CharField(max_length=100, blank=True, help_text='Manually confirmed real name.')
    role            = models.CharField(max_length=100, blank=True, help_text='e.g. Sales Rep, CEO, Community Member.')
    company         = models.CharField(max_length=100, blank=True)
    trust_level     = models.CharField(max_length=20, choices=TRUST_LEVELS, default='unknown')
    groups          = models.JSONField(default=list, help_text='List of channel_ids this person is active in.')
    preferences     = models.JSONField(default=dict, help_text='Communication style and preferences learned over time.')
    embedding       = models.JSONField(default=list, help_text='pgvector embedding of this person profile.')
    first_seen      = models.DateTimeField(auto_now_add=True)
    last_active     = models.DateTimeField(auto_now=True)
    metadata        = models.JSONField(default=dict)

    class Meta:
        verbose_name        = 'Person Entity'
        verbose_name_plural = 'Person Entities'
        ordering            = ['-last_active']
        indexes             = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['trust_level']),
        ]

    def __str__(self):
        return f'{self.display_name} ({self.phone_number})'

    @property
    def display_name(self) -> str:
        raise NotImplementedError('Return real_name if set, else whatsapp_name, else phone_number.')

    def is_blocked(self) -> bool:
        raise NotImplementedError('Return True if trust_level is blocked.')

    def is_team_member(self) -> bool:
        raise NotImplementedError('Return True if trust_level is team.')

    @classmethod
    def resolve(cls, phone_number: str, pushname: str = ''):
        raise NotImplementedError('Get or create PersonEntity from phone_number. Update whatsapp_name from pushname if provided.')
EOF

# ── manager.py ──
cat > $APP/manager.py << 'EOF'
from memory.models import ConversationLog, EpisodicMemory, EntityMemory, PersonEntity


class MemoryManager:
    """
    Coordinates all four memory layers.
    Called by BaseAgent.process() before every agent invocation.
    """

    def __init__(self, agent_config):
        self.config = agent_config

    def resolve_identity(self, phone_number: str, pushname: str = '') -> PersonEntity:
        raise NotImplementedError('Resolve sender identity via PersonEntity.resolve().')

    def retrieve_minimal(self, person: PersonEntity, channel_binding) -> dict:
        raise NotImplementedError('Return identity + last 2 conversation messages only.')

    def retrieve_standard(self, person: PersonEntity, channel_binding, message: str) -> dict:
        raise NotImplementedError('Return identity + episodic summary + last N conversation messages.')

    def retrieve_full(self, person: PersonEntity, channel_binding, message: str) -> dict:
        raise NotImplementedError('Return all layers — identity, episodic, semantic pgvector search, entity memory.')

    def store_episode(self, message: str, reply: str, person: PersonEntity, channel_binding):
        raise NotImplementedError('Save ConversationLog entries for user message and assistant reply.')

    def summarise_session(self, channel_id: str, sender: str):
        raise NotImplementedError('Background task — summarise recent ConversationLog entries into EpisodicMemory.')

    def get_entity(self, entity_name: str, scope: str = 'global', scope_id: str = ''):
        raise NotImplementedError('Retrieve EntityMemory by name and scope.')

    def store_entity(self, entity_name: str, data: dict, scope: str = 'global', scope_id: str = ''):
        raise NotImplementedError('Create or update EntityMemory for this entity.')

    def is_stale(self, entity: EntityMemory) -> bool:
        raise NotImplementedError('Return True if entity research is older than config.memory_staleness_days.')
EOF

# ── precompose.py ──
cat > $APP/precompose.py << 'EOF'
class PreComposer:
    """
    Cheap LLM call (gpt-5-nano) that synthesises raw retrieved memory
    into a tight 2-3 sentence context block for the main agent call.
    Skipped entirely when context_requirement is 'none'.
    """

    def __init__(self, llm):
        self.llm = llm

    def compose(self, message: str, memories: dict, person) -> str:
        raise NotImplementedError(
            'Take raw memories dict and incoming message. '
            'Return a 2-3 sentence context summary string. '
            'Return empty string if no relevant context found.'
        )

    def _build_prompt(self, message: str, memories: dict, person) -> str:
        raise NotImplementedError('Build the pre-composition prompt from message + memories + person identity.')
EOF

# ── views/__init__.py ──
cat > $APP/views/__init__.py << 'EOF'
from .conversation_log  import ConversationLogView
from .episodic_memory   import EpisodicMemoryView
from .entity_memory     import EntityMemoryView
from .person_entity     import PersonEntityView

__all__ = [
    'ConversationLogView',
    'EpisodicMemoryView',
    'EntityMemoryView',
    'PersonEntityView',
]
EOF

# ── views/conversation_log.py ──
cat > $APP/views/conversation_log.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from memory.models import ConversationLog


class ConversationLogView(GenericCRUDView):
    model               = ConversationLog
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── views/episodic_memory.py ──
cat > $APP/views/episodic_memory.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from memory.models import EpisodicMemory


class EpisodicMemoryView(GenericCRUDView):
    model               = EpisodicMemory
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── views/entity_memory.py ──
cat > $APP/views/entity_memory.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from memory.models import EntityMemory


class EntityMemoryView(GenericCRUDView):
    model               = EntityMemory
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── views/person_entity.py ──
cat > $APP/views/person_entity.py << 'EOF'
from django_api_helper.views import GenericCRUDView
from memory.models import PersonEntity


class PersonEntityView(GenericCRUDView):
    model               = PersonEntity
    serializer_class    = None  # TODO: wire serializer
    filterset_class     = None  # TODO: wire filterset
    permission_classes  = []    # TODO: wire permissions
EOF

# ── urls.py ──
cat > $APP/urls.py << 'EOF'
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
EOF

# ── admin.py ──
cat > $APP/admin.py << 'EOF'
from django.contrib import admin
from .models import ConversationLog, EpisodicMemory, EntityMemory, PersonEntity


@admin.register(ConversationLog)
class ConversationLogAdmin(admin.ModelAdmin):
    list_display    = ['channel_id', 'sender_name', 'role', 'intent', 'tokens_used', 'created_at']
    list_filter     = ['role', 'intent']
    ordering        = ['-created_at']


@admin.register(EpisodicMemory)
class EpisodicMemoryAdmin(admin.ModelAdmin):
    list_display    = ['channel_id', 'sender', 'scope', 'session_end']
    list_filter     = ['scope']
    ordering        = ['-session_end']


@admin.register(EntityMemory)
class EntityMemoryAdmin(admin.ModelAdmin):
    list_display    = ['entity_type', 'entity_name', 'scope', 'confidence', 'last_researched']
    list_filter     = ['entity_type', 'scope']
    ordering        = ['-updated_at']


@admin.register(PersonEntity)
class PersonEntityAdmin(admin.ModelAdmin):
    list_display    = ['phone_number', 'whatsapp_name', 'real_name', 'trust_level', 'last_active']
    list_filter     = ['trust_level']
    ordering        = ['-last_active']
EOF

# ── apps.py ──
cat > $APP/apps.py << 'EOF'
from django.apps import AppConfig


class MemoryConfig(AppConfig):
    default_auto_field  = 'django.db.models.BigAutoField'
    name                = 'memory'
    verbose_name        = 'Agent Memory'
EOF

echo ""
echo "memory app structure created successfully."