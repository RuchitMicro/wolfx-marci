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
