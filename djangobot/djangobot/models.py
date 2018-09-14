from django.db import models


class JerkManager(models.Manager):

    def get_by_natural_key(self, nick):
        return self.get(nick=nick)


class Jerk(models.Model):

    objects = JerkManager()

    nick = models.CharField(max_length=128, unique=True)

    def natural_key(self):
        return (self.nick,)

    def __str__(self):
        return self.nick
