from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Library, Context
from django.conf import settings
from django.utils.timezone import utc
from django.db.models import Q, Avg, Max, Min, Sum, Count
from dateutil import parser
from datetime import datetime, date, time, timedelta
import logging

#logger = logging.getLogger("root")
#logging.basicConfig(
    #format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    #level=logging.DEBUG
#)

logger = logging.getLogger("accountability_tracker")

register = Library()

def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

register.filter(currency)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()