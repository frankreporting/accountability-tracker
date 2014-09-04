# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Initiative.deadline'
        db.delete_column(u'ballot_initiatives_initiative', 'deadline')

        # Deleting field 'Initiative.sig_req'
        db.delete_column(u'ballot_initiatives_initiative', 'sig_req')

        # Deleting field 'Initiative.sum_date'
        db.delete_column(u'ballot_initiatives_initiative', 'sum_date')

        # Adding field 'Initiative.date_sum'
        db.add_column(u'ballot_initiatives_initiative', 'date_sum',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.date_circulation_deadline'
        db.add_column(u'ballot_initiatives_initiative', 'date_circulation_deadline',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.sigs_req'
        db.add_column(u'ballot_initiatives_initiative', 'sigs_req',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Initiative.date_qualified'
        db.add_column(u'ballot_initiatives_initiative', 'date_qualified',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.date_failed'
        db.add_column(u'ballot_initiatives_initiative', 'date_failed',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.date_sample_due'
        db.add_column(u'ballot_initiatives_initiative', 'date_sample_due',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.date_raw_count_due'
        db.add_column(u'ballot_initiatives_initiative', 'date_raw_count_due',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.election'
        db.add_column(u'ballot_initiatives_initiative', 'election',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=200),
                      keep_default=False)

        # Adding field 'Initiative.prop_num'
        db.add_column(u'ballot_initiatives_initiative', 'prop_num',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=10),
                      keep_default=False)

        # Adding field 'Initiative.full_text_link'
        db.add_column(u'ballot_initiatives_initiative', 'full_text_link',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=200),
                      keep_default=False)

        # Adding field 'Initiative.sig_count_link'
        db.add_column(u'ballot_initiatives_initiative', 'sig_count_link',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=200),
                      keep_default=False)

        # Adding field 'Initiative.fiscal_impact_link'
        db.add_column(u'ballot_initiatives_initiative', 'fiscal_impact_link',
                      self.gf('django.db.models.fields.CharField')(default='N/A', max_length=200),
                      keep_default=False)


        # Changing field 'Initiative.status'
        db.alter_column(u'ballot_initiatives_initiative', 'status', self.gf('django.db.models.fields.CharField')(max_length=50))

    def backwards(self, orm):
        # Adding field 'Initiative.deadline'
        db.add_column(u'ballot_initiatives_initiative', 'deadline',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Adding field 'Initiative.sig_req'
        db.add_column(u'ballot_initiatives_initiative', 'sig_req',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Initiative.sum_date'
        db.add_column(u'ballot_initiatives_initiative', 'sum_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 9, 3, 0, 0)),
                      keep_default=False)

        # Deleting field 'Initiative.date_sum'
        db.delete_column(u'ballot_initiatives_initiative', 'date_sum')

        # Deleting field 'Initiative.date_circulation_deadline'
        db.delete_column(u'ballot_initiatives_initiative', 'date_circulation_deadline')

        # Deleting field 'Initiative.sigs_req'
        db.delete_column(u'ballot_initiatives_initiative', 'sigs_req')

        # Deleting field 'Initiative.date_qualified'
        db.delete_column(u'ballot_initiatives_initiative', 'date_qualified')

        # Deleting field 'Initiative.date_failed'
        db.delete_column(u'ballot_initiatives_initiative', 'date_failed')

        # Deleting field 'Initiative.date_sample_due'
        db.delete_column(u'ballot_initiatives_initiative', 'date_sample_due')

        # Deleting field 'Initiative.date_raw_count_due'
        db.delete_column(u'ballot_initiatives_initiative', 'date_raw_count_due')

        # Deleting field 'Initiative.election'
        db.delete_column(u'ballot_initiatives_initiative', 'election')

        # Deleting field 'Initiative.prop_num'
        db.delete_column(u'ballot_initiatives_initiative', 'prop_num')

        # Deleting field 'Initiative.full_text_link'
        db.delete_column(u'ballot_initiatives_initiative', 'full_text_link')

        # Deleting field 'Initiative.sig_count_link'
        db.delete_column(u'ballot_initiatives_initiative', 'sig_count_link')

        # Deleting field 'Initiative.fiscal_impact_link'
        db.delete_column(u'ballot_initiatives_initiative', 'fiscal_impact_link')


        # Changing field 'Initiative.status'
        db.alter_column(u'ballot_initiatives_initiative', 'status', self.gf('django.db.models.fields.CharField')(max_length=20))

    models = {
        u'ballot_initiatives.initiative': {
            'Meta': {'object_name': 'Initiative'},
            'ag_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'date_circulation_deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'date_failed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_qualified': ('django.db.models.fields.DateTimeField', [], {}),
            'date_raw_count_due': ('django.db.models.fields.DateTimeField', [], {}),
            'date_sample_due': ('django.db.models.fields.DateTimeField', [], {}),
            'date_sum': ('django.db.models.fields.DateTimeField', [], {}),
            'election': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fiscal_impact_link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'full_text_link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_note': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'prop_num': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'proponent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sig_count_link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sigs_req': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sos_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '9999'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '999'})
        }
    }

    complete_apps = ['ballot_initiatives']