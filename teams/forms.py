#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from teams.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
