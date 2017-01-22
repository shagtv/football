from django.urls import reverse_lazy
from django.utils.translation import get_language
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from .models import Article


class ArticleListView(ListView):
    model = Article
    paginate_by = 3

    def get_queryset(self):
        return super(ArticleListView, self).get_queryset().filter(language=get_language())


class ArticleDetailView(DetailView):
    model = Article


class ArticleCreateView(CreateView):
    model = Article
    fields = ('title', 'text', 'category', 'tag')


class ArticleUpdateView(UpdateView):
    model = Article
    fields = '__all__'


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('article:article-list')
