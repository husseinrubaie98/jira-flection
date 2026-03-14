from django.db import models


class JiraSetting(models.Model):
    """Stores JIRA configuration settings as key-value pairs."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'JIRA Setting'
        verbose_name_plural = 'JIRA Settings'

    def __str__(self):
        return self.key

    @classmethod
    def get(cls, key, default=''):
        """Get a setting value by key."""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key, value):
        """Set a setting value by key."""
        obj, _ = cls.objects.update_or_create(key=key, defaults={'value': value})
        return obj
