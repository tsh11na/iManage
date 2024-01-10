import datetime

from django.db import models
from django.utils import timezone
from django import forms


class ModelInfo(models.Model):
    model_id = models.AutoField('モデルID',
                                primary_key=True)
    pc_or_display = models.CharField(
        '区分', max_length=100, choices=(('pc', 'PC'), ('display', 'ディスプレイ'),))
    desk_or_lap = models.CharField('種類', max_length=100,
                                   choices=(('desktop', 'デスクトップPC'), ('laptop', 'ノートPC'),), null=True)
    model_name = models.CharField('モデル名', max_length=100)
    maker = models.CharField('メーカー', max_length=100)
    release_date = models.DateField('発売日')

    class Meta:
        unique_together = ('pc_or_display', 'model_name',
                           'maker', 'release_date',)
        verbose_name = "モデル"  # model-name on admin/imapp/$MODEL
        verbose_name_plural = "モデル"  # model-name on admin/imapp

    def __str__(self):
        return str(self.model_name)


class DisplayInfo(models.Model):
    model_id = models.OneToOneField(
        ModelInfo,
        related_name="related_model_id",
        on_delete=models.CASCADE, primary_key=True)
    inch = models.FloatField('インチ', default=24.0)

    class Meta:
        verbose_name = "ディスプレイ情報"
        verbose_name_plural = "ディスプレイ情報"

    def __str__(self):
        return str(self.inch)


class Equipment(models.Model):
    sam = models.CharField('SAM', max_length=100, primary_key=True)
    pc_or_display = models.CharField('区分', max_length=100, choices=(
        ('pc', 'PC'),
        ('display', 'ディスプレイ'),))
    purchase = models.DateField('購入日')
    warranty = models.DateField('保証期限')
    note = models.TextField('備考', blank=True)
    model_id = models.ForeignKey(ModelInfo, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "備品 (PC)"
        verbose_name_plural = "備品 (PC)"

    def __str__(self):
        return str(self.sam)


class OsId(models.Model):
    os_id = models.AutoField('OSID', primary_key=True)
    os = models.CharField('OS', max_length=100, unique=True)

    class Meta:
        verbose_name = "OS"
        verbose_name_plural = "OS"

    def __str__(self):
        return str(self.os)


class CpuId(models.Model):
    cpu_id = models.AutoField('CPU',
                              primary_key=True)
    cpu = models.CharField('CPU', max_length=100, unique=True)

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPU"

    def __str__(self):
        return str(self.cpu)


class DriveId(models.Model):
    drive_id = models.AutoField('ドライブID', primary_key=True)
    drive = models.CharField('ドライブ', max_length=100, unique=True)

    class Meta:
        verbose_name = "ドライブ"
        verbose_name_plural = "ドライブ"

    def __str__(self):
        return str(self.drive)

class MemoryId(models.Model):
    memory_id = models.AutoField('メモリID', primary_key=True)
    memory = models.CharField('メモリ', max_length=100, unique=True)

    class Meta:
        verbose_name = "メモリ"
        verbose_name_plural = "メモリ"

    def __str__(self):
        return str(self.memory)

class PcEquipment(models.Model):
    sam = models.OneToOneField(
        Equipment,
        related_name="related_sam_id",
        on_delete=models.CASCADE, primary_key=True)
    os_id = models.ForeignKey(OsId, on_delete=models.PROTECT)
    cpu_id = models.ForeignKey(CpuId,
                               on_delete=models.PROTECT)
    drive_id = models.ForeignKey(DriveId, on_delete=models.PROTECT)
    memory_id = models.ForeignKey(MemoryId, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "PC備品"
        verbose_name_plural = "PC備品"

    def __str__(self):
        return str(self.sam)


class User(models.Model):
    YEAR_CHOICES = []
    for r in range(2006, (datetime.datetime.now().year+1)):
        YEAR_CHOICES.append((r, r))
    YEAR_CHOICES.sort(reverse=True)
    user_id = models.AutoField('利用者ID', primary_key=True)
    username = models.CharField('利用者名', max_length=100)
    assigned_year = models.IntegerField(
        '配属年度', choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    is_affiliated = models.BooleanField('現役？', default=True)

    class Meta:
        unique_together = ('username', 'assigned_year',)
        verbose_name = "利用者"
        verbose_name_plural = "利用者"

    def judge_affiliation(self):
        return self.is_affiliated

    judge_affiliation.admin_order_field = 'is_affiliated'
    judge_affiliation.boolean = True
    judge_affiliation.short_description = "現役?????"

    def __str__(self):
        return str(self.username) + " (" + str(self.assigned_year) + "年配属) "


class Log(models.Model):
    """
    'id' is automatically made and set as a primary key.
    """
    sam = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    begin_date = models.DateField('使用開始日')
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sam', 'begin_date', 'user_id',)
        verbose_name = "ログ"
        verbose_name_plural = "ログ ⚠基本的に使用しないこと⚠"

    def __str__(self):
        return "(" + str(self.sam) + ", " + str(self.user_id.username) + ", " + str(self.begin_date) + ")"
