from django.contrib import admin
from . import models



# 需要后台接口
admin.site.register(models.ApiCases)
admin.site.register(models.ApiCreatedtasks)

# Register your models here.
