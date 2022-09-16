from django.contrib import admin
from . import models
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
# Register your models here.

class RuleAdmin(ImportExportModelAdmin):
    list_display = ('Name','Hat','Gloves','Vest','Boot','Glasses','Mask')

class PersonnelAdmin(ImportExportModelAdmin):
    def image_tag(self, obj):
        return format_html('<img src="{}"  width="50px" />'.format(obj.Photo.url))
    list_display = ('image_tag','Name','UniqueID','EmiratesID','ContactNo','Created','Modified')
    list_filter = ('Created',('Created', DateRangeFilter))
    search_fields = ['Name','UniqueID','EmiratesID','ContactNo','Created','Modified']
    image_tag.short_description = 'Photo'
    #list_display = ['image_tag']
    readonly_fields = ['image_tag']

class DeviceAdmin(ImportExportModelAdmin):
    list_display = ('Name','UniqueID','Enable','Created','Modified')
    list_filter = ('Created','Modified',('Created', DateRangeFilter))
    search_fields = ['Name','UniqueID']

class EventAdmin(ImportExportModelAdmin):
    list_display = ('EventID','Person','Rule','Device','Lattitude','Longitude','action','processed','created')
    list_filter = ('created',('created', DateTimeRangeFilter))

class HealthScanAdmin(ImportExportModelAdmin):
    list_display = ('EventID','Name','IDn','CodeType','GenTime','PCRDate','PCRResult','created')
    list_filter = ('created',('created', DateRangeFilter),'CodeType','PCRResult')

class SafetyScanAdmin(ImportExportModelAdmin):
    list_display = ('EventID','Hat','Gloves','Vest','Boot','Glasses','Mask','created')
    list_filter = ('created',('created', DateRangeFilter),'Hat','Gloves','Vest','Boot','Glasses','Mask')


admin.site.register(models.Event,EventAdmin)
admin.site.register(models.HealthScan,HealthScanAdmin)
admin.site.register(models.SafetyScan,SafetyScanAdmin)
admin.site.register(models.Rule,RuleAdmin)
admin.site.register(models.Personnel,PersonnelAdmin)
admin.site.register(models.Device,DeviceAdmin)
