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

def neg_to_posi(value):
    return abs(value)

def get_last_year(value):
    last_year = value.year-2
    output = date(last_year, value.month, value.day)
    return output

@register.filter
def percentage(value):
    return "%s percent" % (value*100)

@register.simple_tag
def standardize_unit_to_gallons(value, unit):
    if unit == "G":
        output = (value * 1)
    elif unit == "MG":
        output = (value * 1000000)
    elif unit == "CCF":
        output = (value * 748)
    elif unit == "AF":
        output = (value * 325851)
    else:
        output = "outlier"
    return output

@register.simple_tag
def build_chart_sentence(data):
    number_of_records = len(data)
    newest_record = data[0]
    oldest_record = data[-1]
    percent_change = calculate.percentage_change(oldest_record, newest_record)
    if percent_change > 0:
        change_trend = "increased"
    else:
        change_trend = "decreased"
    return "And over the past %s months, this supplier and its consumers have %s water use by %s%%, going from %s gallons used per person per day to %s gallons used per person per day." % (number_of_records, change_trend, round(percent_change, 2), round(oldest_record, 2), round(newest_record, 2))

@register.simple_tag
def increase_or_decrease(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        #output = "decreased by %s percent" % ("%.2f" % round(percent_change, 2))
        output = "increased"
    else:
        #output = "increased by %s percent" % ("%.2f" % round(percent_change, 2))
        output = "decreased"
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
def app_config_object(input):
    return json.dumps(input)

register.filter(neg_to_posi)
register.filter(get_last_year)
register.filter(percentage)
register.filter(standardize_unit_to_gallons)
register.filter(build_chart_sentence)
register.filter(increase_or_decrease)
register.filter(app_config_object)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()