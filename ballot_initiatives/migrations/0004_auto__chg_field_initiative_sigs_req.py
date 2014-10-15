# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Initiative.sigs_req'
        db.alter_column(u'ballot_initiatives_initiative', 'sigs_req', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

    def backwards(self, orm):

        # Changing field 'Initiative.sigs_req'
        db.alter_column(u'ballot_initiatives_initiative', 'sigs_req', self.gf('django.db.models.fields.IntegerField')(null=True))

    models = {
        u'ballot_initiatives.initiative': {
            'Meta': {'object_name': 'Initiative'},
            'ag_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'date_circulation_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_failed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_qualified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_raw_count_due': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_sample_due': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_sum': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'election': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fiscal_impact_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'full_text_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_note': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'prop_num': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'proponent': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sig_count_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sigs_req': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'sos_id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '9999', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '999', 'blank': 'True'})
        }
    }

    complete_apps = ['ballot_initiatives']