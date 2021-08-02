from django.db import models
from libs.mixins import ModelMixin
# Create your models here.


class RemoteHost(models.Model, ModelMixin):
	models.AutoField(primary_key=True)  # 设置AutoField，不要加default属性
	host = models.GenericIPAddressField(verbose_name=u'IP地址', max_length=30, blank=False, unique=True)


	def __str__(self):
		return self.host

	class Meta:
		db_table = "remote_host"
		verbose_name = u"远程登陆设备"
		verbose_name_plural = verbose_name
