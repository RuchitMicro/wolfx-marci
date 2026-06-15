"""
config/models/global_prompt.py

GlobalPrompt — versioned global prompt applied to all agents.
Only one instance should be active at a time.
Saving a new active prompt deactivates all others automatically.
"""

from django.db  import models
from django.db  import transaction


class GlobalPrompt(models.Model):
    """
    Versioned global prompt applied to all agents as the base non-negotiable layer.
    Only one instance active at a time.
    """
    version     = models.CharField(max_length=20, unique=True)
    content     = models.TextField(help_text='Non-negotiable instructions applied to all agents.')
    is_active   = models.BooleanField(default=False, help_text='Only one GlobalPrompt should be active at a time.')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Global Prompt'
        verbose_name_plural = 'Global Prompts'
        ordering            = ['-created_at']

    def __str__(self):
        return f'v{self.version} ({"active" if self.is_active else "inactive"})'

    def save(self, *args, **kwargs):
        """
        If this prompt is being set to active,
        deactivate all other prompts first.
        Wrapped in transaction to ensure consistency.
        """
        if self.is_active:
            with transaction.atomic():
                GlobalPrompt.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls) -> str:
        """
        Returns the content of the currently active GlobalPrompt.
        Returns empty string if none is set — agents still function without it.
        """
        obj = cls.objects.filter(is_active=True).first()
        return obj.content.strip() if obj else ''