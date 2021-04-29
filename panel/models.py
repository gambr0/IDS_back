# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class NetworkClass(models.Model):
    index = models.BigIntegerField(primary_key=True)
    src_ip = models.TextField(db_column='Src IP', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    src_port = models.BigIntegerField(db_column='Src Port', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    dst_ip = models.TextField(db_column='Dst IP', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    dst_port = models.BigIntegerField(db_column='Dst Port', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    timestamp = models.TextField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.
    class_field = models.TextField(db_column='Class', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.

    class Meta:
        managed = True
        db_table = 'network_class'

    @staticmethod
    def get_all():
        data = NetworkClass.objects.all().order_by('-index')
        return data