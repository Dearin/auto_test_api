# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class JenkinsJob(models.Model):
    id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    dir_name = models.CharField(max_length=200, blank=True, null=True)
    log_name = models.CharField(max_length=200, blank=True, null=True)
    rmp_name = models.CharField(max_length=200, blank=True, null=True)
    log_content = models.TextField(blank=True, null=True)
    rpm_command = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    build_number = models.BigIntegerField(null=False)

    class Meta:
        managed = False
        db_table = 'jenkins_job'





