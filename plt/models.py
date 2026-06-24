from django.db import models
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

class Patient(models.Model):
    EnrollmentStatus = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Withdrawn', 'Withdrawn'),
        ('Excluded', 'Excluded'),
        ('Completed', 'Completed')
    ]
    patient_id = models.CharField(max_length=8)
    liver_cub = models.BooleanField(default=False)
    enrollment_status = models.CharField(max_length=10, choices=EnrollmentStatus, blank=True, null=True)
    consent_date = models.DateTimeField(blank=True, null=True)
    txp_amount = models.IntegerField()

    class Meta:
        pass

    def __str__(self):
        return self.patient_id

class Stool(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    stool_id = models.IntegerField()
    aliquots = models.IntegerField()
    date_collected = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('patient_id', 'stool_id'),)

    def __str__(self):
        return self.stool_id

class StoolAliquot(models.Model):
    stool_id = models.ForeignKey(Stool, on_delete=models.CASCADE)
    aliquot = models.CharField(max_length=10, editable=False)
    box = models.CharField(max_length = 13, editable=False)
    position = models.IntegerField(editable=False)

    class Meta:
        unique_together = (
            ('stool_id', 'aliquot'),
            ('box', 'position'),
        )

    def __str__(self):
        return f"{self.stool.stool_id}_{self.aliquot_number}"
    
class Isolate(models.Model):
    AgarType = [
        ('VRE', 'VRE'),
        ('ESBL', 'ESBL'),
        ('KPC', 'kPC')
    ]
    stool_id = models.ForeignKey(Stool, on_delete=models.CASCADE)
    isolate_id = models.IntegerField() 
    sample_type = models.CharField(max_length=10, choices=AgarType)
    amount = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(26)])
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('stool_id', 'isolate_id'),)

    def __str__(self):
        return str(self.isolate_id)

class IsolateStock(models.Model):
    isolate_id = models.ForeignKey(Isolate, on_delete=models.CASCADE)
    stock_letter = models.CharField(max_length=1, editable=False)
    box = models.CharField(max_length=13, editable=False)
    position = models.IntegerField(editable=False)

    class Meta:
        unique_together = (
            ('isolate_id', 'stock_letter'),
            ('box', 'position'),
        )

    def __str__(self):
        return f"{self.isolate.isolate_id}_{self.stock_letter}"

class TaggedArg(TaggedItemBase):
    content_object = models.ForeignKey('WGS', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Arg Tag'

class WGS(models.Model):
    isolate_id = models.ForeignKey(Isolate, on_delete=models.CASCADE, related_name='wgs_plt_isolate_id')
    sequence_type = models.CharField(max_length=25)
    depth = models.FloatField()
    organism = models.CharField(max_length=50)
    arg = TaggableManager(through=TaggedArg, blank=True, related_name='arg_plt_wgs')   

    class Meta:
        verbose_name = 'WGS'
        verbose_name_plural = 'WGS'

    def __str__(self):
        return f"{self.isolate_id}"