# Register your models here.
from maplight_finance.models import InitiativeContributor
from django.conf import settings
from django.contrib import admin
from django.utils.timezone import utc, localtime
import logging

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

class InitiativeContributorAdmin(admin.ModelAdmin):
    list_display = ("initiative_identifier", "name", "zip_code", "amount")
    list_per_page = 15
    search_fields = ["name"]
    list_filter = ["initiative_identifier"]
    ordering = ["-amount", "initiative_identifier"]

admin.site.register(InitiativeContributor, InitiativeContributorAdmin)