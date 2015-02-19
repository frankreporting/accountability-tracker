from __future__ import division
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from django.db.models import Q, Avg, Max, Min, Sum, Count
from election_profiles.models import Candidate
from bakery.views import BuildableListView, BuildableDetailView
import datetime
import logging
import yaml
import re
import json

logger = logging.getLogger("accountability_tracker")

# Create your views here.
class InitialListView(BuildableListView):
    model = Candidate
    template_name = "election_profiles/index.html"
    def get_object(self):
        object = super(InitialListView, self).get_object()
        return object
    def get_queryset(self):
        queryset = super(InitialListView, self).get_queryset()
        races = []
        for contest in queryset:
            races.append(contest.contest)
        display_races = sorted(set(races), key=lambda x: races.index(x))
        config = yaml.load(open("election_profiles/config.yml"))
        return {
            "article_content": config["article_content"],
            "about_content": config["about_content"],
            "config_object": config["config_object"],
            "display_races": display_races,
            "objects": queryset,
        }


class InitialDetailView(BuildableDetailView):
    model = Candidate
    template_name = "election_profiles/detail.html"
    slug_field = "candidate_slug"
    def get_object(self):
        object = super(InitialDetailView, self).get_object()
        return object
    def get_context_data(self, **kwargs):
        context = super(InitialDetailView, self).get_context_data(**kwargs)
        config = yaml.load(open("election_profiles/config.yml"))
        context["slug"] = self.object.candidate_slug
        context["article_content"] = config["article_content"]
        context["about_content"] = config["about_content"]
        context["config_object"] = config["config_object"]
        return context
