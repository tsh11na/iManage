from django.contrib import admin
from django.db import models
from django import forms
from .models import (
    CpuId,
    OsId,
    DriveId,
    MemoryId,
    ModelInfo,
    Equipment,
    DisplayInfo,
    PcEquipment,
    User,
    Log,
)
import django.contrib.auth.admin
import django.contrib.auth.models
from django.contrib import auth

from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import reverse

# *pc_or_display dividing classes*


class FormForPC(forms.ModelForm):
    PC_ONLY_CHOICE = (('pc', 'PC'),)
    pc_or_display = forms.ChoiceField(choices=PC_ONLY_CHOICE)


class FormForDisplay(forms.ModelForm):
    DISPLAY_ONLY_CHOICE = (('display', 'ディスプレイ'),)
    pc_or_display = forms.ChoiceField(choices=DISPLAY_ONLY_CHOICE)


class StatusFilterForPC(SimpleListFilter):
    title = "区分"
    parameter_name = "parameter-name"

    def lookups(self, request, model_admin):
        yield ("pc", _("PC"))

    def choices(self, cl):
        yield

    def queryset(self, request, queryset):
        return queryset.filter(pc_or_display="pc")


class StatusFilterForDisplay(SimpleListFilter):
    title = "区分"
    parameter_name = "parameter-name"

    def lookups(self, request, model_admin):
        yield ("display", _("ディスプレイ"))

    def choices(self, cl):
        yield

    def queryset(self, request, queryset):
        return queryset.filter(pc_or_display="display")


# CPU

class CPU_idAdmin(admin.ModelAdmin):
    list_display = ('cpu',)
    search_fields = ['cpu', ]

    # def has_add_permission(self, request):
    #    return True
    # def has_change_permission(self,request):
    #    return False
    # def has_delete_permission(self,request):
    #    return False


# OS

class OS_idAdmin(admin.ModelAdmin):
    list_display = ('os',)
    search_fields = ['os', ]


# Drives

class Drive_idAdmin(admin.ModelAdmin):
    list_display = ('drive',)
    search_fields = ['drive', ]


# Memory

class Memory_idAdmin(admin.ModelAdmin):
    list_display = ('memory',)
    search_fields = ['memory', ]


# Models (PC)

class Model_infoForPC(ModelInfo):
    class Meta:
        proxy = True
        verbose_name = "モデル (PC)"  # model-name on admin/imapp/$MODEL
        verbose_name_plural = "モデル (PC)"  # model-name on admin/imapp

    inlines = []


class Model_infoForPCAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'desk_or_lap', 'maker', 'release_date',)
    inlines = []
    form = FormForPC
    list_filter = [StatusFilterForPC]
    search_fields = ['model_name', ]


# Models (Display)

class Display_infoInline(admin.StackedInline):
    model = DisplayInfo


class Model_infoForDisplay(ModelInfo):
    class Meta:
        proxy = True
        verbose_name = "モデル (ディスプレイ)"
        verbose_name_plural = "モデル (ディスプレイ)"
    inlines = [Display_infoInline, ]


class Model_infoForDisplayAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'maker', 'release_date', '_inch')
    inlines = [Display_infoInline, ]
    form = FormForDisplay
    list_filter = [StatusFilterForDisplay]

    def _inch(self, obj):
        return DisplayInfo.objects.get(model_id_id=obj.model_id).inch

    _inch.short_description = "インチ"
    search_fields = ['model_name', ]


# Equipment (PC)

class PC_equipmentInline(admin.StackedInline):
    model = PcEquipment
    min_num = 1


class EquipmentForPC(Equipment):
    class Meta:
        proxy = True
        verbose_name = "備品 (PC)"
        verbose_name_plural = "備品 (PC)"

    inlines = [PC_equipmentInline, ]


class EquipmentForPCAdmin(admin.ModelAdmin):
    list_display = ('sam', '_DorL', '_model_name', '_maker',
                    '_OS', '_CPU', '_DRIVE','_MEMORY', 'purchase', 'warranty', 'note')
    inlines = [PC_equipmentInline, ]
    form = FormForPC
    list_filter = [StatusFilterForPC]

    # only show pc's model_ids in add/change pages
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['model_id'].queryset = ModelInfo.objects.filter(
            pc_or_display='pc')
        return super(EquipmentForPCAdmin, self).render_change_form(request, context, *args, **kwargs)

    def _DorL(self, obj):
        this_model = ModelInfo.objects.all().filter(
            model_id=obj.model_id_id).values()[0]
        return 'デスクトップPC' if this_model['desk_or_lap'] == 'desktop'else 'ノートPC'
    _DorL.short_description = "種類"

    def _OS(self, obj):
        return obj.related_sam_id.os_id.os

    def _CPU(self, obj):
        return obj.related_sam_id.cpu_id.cpu

    def _DRIVE(self, obj):
        return obj.related_sam_id.drive_id.drive
    _DRIVE.short_description = "ドライブ"

    def _MEMORY(self, obj):
        return obj.related_sam_id.memory_id.memory
    _MEMORY.short_description = "メモリ"

    def _model_name(self, obj):
        return obj.model_id.model_name
    _model_name.short_description = "モデル名"

    def _maker(self, obj):
        return obj.model_id.maker
    _maker.short_description = "メーカー"

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            print("SUPER DEBUG TIME :", request.POST)
            for a in request.POST:
                print("Cont is :", a)
            url = reverse("admin:imapp_equipmentforpc_add")
            purchase = request.POST['purchase']
            purchase_info = '?purchase=%s' % purchase
            warranty = request.POST['warranty']
            warranty_info = '&warranty=%s' % warranty
            note = request.POST['note']
            note_info = '&note=%s' % note
            model_id = request.POST['model_id']
            model_id_info = '&model_id=%s' % model_id
            related_sam_id_os_id = request.POST['related_sam_id-0-os_id']
            related_sam_id_os_id_info = '&id_related_sam_id-0-os_id=%s' % related_sam_id_os_id
            related_sam_id_cpu_id = request.POST['related_sam_id-0-cpu_id']
            related_sam_id_cpu_id_info = '&related_sam_id-0-cpu_id=%s' % related_sam_id_cpu_id
            related_sam_id_drive_id = request.POST['related_sam_id-0-drive_id']
            related_sam_id_drive_id_info = '&related_sam_id-0-drive_id=%s' % related_sam_id_drive_id

            query_set = purchase_info + warranty_info + note_info + model_id_info + \
                related_sam_id_os_id_info + related_sam_id_cpu_id_info + related_sam_id_drive_id_info
            return HttpResponseRedirect(''.join((url, query_set)))
        else:
            return HttpResponseRedirect(reverse("admin:imapp_equipmentforpc_changelist"))

    search_fields = ['sam', ]


# Equipment (Display)

class EquipmentForDisplay(Equipment):
    class Meta:
        proxy = True
        verbose_name = "備品 (ディスプレイ)"
        verbose_name_plural = "備品 (ディスプレイ)"

    inlines = []


class EquipmentForDisplayAdmin(admin.ModelAdmin):
    list_display = ('sam', '_model_name', '_maker', '_inch',
                    'purchase', 'warranty', 'note',)
    inlines = []
    form = FormForDisplay
    list_filter = [StatusFilterForDisplay]
    search_fields = ['sam', 'note', 'purchase']
    # only show display's model_ids in add/change pages

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['model_id'].queryset = ModelInfo.objects.filter(
            pc_or_display='display')
        return super(EquipmentForDisplayAdmin, self).render_change_form(request, context, *args, **kwargs)

    def _inch(self, obj):
        return DisplayInfo.objects.get(model_id_id=obj.model_id).inch
    _inch.short_description = "インチ"

    def _model_name(self, obj):
        return obj.model_id.model_name
    _model_name.short_description = "モデル名"

    def _maker(self, obj):
        return obj.model_id.maker
    _maker.short_description = "メーカー"

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            print("SUPER DEBUG TIME :", request.POST)
            for a in request.POST:
                print("Cont is :", a)
            url = reverse("admin:imapp_equipmentfordisplay_add")
            purchase = request.POST['purchase']
            purchase_info = '?purchase=%s' % purchase
            warranty = request.POST['warranty']
            warranty_info = '&warranty=%s' % warranty
            note = request.POST['note']
            note_info = '&note=%s' % note
            model_id = request.POST['model_id']
            model_id_info = '&model_id=%s' % model_id

            query_set = purchase_info + warranty_info + note_info + model_id_info
            return HttpResponseRedirect(''.join((url, query_set)))
        else:
            return HttpResponseRedirect(reverse("admin:imapp_equipmentfordisplay_changelist"))

    search_fields = ['sam', ]


# User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'assigned_year', 'is_affiliated',)
    list_filter = ['is_affiliated', ]
    search_fields = ['username', ]

# Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('_sam', 'begin_date', '_username')
    search_fields = ['sam__sam', ]

    def _sam(self, obj):
        return obj.sam_id

    def _username(self, obj):
        return obj.user_id.username
    _username.short_description = "利用者"


admin.site.register(CpuId, CPU_idAdmin)
admin.site.register(OsId, OS_idAdmin)
admin.site.register(DriveId, Drive_idAdmin)
admin.site.register(MemoryId, Memory_idAdmin)
admin.site.register(Model_infoForPC, Model_infoForPCAdmin)
admin.site.register(Model_infoForDisplay, Model_infoForDisplayAdmin)
admin.site.register(EquipmentForPC, EquipmentForPCAdmin)
admin.site.register(EquipmentForDisplay, EquipmentForDisplayAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Log, LogAdmin)

admin.site.unregister(auth.models.User)
admin.site.unregister(auth.models.Group)
