from django.contrib import admin
from django.db import models
from django import forms
from import_export import resources, fields
from import_export.widgets import Widget, ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin, ExportMixin, ExportActionModelAdmin
from .models import Participant, Culture, Isolate, Kb, WGS
from django.utils.translation import gettext_lazy as _
from taggit.models import Tag, TaggedItem

class TagWidget(ManyToManyWidget):
    def render(self, value, obj=None, **kwargs):
        if value is None:
            return ""
        try:
            return ", ".join([tag.name for tag in value.all()])
        except AttributeError:
            return ""

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []
        return [tag.strip() for tag in value.split(",") if tag.strip()]

    def save(self, obj, data, is_m2m=False, **kwargs):
        pass

class ParticipantStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'participant_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(status=True)
        if self.value() == 'inactive':
            return queryset.filter(status=False)
        return queryset

class ParticipantTreatmentFilter(admin.SimpleListFilter):
    title = _('treatment')
    parameter_name = 'treatment'
 
    def lookups(self, request, model_admin):
        return (
            ('doxycycline', _('Doxycycline')),
            ('control', _('Control')),
            ('unknown', _('Unknown')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'doxycycline':
            return queryset.filter(treatment=True)
        if self.value() == 'control':
            return queryset.filter(treatment=False)
        if self.value() == 'unknown':
            return queryset.filter(participant_type=None)
        return queryset

class ParticipantParticipantTypeFilter(admin.SimpleListFilter):
    title = _('participant_type')
    parameter_name = 'participant_type'

    def lookups(self, request, model_admin):
        return (
            ('participant', _('Participant')),
            ('partner', _('Partner')),
            ('unknown', _('Unknown')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'participant':
            return queryset.filter(participant_type=True)
        if self.value() == 'partner':
            return queryset.filter(participant_type=False)
        if self.value() == 'unknown':
            return queryset.filter(participant_type=None)
        return queryset

class ParticipantResource(resources.ModelResource):
    class Meta: 
        model = Participant
        fields = ('id', 'participant_id', 'status', 'treatment', 'participant_type')
 
@admin.register(Participant)
class ParticipantAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = ParticipantResource
    list_display = (
        'participant_id',
        'status',
        'treatment',
        'participant_type',
    )
    list_filter = (
       ParticipantStatusFilter,
       ParticipantTreatmentFilter,
       ParticipantParticipantTypeFilter,
    )
    search_fields = ['participant_id']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        custom_choices = {
            'status': [
                (True, 'Active'),
                (False, 'Inactive'),
            ],
            'treatment': [
                (True, 'Doxycycline'),
                (False, 'Control'),
                (None, 'Unknown'),
            ],
            'participant_type': [
                (True, 'Participant'),
                (False, 'Partner'),
                (None, 'Unknown'),
            ]
        }

        if db_field.name in custom_choices:
            kwargs['choices'] = custom_choices[db_field.name]
            kwargs['widget'] = forms.RadioSelect(
                attrs={'class': 'horizontal-radios'}
            )
            return db_field.formfield(form_class=forms.ChoiceField, **kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        css = {
            'all': ('css/admin.css',)
        }

class CultureStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'participant_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(participant_id__status=True)
        if self.value() == 'inactive':
            return queryset.filter(participant_id__status=False)
        return queryset

class CultureTreatmentFilter(admin.SimpleListFilter):
    title = _('treatment')
    parameter_name = 'treatment'
 
    def lookups(self, request, model_admin):
        return (
            ('doxycycline', _('Doxycycline')),
            ('control', _('Control')),
            ('unknown', _('Unknown')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'doxycycline':
            return queryset.filter(participant_id__treatment=True)
        if self.value() == 'control':
            return queryset.filter(participant_id__treatment=False)
        return queryset

class CultureParticipantTypeFilter(admin.SimpleListFilter):
    title = _('participant_type')
    parameter_name = 'participant_type'

    def lookups(self, request, model_admin):
        return (
            ('participant', _('Participant')),
            ('partner', _('Partner')),
            ('unknown', _('Unknown')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'participant':
            return queryset.filter(participant_id__participant_type=True)
        if self.value() == 'partner':
            return queryset.filter(participant_id__participant_type=False)
        return queryset

class CultureResource(resources.ModelResource):
    participant_id = fields.Field(
        column_name='participant_id',
        attribute='participant_id',
        widget=ForeignKeyWidget(Participant, 'participant_id')
    )

    class Meta:
        model = Culture
        fields = ('id', 'participant_id', 'visit_num', 'timepoint_id', 'phar_sa', 'rec_sa', 'rec_mac', 'rec_esbl', 'nas_sa', 'vag_sa', 'vag_mac', 'vag_esbl', 'date', 'notes')

@admin.register(Culture)
class CultureAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    autocomplete_fields = ['participant_id']
    resource_class = CultureResource
    list_display = (
        'timepoint_id', 
        'phar_sa',
        'rec_sa',
        'rec_mac',
        'rec_esbl',
        'nas_sa', 
        'vag_sa',
        'vag_mac',
        'vag_esbl',
        'notes'
    )
    list_filter = (
        'visit_num',
        CultureStatusFilter,
        CultureTreatmentFilter,
        CultureParticipantTypeFilter,
    )
    search_fields = [
        'participant_id__participant_id',
        'timepoint_id'
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        target_fields = ['phar_sa', 'rec_sa', 'rec_mac', 'rec_esbl', 'nas_sa', 'vag_sa', 'vag_mac', 'vag_esbl']
        if db_field.name in target_fields: 
            kwargs['widget'] = forms.RadioSelect(
                attrs = {'class': 'horizontal-radios'},
                choices = [
                    (True, 'Positive'),
                    (False, 'Negative'),
                    (None, 'NA'),
                ]   
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media: 
        css = {
            'all': ('css/admin.css',)
        }

    fieldsets = (
        (None, {
            'fields': ('participant_id', 'visit_num', 'date', 'notes') 
        }),
        ('Test Results', {
            'fields': (
                'phar_sa',
                'rec_sa',
                'rec_mac',
                'rec_esbl',
                'nas_sa',
                'vag_sa',
                'vag_mac',
                'vag_esbl',
            )
        }),
    )

class IsolateParticipantStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'participant_status'

    def lookups(self, request, model_admin):
        return (('active', _('Active')), ('inactive', _('Inactive')),)

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(timepoint_id__participant_id__status=True)
        if self.value() == 'inactive':
            return queryset.filter(timepoint_id__participant_id__status=False)
        return queryset

class IsolateTreatmentFilter(admin.SimpleListFilter):
    title = _('treatment')
    parameter_name = 'treatment'

    def lookups(self, request, model_admin):
        return (
            ('doxycycline', _('Doxycycline')),
            ('control', _('Control')),
            ('unknown', _('Unknown')),
        )
 
    def queryset(self, request, queryset):
        if self.value() == 'doxycycline':
            return queryset.filter(timepoint_id__participant_id__treatment=True)
        if self.value() == 'control':
            return queryset.filter(timepoint_id__participant_id__treatment=False)
        if self.value() == 'unknown':
            return queryset.filter(timepoint_id__participant_id__treatment=None)
        return queryset

class IsolateParticipantTypeFilter(admin.SimpleListFilter): 
    title = _('participant_type')
    parameter_name = 'participant_type'

    def lookups(self, request, model_admin):
        return (
            ('participant', _('Participant')),
            ('partner', _('Partner')),
            ('unknown', _('Unknown')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'participant':
            return queryset.filter(timepoint_id__participant_id__participant_type=True)
        if self.value() == 'partner':
            return queryset.filter(timepoint_id__participant_id__participant_type=False)
        if self.value() == 'unknown':
            return queryset.filter(timepoint_id__participant_id__participant_type=None)
        return queryset

class IsolateResource(resources.ModelResource):
    timepoint_id = fields.Field(
        column_name='timepoint_id',
        attribute='timepoint_id',
        widget=ForeignKeyWidget(Culture, 'timepoint_id')
    )

    class Meta: 
        model = Isolate
        fields = ('id', 'original_label', 'timepoint_id', 'sample_type', 'isolate_num', 'date', 'box', 'position', 'status', 'notes')

@admin.register(Isolate)
class IsolateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    autocomplete_fields = ['timepoint_id']
    resource_class = IsolateResource
    list_display = (
        'isolate_num',
        'sample_type',
        'date',
        'box',
        'position', 
        'status',
        'notes',
    )
    list_filter = (
        'timepoint_id__visit_num',
        IsolateParticipantStatusFilter,
        IsolateTreatmentFilter,
        IsolateParticipantTypeFilter,
        'sample_type'
    )
    search_fields = [
        'isolate_num',
        'timepoint_id__timepoint_id',
        'timepoint_id__participant_id__participant_id',
    ] 

class KbStatusFilter(admin.SimpleListFilter):
    title = _('status')
    parameter_name = 'status'
 
    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
        )
 
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(isolate_num__timepoint_id__participant_id__status=True)
        if self.value() == 'inactive':
            return queryset.filter(isolate_num__timepoint_id__participant_id__status=False)
        return queryset

class KbTreatmentFilter(admin.SimpleListFilter):
    title = _('treatment')
    parameter_name = 'treatment'

    def lookups(self, request, model_admin):
        return (
            ('doxycycline', _('Doxycycline')),
            ('control', _('Control')),
            ('unknown', _('Unknown')),
        )
 
    def queryset(self, request, queryset):
        if self.value() == 'doxycycline':
            return queryset.filter(isolate_num__timepoint_id__participant_id__treatment=True)
        if self.value() == 'control':
            return queryset.filter(isolate_num__timepoint_id__participant_id__treatment=False)
        if self.value() == 'unknown':
            return queryset.filter(isolate_num__timepoint_id__participant_id__treatment=None)
        return queryset

class KbParticipantTypeFilter(admin.SimpleListFilter):
    title = _('participant_type')
    parameter_name = 'participant_type'
    
    def lookups(self, request, model_admin):
        return (
            ('participant', _('Participant')),
            ('partner', _('Partner')),
            ('unknown', _('Unknown')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'participant':
            return queryset.filter(isolate_num__timepoint_id__participant_id__participant_type=True)
        if self.value() == 'partner':
            return queryset.filter(isolate_num__timepoint_id__participant_id__participant_type=False)
        if self.value() == 'unknown':
            return queryset.filter(isolate_num__timepoint_id__participant_id__participant_type=None)
        return queryset

class KbResource(resources.ModelResource):
    isolate_num = fields.Field(
        column_name='isolate_num',
        attribute='isolate_num',
        widget=ForeignKeyWidget(Isolate, 'isolate_num')
    )

    class Meta: 
        model = Kb
        fields = ('id', 'isolate_num', 'gentamicin', 'erithromycin', 'tetracycline', 'minocycline', 'doxycycline', 'clindamycin', 'cefoxitin', 'oxacillin', 'date', 'notes')
        import_id_fields = ('id',)

class BaseSusceptibilityFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (('R', 'Resistant'), ('S', 'Susceptible'), ('I', 'Intermediate'))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
            
        field = self.parameter_name
        
        ranges = {
            'gentamicin':   {'S': {'gentamicin__gte': 15}, 'R': {'gentamicin__lte': 12}},
            'erithromycin': {'S': {'erithromycin__gte': 23}, 'R': {'erithromycin__lte': 13}},
            'tetracycline': {'S': {'tetracycline__gt': 19},  'R': {'tetracycline__lte': 14}},
            'minocycline':  {'S': {'minocycline__gte': 19},  'R': {'minocycline__lte': 14}},
            'doxycycline':  {'S': {'doxycycline__gte': 16},  'R': {'doxycycline__lte': 12}},
            'clindamycin':  {'S': {'clindamycin__lte': 14},  'R': {'clindamycin__gte': 21}},
            'cefoxitin':    {'S': {'cefoxitin__lte': 21},    'R': {'cefoxitin__gte': 22}},
            'oxacillin':    {'S': {'oxacillin__lte': 10},    'R': {'oxacillin__gte': 14}},
        }

        if self.value() == 'S':
            return queryset.filter(**ranges[field]['S'])
        elif self.value() == 'R':
            return queryset.filter(**ranges[field]['R'])
        elif self.value() == 'I':
            return queryset.exclude(**ranges[field]['S']).exclude(**ranges[field]['R'])
        
        return queryset

class GentamicinSuscFilter(BaseSusceptibilityFilter):
    title = 'Gentamicin Susc'; parameter_name = 'gentamicin'

class ErithromycinSuscFilter(BaseSusceptibilityFilter):
    title = 'Erithromycin Susc'; parameter_name = 'erithromycin'

class TetracyclineSuscFilter(BaseSusceptibilityFilter):
    title = 'Tetracycline Susc'; parameter_name = 'tetracycline'

class MinocyclineSuscFilter(BaseSusceptibilityFilter):
    title = 'Minocycline Susc'; parameter_name = 'minocycline'

class DoxycyclineSuscFilter(BaseSusceptibilityFilter):
    title = 'Doxycycline Susc'; parameter_name = 'doxycycline'

class ClindamycinSuscFilter(BaseSusceptibilityFilter):
    title = 'Clindamycin Susc'; parameter_name = 'clindamycin'

class CefoxitinSuscFilter(BaseSusceptibilityFilter):
    title = 'Cefoxitin Susc'; parameter_name = 'cefoxitin'

class OxacillinSuscFilter(BaseSusceptibilityFilter):
    title = 'Oxacillin Susc'; parameter_name = 'oxacillin'

@admin.register(Kb)
class KbAdmin(ImportExportModelAdmin):
    autocomplete_fields = ['isolate_num']
    resource_class = KbResource
    list_display = (
        'isolate_num', 
        'gentamicin_susceptibility',
        'erithromycin_susceptibility',
        'tetracycline_susceptibility',
        'minocycline_susceptibility', 
        'doxycycline_susceptibility',
        'clindamycin_susceptibility',
        'cefoxitin_susceptibility',
        'oxacillin_susceptibility',
        'notes',
    )
    list_filter = (
        'isolate_num__timepoint_id__visit_num',
        KbStatusFilter,
        KbTreatmentFilter, 
        KbParticipantTypeFilter,
        'isolate_num__sample_type',
        GentamicinSuscFilter,
        ErithromycinSuscFilter,
        TetracyclineSuscFilter,
        MinocyclineSuscFilter,
        DoxycyclineSuscFilter,
        ClindamycinSuscFilter,
        CefoxitinSuscFilter,
        OxacillinSuscFilter,
    )
    search_fields = [
        'isolate_num__isolate_num',
        'isolate_num__timepoint_id__timepoint_id'
    ]        
        
    @admin.display(description='GM')
    def gentamicin_susceptibility(self, obj):
        return obj.susceptibility(obj.gentamicin, 'gentamicin')

    @admin.display(description='EE')
    def erithromycin_susceptibility(self, obj):
        return obj.susceptibility(obj.erithromycin, 'erithromycin')

    @admin.display(description='TE')
    def tetracycline_susceptibility(self, obj):
        return obj.susceptibility(obj.tetracycline, 'tetracycline')

    @admin.display(description='MI')
    def minocycline_susceptibility(self, obj):
        return obj.susceptibility(obj.minocycline, 'minocycline')
 
    @admin.display(description='DO')
    def doxycycline_susceptibility(self, obj):
        return obj.susceptibility(obj.doxycycline, 'doxycycline')

    @admin.display(description='CC')
    def clindamycin_susceptibility(self, obj):
        return obj.susceptibility(obj.clindamycin, 'clindamycin')
     
    @admin.display(description='FOX')
    def cefoxitin_susceptibility(self, obj):
        return obj.susceptibility(obj.cefoxitin, 'cefoxitin')

    @admin.display(description='OX')
    def oxacillin_susceptibility(self, obj):
        return obj.susceptibility(obj.oxacillin, 'oxacillin')

    fieldsets = (
        (None, {
            'fields': ('isolate_num', 'date', 'notes')
        }),
        ('Antibiotic Results', {
            'fields': (
                'gentamicin',
                'erithromycin',
                'tetracycline',
                'minocycline',
                'doxycycline',
                'clindamycin',
                'cefoxitin',
                'oxacillin',
            )
        }),
    )

class ArgTagFilter(admin.SimpleListFilter):
    title = 'arg'
    parameter_name = 'arg'

    def lookups(self, request, model_admin):
        tags = Tag.objects.filter(arg_wgs__isnull=False).distinct()
        return [(tag.name, tag.name) for tag in tags]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(arg__name=self.value())
        return queryset

class SequenceStatusFilter(admin.SimpleListFilter):
    title = _('need resequencing')
    parameter_name = 'need_resequencing' 

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(need_resequencing=True)
        if self.value() == 'no':
            return queryset.filter(need_resequencing=False) 
        return queryset

class WGSResource(resources.ModelResource):
    isolate_num = fields.Field(
        column_name='isolate_num',
        attribute='isolate_num',
        widget=ForeignKeyWidget(Isolate, 'isolate_num')
    )
    
    arg = fields.Field(
        column_name='arg',
        attribute='arg',
        widget=TagWidget(model=WGS, field='name')
    )

    def before_import_row(self, row, **kwargs):
        print(f"Processing row: {row}")

    def before_save_instance(self, instance, row, **kwargs):
        print(f"Before save: {instance.__dict__}")

    def save_instance(self, instance, new, row, **kwargs):
        try:
            super().save_instance(instance, new, row, **kwargs)
            print(f"Save succeeded: {instance.pk}")
        except Exception as e:
            print(f"Save failed: {e}")
            raise
    
    def after_save_instance(self, instance, row, **kwargs):
        print(f"After save: {instance}, dry_run: {kwargs.get('dry_run')}")
        if kwargs.get('dry_run', False):
            return

        tag_str = row.get('arg', '')
        if not tag_str or str(tag_str) == 'nan':
            return

        tag_names = [t.strip() for t in str(tag_str).split(',') if t.strip()]
        instance.arg.set(tag_names)

    class Meta:
        model = WGS
        fields = ('id', 'isolate_num', 'date_sequenced', 'date_collected', 'sequence_type', 'depth', 'need_resequencing', 'organism', 'arg')
        exclude = ()
        import_id_fields = ('id',)
        skip_unchanged = False

@admin.register(WGS)
class WGSAdmin(ImportExportModelAdmin):
    autocomplete_fields = ['isolate_num']
    resource_class = WGSResource
    list_display = (
        'isolate_num',
        'sequence_type',
        'depth',
        'date_sequenced',
        'date_collected',
        'organism',
    )
    list_filter = (
        'organism',
        SequenceStatusFilter,
        ArgTagFilter,
    )
    search_fields = [
        'isolate_num__isolate_num',
        'isolate_num__timepoint_id__timepoint_id',
        'organism',
        'arg__name',
        'sequence_type',
    ]

    def get_search_results(self, request, queryset, search_term):
        if ',' in search_term:
            # Pure AND tag search — skip super() entirely
            tag_names = [t.strip() for t in search_term.split(',') if t.strip()]
            for tag in tag_names:
                queryset = queryset.filter(arg__name__iexact=tag)
            return queryset, True
        
        # Single term — use default search behavior
        return super().get_search_results(request, queryset, search_term)