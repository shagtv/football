from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone

from teams.models import Team


def index(request):
    queryset = Team.objects.all()

    query = request.GET.get("q")
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
        ).distinct()

    paginator = Paginator(queryset, 5)

    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    context = {
        "object_list": objects,
    }

    return render(request, "teams/index.html", context)


def detail(request, name=None):
    instance = get_object_or_404(Team, name=name)

    context = {
        "instance": instance,
    }
    return render(request, 'teams/detail.html', context)


def update(request, id=None):
    return None


def delete(request, id=None):
    return None