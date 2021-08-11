from django.db import models


class JenkinsJob(models.Model):
    job_name = models.CharField(max_length=50, blank=True, null=True)
    build_number = models.AutoField(unique=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    dir_name = models.CharField(max_length=200, blank=True, null=True)
    log_name = models.CharField(max_length=200, blank=True, null=True)
    rmp_name = models.CharField(max_length=200, blank=True, null=True)
    log_content = models.TextField(blank=True, null=True)
    rpm_command = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jenkins_job'
