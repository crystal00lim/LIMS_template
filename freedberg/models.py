from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Sample(models.Model):
    class Type(models.TextChoices):
        PT = 'P', 'Patient'
        ENV = 'E', 'Environmental'
        DR = 'D', 'Drain'

    sample_id = models.CharField(max_length=6, editable=False)
    sample_num = models.IntegerField()
    sample_type = models.CharField(max_length=3, choices=Type.choices, default=Type.PT)
    sixteen_s = models.BooleanField(default=True)
    extraction = models.BooleanField(null=True, blank=True, default=None)
    sixteen_s_finished = models.BooleanField(default=False)
    date = models.DateTimeField()
    box = models.IntegerField()
    position = models.CharField(max_length=2)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.sample_id:
            if self.sample_type in [self.Type.ENV, self.Type.DR]:
                suffix = self.sample_type
            else:
                suffix = ""

            self.sample_id = f"SB{self.sample_num:03}{suffix}"

        super().save(*args, **kwargs)
    
    class Meta:
        db_table = '"freedberg"."sample"'

    def __str__(self):
        return self.sample_id

class Culture(models.Model):
    sample_id = models.ForeignKey(Sample, on_delete=models.CASCADE)
    vre_blue = models.BooleanField(default=False)
    vre_pink = models.BooleanField(default=False)
    kpc_blue = models.BooleanField(default=False)
    kpc_pink = models.BooleanField(default=False)
    kpc_white = models.BooleanField(default=False)
    kpc_yellow = models.BooleanField(default=False)
    date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = '"freedberg"."culture"'
        unique_together = (('sample_id',),)

    def __str__(self):
        return str(self.sample_id)

class Isolate(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        EXT = 'EXT', 'Colony Extracted'
        LIB = 'LIB', 'Library Prepped'
        WGS = 'WGS', 'Sequenced'
    
    IsolateType = [
        ('vre_blue', 'VRE Blue'),
        ('vre_pink', 'VRE Pink'),
        ('kpc_blue', 'KPC Blue'),
        ('kpc_pink', 'KPC Pink'),
        ('kpc_white', 'KPC White'),
        ('kpc_yellow', 'KPC Yellow')
    ]

    isolate_id = models.CharField(max_length=7, editable=False)
    sample_id = models.ForeignKey(Culture, on_delete=models.CASCADE, related_name='isolate_by_id')
    isolate_type = models.CharField(max_length=10, choices=IsolateType)
    box = models.CharField(max_length=25, editable=False)
    position = models.IntegerField(editable=False)
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.NEW)
    date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    def clean(self):
        sample = self.sample_id.sample_id
        # print("This is sample id", sample)

        check_field = f"{self.isolate_type}"

        filter_kwargs = {
            check_field: True
        }

        exist = Culture.objects.filter(**filter_kwargs, sample_id=sample)
        # print('this is the variable check_field: ', check_field)
        # print('this is the variable exist: ', exist)

        exist = [item.id for item in exist]
        # print('this is the length of exist: ', exist)

        if len(exist) is 0:
            raise ValidationError(
                f"Isolate Type Error: Culture does not have this isolate type marked as positive for this sample ID."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = '"freedberg"."isolate"'
        unique_together = (('box', 'position'),)

    def __str__(self):
        return str(self.isolate_id)
