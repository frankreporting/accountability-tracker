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
from elections_spring2015.models import Candidate, Measure, Contest
from bakery.views import BuildableListView, BuildableDetailView
import datetime
import logging
import yaml
import re
import json

logger = logging.getLogger("accountability_tracker")

# Create your views here.
class PasadenaListView(BuildableListView):
    model = Candidate
    build_path = "pasadena-april-21/index.html"
    template_name = "elections_spring2015/pasadena-index.html"
    def get_object(self):
        object = super(PasadenaListView, self).get_object()
        return object
    def get_queryset(self):
        queryset = super(PasadenaListView, self).get_queryset()
        races = []
        for contest in queryset.filter(city="City of Pasadena"):
            races.append(contest.contest)
        display_races = sorted(set(races), key=lambda x: races.index(x))
        config = yaml.load(open("elections_spring2015/config.yml"))
        return {
            "article_content": config["pasadena_article_content"],
            "about_content": config["about_content"],
            "config_object": config["pasadena_config_object"],
            "display_races": display_races,
            "objects": queryset.filter(city="City of Pasadena"),
        }

class LosAngelesListView(BuildableListView):
    model = Candidate
    build_path = "los-angeles-may-19/index.html"
    template_name = "elections_spring2015/los-angeles-index.html"
    def get_object(self):
        object = super(LosAngelesListView, self).get_object()
        return object
    def get_queryset(self):
        queryset = super(LosAngelesListView, self).get_queryset()
        races = []
        for contest in queryset.filter(city="City of Los Angeles"):
            races.append(contest.contest)
        display_races = sorted(set(races), key=lambda x: races.index(x))
        config = yaml.load(open("elections_spring2015/config.yml"))
        return {
            "article_content": config["la_article_content"],
            "about_content": config["about_content"],
            "config_object": config["la_config_object"],
            "display_races": display_races,
            "objects": queryset.filter(city="City of Los Angeles"),
        }

class CandidateDetailView(BuildableDetailView):
    model = Candidate
    template_name = "elections_spring2015/detail.html"
    slug_field = "candidate_slug"
    def get_object(self):
        object = super(CandidateDetailView, self).get_object()
        return object
    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        config = yaml.load(open("elections_spring2015/config.yml"))
        context["slug"] = self.object.candidate_slug
        if self.object.city == "City of Pasadena":
            context["article_content"] = config["pasadena_article_content"]
            context["config_object"] = config["pasadena_config_object"]
        elif self.object.city == "City of Los Angeles":
            context["article_content"] = config["la_article_content"]
            context["config_object"] = config["la_config_object"]
        context["about_content"] = config["about_content"]
        return context