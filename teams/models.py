from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

class TeamManager(models.Manager):
    pass


class Team(models.Model):
    user = models.ForeignKey(User, default=1)
    name = models.CharField(max_length=120, unique=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = TeamManager()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')

    def get_absolute_url(self):
        return reverse("teams:detail", kwargs={"name": self.name})
