from django.contrib import admin
from ballot_initiatives.models import Initiative

# Register your models here.
class InitiativeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['sos_id','ag_id','id_note','title','summary','status','prop_num']}),
        ('Proponent info',{'fields':['proponent','email','phone'],'classes':['collapse']}),
        ('Date info',{'fields':['date_sum_estimate','date_sum','date_circulation_deadline','date_sample_due','date_raw_count_due','date_sample_update','date_qualified','date_failed'],'classes':['collapse']}),
        ('Documents',{'fields':['full_text_link','sig_count_link','fiscal_impact_link']}),
        ('Other/Misc',{'fields': ['election','proposition_type','sigs_req'],'classes':['collapse']}),
    ]

    list_display = (
        'title',
        'sos_id',
        'ag_id',
        'id_note',
        'proponent',
        'status',
        'prop_num'
    )

    search_fields = [
        'sos_id',
        'ag_id',
        'title',
        'summary',
        'proponent',
        'prop_num'
    ]

    list_filter = [
        'status'
    ]

admin.site.register(Initiative,InitiativeAdmin)