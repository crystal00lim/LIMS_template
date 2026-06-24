from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Participant, Culture, Isolate, Kb, WGS

@receiver(pre_save, sender=Culture)
def set_timepoint_id(sender, instance, **kwargs):
    if not instance.timepoint_id:
        participant_id = instance.participant_id
        visit_num = instance.visit_num
        instance.timepoint_id = f"{participant_id}_{visit_num}"

@receiver(pre_save, sender=Isolate)
def set_isolate_position(sender, instance, **kwargs):
    if instance.position:
        return

    last_record = Isolate.objects.order_by('-id').first() 

    if not last_record:
        instance.position = 1
        instance.box = 'Zuc_Doxy_Iso_B001'
    else:
        last_position = last_record.position
        try:
            cleaned_box = last_record.box.replace('Zuc_Doxy_Iso_B', '')
            last_box_num = int(cleaned_box)
        except ValueError:
            last_box_num = 1

        if last_position < 81:
            instance.position = last_position + 1
            instance.box = f"Zuc_Doxy_Iso_B{last_box_num:03}"
        else:
            instance.position = 1
            instance.box = f"Zuc_Doxy_Iso_B{last_box_num + 1:03}"

@receiver(post_save, sender=Kb)
def update_status_to_tested(sender, instance, created, **kwargs):
    if created:
        instance.isolate_num.status = Isolate.Status.KBT
        instance.isolate_num.save()

@receiver(post_save, sender=WGS)
def update_status_to_wgs(sender, instance, created, **kwargs):
    if created:
        if instance.depth >= 30:
            instance.isolate_num.status = Isolate.Status.FIN
        else:
            instance.isolate_num.status = Isolate.Status.WGS
        instance.isolate_num.save()

@receiver(pre_save, sender=Isolate)
def set_isolate_num(sender, instance, **kwargs):
    if not instance.isolate_num:
        last_record = Isolate.objects.order_by('-isolate_num').first()
        if not last_record: 
            new_record = 1
        else:
            try: 
                last_num = last_record.isolate_num
                new_record = last_num + 1
            except ValueError:
                new_record = 1
        instance.isolate_num = new_record
