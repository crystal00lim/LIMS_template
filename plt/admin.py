from django.contrib import admin
from django.db import models
from .models import Patient, Stool, StoolAliquot, Isolate, IsolateStock, WGS
from django import forms
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient
        fields = ('id', 'patient_id', 'liver_cub', 'enrollment_status', 'consent_date', 'txp_amount') 

@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = PatientResource
    list_display = (
        'patient_id', 
        'txp_amount', 
        'consent_date',
        'enrollment_status'
    )
    list_filter = (
        'txp_amount',
        'enrollment_status'
    )
    search_fields = [
        'patient_id',
    ]

class StoolResource(resources.ModelResource):
    class Meta:
        model = Stool
        fields = ('id', 'patient_id', 'stool_id', 'aliquots', 'date_collected', 'notes')

@admin.register(Stool)
class StoolAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StoolResource
    list_display = (
        'id', 
        'patient_id', 
        'stool_id', 
        'aliquots', 
        'date_collected', 
        'notes'
    )
    search_fields = [
        'id', 
        'patient_id', 
        'stool_id', 
        'aliquots', 
        'date_collected', 
        'notes'
    ]