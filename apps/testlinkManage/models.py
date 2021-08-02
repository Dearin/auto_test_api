from django.db import models
from libs.mixins import ModelMixin

# Create your models here.


class TestLinkCaseInfo(models.Model, ModelMixin):
    """测试用例信息"""
    RUN_TPYE = (
        (0, u'手工'),
        (1, u'API自动化'),
        (2, u'UI自动化'),
    )
    key = models.AutoField(primary_key=True) #设置AutoField，不要加default属性
    external_id = models.CharField(verbose_name=u'用例id', max_length=100, default='')
    name = models.CharField(verbose_name=u'用例名称', max_length=255, default='')
    auto_id = models.CharField(verbose_name=u'自动化id', max_length=255, default='')
    is_auto = models.BooleanField(verbose_name=u'是否自动化', default=False)
    is_smoke = models.BooleanField(verbose_name=u'是否冒烟用例', default=False)
    run_type = models.SmallIntegerField(verbose_name=u'执行类型', choices=RUN_TPYE, default=0)
    belong_to_module = models.CharField(verbose_name=u'所属模块', max_length=50, default='')
    belong_to_testsuit = models.CharField(verbose_name=u'所属用例集', max_length=50, default='')

    def __str__(self):
        return self.external_id

    class Meta:
        db_table = "test_case_info"
        verbose_name = u"测试用例信息"
        verbose_name_plural = verbose_name


class TestCaseStepIno(models.Model):
    """测试用例步骤和期望数据信息"""
    key = models.AutoField(primary_key=True)  # 设置AutoField，不要加default属性
    external_id = models.CharField(verbose_name=u'用例id', max_length=100, default='')
    case_test_steps = models.TextField(verbose_name=u'用例步骤', default='')
    case_expected_result = models.TextField(verbose_name=u'期望结果', default='')

    def __str__(self):
        return self.external_id

    class Meta:
        db_table = "test_case_step_info"
        verbose_name = u"测试用例步骤和期望数据信息"
        verbose_name_plural = verbose_name
