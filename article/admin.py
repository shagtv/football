from django.contrib import admin

from .models import Article, Category, Tag


class ArticleAdmin(admin.ModelAdmin):
    class Meta:
        model = Article


class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        model = Category


class TagAdmin(admin.ModelAdmin):
    class Meta:
        model = Tag

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)