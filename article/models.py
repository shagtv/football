# coding: utf-8
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from tagging.registry import register

class Category(models.Model):
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default='ru')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Tag(models.Model):
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default='ru')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')


class ArticleManager(models.Manager):
    def get_queryset(self):
        return super(ArticleManager, self).get_queryset().select_related('user')
        # qs = qs.filter(language=get_language())


class Article(models.Model):
    user = models.ForeignKey(User, default=1)
    title = models.CharField(max_length=255)
    text = models.TextField()
    category = models.ForeignKey(Category)
    tag = models.ManyToManyField(Tag, blank=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default='ru')

    objects = ArticleManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article:article-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ["-created"]
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

register(Article)