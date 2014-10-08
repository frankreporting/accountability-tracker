from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from django.db.models import Q, Avg, Max, Min, Sum, Count
from maplight_finance.models import Initiative, InitiativeContributor
from bakery.views import BuildableListView, BuildableDetailView
import logging

#logger = logging.getLogger("root")
#logging.basicConfig(
    #format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    #level=logging.DEBUG
#)

logger = logging.getLogger("accountability_tracker")

# Create your views here.
@xframe_options_sameorigin
def index(request):
    contributions = InitiativeContributor.objects.all()
    supporting_contributions = contributions.filter(stance="Support")
    opposing_contributions = contributions.filter(stance="Oppose")
    total_sum = contributions.values("initiative_identifier").annotate(total=Sum("amount"))
    supporting_sum = supporting_contributions.values("initiative_identifier").annotate(total=Sum("amount"))
    opposing_sum = opposing_contributions.values("initiative_identifier").annotate(total=Sum("amount"))
    return render_to_response("index.html", {
        "total_sum": total_sum,
        "supporting_sum": supporting_sum,
        "opposing_sum": opposing_sum
    })


class InitialListView(BuildableListView):
    """ """
    model = Initiative
    #queryset = InitiativeContributor.objects.values("initiative_identifier").annotate(total=Sum("amount"))
    template_name = "index.html"


class InitialDetailView(BuildableDetailView):
    """ """
    model = Initiative
    template_name = "detail.html"
    slug_field = "initiative_slug"

    def get_object(self):
        object = super(InitialDetailView, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(InitialDetailView, self).get_context_data(**kwargs)
        initiative_id = self.object.id
        contributions = InitiativeContributor.objects.filter(initiative_identifier_id = initiative_id)
        total_contributions = contributions.values("initiative_identifier").annotate(total=Sum("amount"))
        total_support = contributions.filter(stance="Support").values("initiative_identifier").annotate(total=Sum("amount"))
        total_opposition = contributions.filter(stance="Oppose").values("initiative_identifier").annotate(total=Sum("amount"))
        supporting_contributions = contributions.filter(stance="Support").order_by('-amount')[0:5]
        opposing_contributions = contributions.filter(stance="Oppose").order_by('-amount')[0:5]
        context["total_contributions"] = total_contributions
        context["total_contributions"] = context["total_contributions"][0]["total"]
        context["total_support"] = total_support
        context["total_support"] = context["total_support"][0]["total"]
        context["total_opposition"] = total_opposition
        context["total_opposition"] = context["total_opposition"][0]["total"]
        context["supporting_contributions"] = supporting_contributions
        context["opposing_contributions"] = opposing_contributions
        return context
