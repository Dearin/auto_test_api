from django.db import models

# Create your models here.
class ApiCreatedtasks(models.Model):
    id = models.BigAutoField(primary_key=True)
    task_name = models.CharField(max_length=50)
    task_type = models.CharField(max_length=50)
    version = models.CharField(max_length=100)
    bussiness_branch = models.CharField(max_length=120)
    basepacket_branch = models.CharField(max_length=120)
    module = models.CharField(max_length=50)
    process = models.CharField(max_length=50, blank=True, null=True)
    build_number = models.CharField(max_length=20, blank=True, null=True)
    build_job = models.CharField(max_length=255, blank=True, null=True)
    cases = models.TextField()
    cases_count = models.CharField(max_length=50, blank=True, null=True)
    dns_ver = models.CharField(max_length=20, blank=True, null=True)
    zdnf_conf_len = models.CharField(max_length=10, blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    test_envir = models.CharField(max_length=50)
    master_ip1 = models.CharField(max_length=50)
    master_ip2 = models.CharField(max_length=50)
    slave = models.CharField(max_length=50)
    master2 = models.CharField(max_length=50)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_createdtasks'

    def __str__(self):
        return self.apicreatedtasks_text


class ApiCases(models.Model):
    version = models.CharField(max_length=10, blank=True, null=True)
    module = models.CharField(max_length=50)
    case_en_name = models.CharField(unique=True, max_length=200)
    case_ch_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_cases'

    def __str__(self):
        return self.apicases_text

    # 获取对应模块用例集合
    def getCasesByModule(self,module_name):
        return self.module == module_name




