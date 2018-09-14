from django.db import models
from django.core.cache import cache


class CacheRefreshModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(CacheRefreshModel, self).save(*args, **kwargs)
        cache.set('refresh_triggers', True)

    def delete(self, *args, **kwargs):
        super(CacheRefreshModel, self).delete(*args, **kwargs)
        cache.set('refresh_triggers', True)


class JerkManager(models.Manager):

    def get_by_natural_key(self, nick):
        return self.get(nick=nick)


class Jerk(CacheRefreshModel):

    objects = JerkManager()

    nick = models.CharField(max_length=128, unique=True)

    def natural_key(self):
        return (self.nick,)

    def __str__(self):
        return self.nick
