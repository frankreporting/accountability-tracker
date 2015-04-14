from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Library, Context
from django.conf import settings
from django.utils.timezone import utc
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from dateutil import parser
from datetime import datetime, date, time, timedelta
import re
import json
import logging

logger = logging.getLogger("accountability_tracker")

register = Library()

def image_path(value):
    value = value.encode("ascii", "ignore").lower().strip().replace(" ", "_")
    value = re.sub(r"[^\w-]", "", value)
    return "%s.jpg" % (value)

@register.simple_tag
def app_config_object(input):
    return json.dumps(input)

register.filter(image_path)
register.filter(app_config_object)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()