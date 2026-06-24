from django.db import models
from django.db.models.functions import Concat
from django.db.models import Value
from django.core.exceptions import ValidationError
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

class Participant(models.Model):
    participant_id = models.CharField(max_length=8)
    status = models.BooleanField(default=True) 
    treatment = models.BooleanField(null=True, blank=True, default=None)
    participant_type = models.BooleanField(null=True, blank=True, default=None)

    class Meta:
        pass

    def __str__(self):
        return self.participant_id

class Culture(models.Model):
    participant_id = models.ForeignKey(Participant, on_delete=models.CASCADE)
    visit_num = models.IntegerField()
    timepoint_id = models.CharField(max_length=11, editable=False, db_index=True)
    phar_sa = models.BooleanField(null=True, blank=True, default=None)
    rec_sa = models.BooleanField(null=True, blank=True, default=None)
    rec_mac = models.BooleanField(null=True, blank=True, default=None)
    rec_esbl = models.BooleanField(null=True, blank=True, default=None)
    nas_sa = models.BooleanField(null=True, blank=True, default=None)
    vag_sa = models.BooleanField(null=True, blank=True, default=None)
    vag_mac = models.BooleanField(null=True, blank=True, default=None)
    vag_esbl = models.BooleanField(null=True, blank=True, default=None)
    date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.participant_id:
            prefix = str(self.participant_id.participant_id)
            self.timepoint_id = f"{prefix}_{self.visit_num}"
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('participant_id', 'visit_num'),)

    def __str__(self):
        return self.timepoint_id 
    
class Isolate(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        KBT = 'KBT', 'KB Tested'
        FIN = 'FIN', 'Finished'
        WGS = 'WGS', 'Sequenced'
    
    SampleType = [
        ('Nas_SA', 'Nas SA'),
        ('Phar_SA', 'Phar SA'),
        ('Rec_SA', 'Rec SA'),
        ('Rec_Mac', 'Rec Mac'),
        ('Rec_ESBL', 'Rec ESBL'),
        ('Vag_SA', 'Vag SA'),
        ('Vag_Mac', 'Vag Mac'),
        ('Vag_ESBL', 'Vag ESBL'),
        ('Other', 'Other'),
    ]
    original_label = models.CharField(max_length=25, blank=True, null=True)
    timepoint_id = models.ForeignKey(Culture, on_delete=models.CASCADE) 
    sample_type = models.CharField(max_length=10, choices=SampleType)
    isolate_num = models.IntegerField(editable=False)
    date = models.DateTimeField()
    box = models.CharField(max_length=25, editable=False)
    position = models.IntegerField(editable=False)
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.NEW)
    notes = models.TextField(blank=True, null=True)

    def clean(self):
        if self.sample_type == 'Other':
            return

        isolate = self.timepoint_id
        check_field = f"{self.sample_type}".lower()
        
        filter_kwargs = {
            check_field: True,
            'id': isolate.id 
        }
        
        exist = Culture.objects.filter(**filter_kwargs).exists()
        
        if not exist:
            raise ValidationError( 
                f"Isolate Type Error: Culture does not have {self.sample_type} marked as positive."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (('box', 'position'),)

    def __str__(self):
        return str(self.isolate_num)

class Kb(models.Model):
    isolate_num = models.ForeignKey(Isolate, on_delete=models.CASCADE, related_name='kb_isolate_num')
    gentamicin = models.IntegerField()
    erithromycin = models.IntegerField()
    tetracycline = models.IntegerField()
    minocycline = models.IntegerField()
    doxycycline = models.IntegerField()
    clindamycin = models.IntegerField()
    cefoxitin = models.IntegerField()
    oxacillin = models.IntegerField()
    date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.isolate_num}"

    def susceptibility(self, result, antibiotic):
        if antibiotic == 'gentamicin':
            if result <= 12:
                return 'R'
            elif result >= 15:
                return 'S'
            else:
                return 'I'
        elif antibiotic == 'erithromycin':
            if result <= 13:
                return 'R'
            elif result >= 23:
                return 'S'
            else: 
                return 'I'
        elif antibiotic == 'tetracycline':
            if result <= 14:
                return 'R'
            elif result > 19:
                return 'S'
            else:
                return 'I'
        elif antibiotic == 'minocycline':
            if result <= 14:
                return 'R'
            elif result >= 19:
                return 'S'
            else:
                return 'I'
        elif antibiotic == 'doxycycline':
            if result <= 12:
                return 'R'
            elif result >= 16:
                return 'S'
            else:
                return 'I'
        elif antibiotic == 'clindamycin':
            if result <= 14:
                return 'R'
            elif result >= 21:
                return 'S'
            else:
                return 'I'
        elif antibiotic == 'cefoxitin':
            if result <= 21:
                return 'R'
            elif result >= 22:
                return 'S'
            else:
                return 'I'
        elif antibiotic == 'oxacillin':
            if result <= 10:
                return 'R'
            elif result >= 14:
                return 'S'
            else:
                return 'I'
        else:
            return 'Invalid susceptibility'

class TaggedArg(TaggedItemBase):
    content_object = models.ForeignKey('WGS', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Arg Tag'

class WGS(models.Model):
    isolate_num = models.ForeignKey(Isolate, on_delete=models.CASCADE, related_name='wgs_isolate_num')
    date_sequenced = models.DateTimeField()
    date_collected = models.DateTimeField()
    sequence_type = models.CharField(max_length=25)
    depth = models.FloatField()
    need_resequencing = models.BooleanField(null=True, blank=True, default=None)
    organism = models.CharField(max_length=50)
    arg = TaggableManager(through=TaggedArg, blank=True, related_name='arg_wgs')   

    class Meta:
        verbose_name = 'WGS'
        verbose_name_plural = 'WGS'

    def __str__(self):
        return f"{self.isolate_num}"