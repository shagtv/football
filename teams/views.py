from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from numpy.distutils.fcompiler import none

from django.views.decorators.cache import cache_page

from teams.forms import TeamForm
from teams.models import Team

@cache_page(60)
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

@cache_page(60)
def detail(request, name=None):
    instance = get_object_or_404(Team, name=name)

    context = {
        "instance": instance,
    }
    return render(request, 'teams/detail.html', context)


def update(request, id=None):
    instance = get_object_or_404(Team, id=id)

    if request.user != instance.user:
        return HttpResponseForbidden()

    form = TeamForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()

        messages.add_message(request, messages.SUCCESS, 'Hello world.')
        
        return redirect(reverse('teams:detail', args=(form.instance.name,)))
    
    context = {
        "instance": instance,
        "form": form,
    }
    return render(request, 'teams/update.html', context)


def delete(request, id=None):
    instance = get_object_or_404(Team, id=id)
    
    if request.user != instance.user:
        return HttpResponseForbidden()
    
    instance.delete()
    return redirect(reverse('teams:list'))


def create(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden()
    
    form = TeamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        
        messages.add_message(request, messages.SUCCESS, 'Hello world.')
        
        return redirect(reverse('teams:detail', args=(form.instance.name,)))
    
    context = {
        "form": form,
    }
    return render(request, 'teams/create.html', context)