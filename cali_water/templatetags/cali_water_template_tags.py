from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Library, Context
from django.conf import settings
from django.utils.timezone import utc
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from dateutil import parser
from datetime import datetime, date, time, timedelta
import json
import logging
import decimal
import calculate

logger = logging.getLogger("accountability_tracker")

register = Library()

@register.filter
def currency(dollars):
    dollars = round(int(dollars), 2)
    return "$%s" % (intcomma(int(dollars)))

@register.filter
def neg_to_posi(value):
    return abs(value)

@register.filter
def get_last_year(value):
    last_year = value.year-2
    output = date(last_year, value.month, value.day)
    return output

@register.filter
def percentage(value):
    return "%s%%" % (value*100)

@register.simple_tag
def standardize_unit_to_gallons(value, unit):
    if unit.upper() == "G":
        output = (value * 1)
    elif unit.upper() == "MG":
        output = (value * 1000000)
    elif unit.upper() == "CCF":
        output = (value * 748)
    elif unit.upper() == "AF":
        output = (value * 325851)
    else:
        output = (value * 1)
    return output

@register.simple_tag
def build_chart_title(data):
    number_of_records = len(data)
    newest_record = data[0]
    oldest_record = data[-1]
    percent_change = calculate.percentage_change(oldest_record, newest_record)
    if percent_change > 0:
        change_trend = "<span class='increase-accent'>Increased</span>"
    else:
        change_trend = "<span class='decrease-accent'>Decreased</span>"
    return change_trend

@register.simple_tag
def build_chart_sentence(data):
    number_of_records = len(data)
    newest_record = data[0]
    oldest_record = data[-1]
    percent_change = calculate.percentage_change(oldest_record, newest_record)
    if percent_change > 0:
        change_trend = "<span class='increase-accent'>increased</span>"
    else:
        change_trend = "<span class='decrease-accent'>decreased</span>"
    return "Over the past %s months, water use by this agency's residential customers has %s by %s%%, going from %s residential gallons used daily per capita to %s residential gallons used daily per capita." % (number_of_records, change_trend, round(percent_change, 2), round(oldest_record, 2), round(newest_record, 2))

@register.simple_tag
def increase_or_decrease(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        output = "<span class='increase-accent'>increased</span>"
    else:
        output = "<span class='decrease-accent'>decreased</span>"
    return output

@register.simple_tag
def settings_value(name):
    output = getattr(settings, name, "")
    return output

@register.simple_tag
def no_span_increase_or_decrease(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        output = "increased"
    else:
        output = "decreased"
    return output

@register.simple_tag
def compare_to_avg(state_figure, local_figure):
    percent_change = calculate.percentage_change(state_figure, local_figure)
    if local_figure > state_figure:
        percent_change = "%.2f" % round(percent_change, 2)
        output = "<span class='increase-accent'>more</span>"
    else:
        percent_change = "%.2f" % round(percent_change, 2)
        output = "<span class='decrease-accent'>less</span>"
    return output

@register.simple_tag
def percent_change(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        percent_change = "%.2f" % round(percent_change, 2)
        output = "<span class='increase-accent'>+%s%%</span>" % (percent_change)
    else:
        percent_change = "%.2f" % round(percent_change, 2)
        output = "<span class='decrease-accent'>%s%%</span>" % (percent_change)
    return output

@register.simple_tag
def change_in_reduction_tier(latest_proposal, prior_proposal):
    if latest_proposal == None and prior_proposal == None:
        output = "n/a"
    else:
        if latest_proposal == prior_proposal:
            output = "No Change"
        elif latest_proposal > prior_proposal:
            output = "Increased"
        elif latest_proposal < prior_proposal:
            output = "Decreased"
        else:
            output = "n/a"
    return output

@register.simple_tag
def app_config_object(input):
    return json.dumps(input)

register.filter(currency)
register.filter(neg_to_posi)
register.filter(get_last_year)
register.filter(percentage)
register.filter(standardize_unit_to_gallons)
register.filter(build_chart_sentence)
register.filter(increase_or_decrease)
register.filter(settings_value)
register.filter(no_span_increase_or_decrease)
register.filter(compare_to_avg)
register.filter(percent_change)
register.filter(change_in_reduction_tier)
register.filter(app_config_object)