from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from .models import Article


class ArticleListView(ListView):
    model = Article
    paginate_by = 3


class ArticleDetailView(DetailView):
    model = Article


class ArticleCreateView(CreateView):
    model = Article
    fields = '__all__'


class ArticleUpdateView(UpdateView):
    model = Article
    fields = '__all__'


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('article:article-list')
