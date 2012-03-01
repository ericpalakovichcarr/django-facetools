# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'TestUser.facebook_id'
        db.alter_column('facetools_testuser', 'facebook_id', self.gf('django.db.models.fields.BigIntegerField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'TestUser.facebook_id'
        db.alter_column('facetools_testuser', 'facebook_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))


    models = {
        'facetools.testuser': {
            'Meta': {'object_name': 'TestUser'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'login_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['facetools']
