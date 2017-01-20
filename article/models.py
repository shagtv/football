# coding: utf-8
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _


class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

class Tag(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class Article(models.Model):
    user = models.ForeignKey(User, default=1)
    title = models.CharField(max_length=255)
    text = models.TextField()
    category = models.ForeignKey(Category)
    tag = models.ManyToManyField(Tag, blank=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created"]
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')