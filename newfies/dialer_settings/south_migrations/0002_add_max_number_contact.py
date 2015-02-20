# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DialerSetting.max_number_contact'
        db.add_column('dialer_setting', 'max_number_contact',
                      self.gf('django.db.models.fields.IntegerField')(default=1000000),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'DialerSetting.max_number_contact'
        db.delete_column('dialer_setting', 'max_number_contact')

    models = {
        u'dialer_settings.dialersetting': {
            'Meta': {'object_name': 'DialerSetting', 'db_table': "'dialer_setting'"},
            'blacklist': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'max_frequency': ('django.db.models.fields.IntegerField', [], {'default': "'5000'", 'null': 'True', 'blank': 'True'}),
            'max_number_campaign': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'max_number_contact': ('django.db.models.fields.IntegerField', [], {'default': '1000000'}),
            'max_number_subscriber_campaign': ('django.db.models.fields.IntegerField', [], {'default': '1000000'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'whitelist': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dialer_settings']
