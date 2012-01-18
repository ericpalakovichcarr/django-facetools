# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TestUser'
        db.create_table('facetools_testuser', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('facebook_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('facetools', ['TestUser'])


    def backwards(self, orm):
        
        # Deleting model 'TestUser'
        db.delete_table('facetools_testuser')


    models = {
        'facetools.testuser': {
            'Meta': {'object_name': 'TestUser'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['facetools']
