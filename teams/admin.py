from django.contrib import admin

from teams.models import Team


class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "updated", "created"]
    list_display_links = ["updated"]
    list_filter = ["updated", "created"]
    search_fields = ["name"]

    class Meta:
        model = Team

admin.site.register(Team, TeamAdmin)