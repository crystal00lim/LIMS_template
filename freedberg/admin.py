from django.contrib import admin
from django.db import models
from .models import Sample, Culture, Isolate
from django import forms
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class SampleResource(resources.ModelResource):
    class Meta:
        model = Sample
        fields = ('id', 'sample_id', 'sample_num', 'sample_type', 'sixteen_s', 'extraction', 'sixteen_s_finished', 'date', 'box', 'position', 'notes') 

@admin.register(Sample)
class SampleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = SampleResource
    list_display = (
        'sample_id',
        'sample_num',
        'sample_type',
        'sixteen_s',
        'extraction',
        'sixteen_s_finished',
        'date',
        'box',
        'position',
    )
    list_filter = (
        'sample_type',
        'sixteen_s',
        'extraction',
        'sixteen_s_finished',
    )
    search_fields = [
        'sample_id', 
        'sample_num', 
        'sample_type'
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        target_fields = ['sixteen_s', 'extraction', 'sixteen_s_finished']
        if db_field.name in target_fields:
            kwargs['widget'] = forms.RadioSelect(
                attrs = {'class': 'horizontal-radios'},
                choices = [
                    (True, 'Yes'),
                    (False, 'No'),
                    (None, 'NA'),
                ]
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media: 
            css = {
                'all': ('css/admin.css',) 
            }

class CultureResource(resources.ModelResource):
    sample_id = fields.Field(
        column_name='sample_id',
        attribute='sample_id',
        widget=ForeignKeyWidget(Sample, 'sample_id') 
    )
    class Meta:
        model = Culture
        fields = ('id', 'sample_id', 'vre_blue', 'vre_pink', 'kpc_blue', 'kpc_pink', 'date', 'notes')

@admin.register(Culture)
class CultureAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    autocomplete_fields = ['sample_id']
    resource_class = CultureResource
    list_display = (
        'sample_id',
        'get_type',
        'vre_blue',
        'vre_pink',
        'kpc_blue',
        'kpc_pink',
        'kpc_white',
        'date',
        'notes',
    )
    list_filter = (
        'sample_id__sample_type',
    )
    search_fields = [
        'sample_id__sample_id'
    ]

    @admin.display(description='Sample Type')
    def get_type(self, obj):
        if obj.sample_id:
            return obj.sample_id.get_sample_type_display()
        return "-"

    fieldsets = (
        (None, {
            'fields': ('sample_id', 'date', 'notes')
        }),
        ('Test Results', {
            'fields': (
                'vre_blue',
                'vre_pink',
                'kpc_blue',
                'kpc_pink',
                'kpc_white',
            )
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        target_fields = ['vre_blue', 'vre_pink', 'kpc_blue', 'kpc_pink', 'kpc_white']
        if db_field.name in target_fields:
            kwargs['widget'] = forms.RadioSelect(
                attrs = {'class': 'horizontal-radios'},
                choices = [
                    (True, 'Yes'),
                    (False, 'No'),
                ]
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    
    class Media:
        css = {
            'all': ('css/admin.css',)
        }

class IsolateResource(resources.ModelResource):
    sample_id = fields.Field(
        column_name = 'sample_id',
        attribute = 'sample_id',
        widget = ForeignKeyWidget(Culture, 'sample_id__sample_id')
    )

    class Meta:
        model = Isolate
        fields = ('id', 'isolate_id', 'sample_id', 'isolate_type', 'box', 'position', 'status', 'notes', 'date')

@admin.register(Isolate)
class IsolateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    autocomplete_fields = ['sample_id']
    resource_class = IsolateResource
    list_display = (
        'isolate_id',
        'isolate_type',
        'box',
        'position',
        'status',
        'notes',
    )
    list_filter = (
        'isolate_type',
        'status',
    )
    search_fields = [
        'isolate_id',
        'sample_id__sample_id__sample_id',
    ]
