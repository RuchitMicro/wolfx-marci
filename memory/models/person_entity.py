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
