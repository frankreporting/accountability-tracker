# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Initiative'
        db.create_table(u'ballot_initiatives_initiative', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ag_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('id_note', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sos_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=999)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=9999)),
            ('proponent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sum_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
            ('sig_req', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'ballot_initiatives', ['Initiative'])


    def backwards(self, orm):
        # Deleting model 'Initiative'
        db.delete_table(u'ballot_initiatives_initiative')


    models = {
        u'ballot_initiatives.initiative': {
            'Meta': {'object_name': 'Initiative'},
            'ag_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_note': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'proponent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sig_req': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sos_id': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sum_date': ('django.db.models.fields.DateTimeField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '9999'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '999'})
        }
    }

    complete_apps = ['ballot_initiatives']