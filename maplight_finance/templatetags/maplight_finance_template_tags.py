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

logger = logging.getLogger("accountability_tracker")

register = Library()

def currency(dollars):
    #dollars = round(float(dollars), 2)
    dollars = round(int(dollars), 2)
    #return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
    return "$%s" % (intcomma(int(dollars)))

@register.simple_tag
def contribs_as_percent(support_dollars, oppose_dollars):
    total_contributions = support_dollars + oppose_dollars
    support_percent = (support_dollars / total_contributions) * 100
    support_percent = round(support_percent, 2)
    oppose_percent = (oppose_dollars / total_contributions) * 100
    oppose_percent = round(oppose_percent, 2)

    if support_percent > oppose_percent:
        start_angle = -90
        end_angle = 90
    elif support_percent < oppose_percent:
        start_angle = 90
        end_angle = -90
    output = {
        "support_percent": support_percent,
        "oppose_percent": oppose_percent,
        "start_angle": start_angle,
        "end_angle": end_angle
    }
    return json.dumps(output)

register.filter(currency)
register.filter(contribs_as_percent)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()