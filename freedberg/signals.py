from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Sample, Culture, Isolate

@receiver(pre_save, sender=Isolate)
def set_isolate_position(sender, instance, **kwargs):
    if instance.position:
        return

    last_record = Isolate.objects.order_by('-id').first() 

    if not last_record:
        instance.position = 1
        instance.box = 'FSB_ISO_B1'
    else:
        last_position = last_record.position
        try:
            last_box_num = int(last_record.box.replace('FSB_ISO_B', ''))
        except ValueError:
            last_box_num = 1

        if last_position < 81:
            instance.position = last_position + 1
            instance.box = f"FSB_ISO_B{last_box_num:03}"
        else:
            instance.position = 1
            instance.box = f"FSB_ISO_B{last_box_num + 1:03}"

@receiver(pre_save, sender=Isolate)
def set_isolate_id(sender, instance, **kwargs):
    if not instance.isolate_id:
        last_record = Isolate.objects.order_by('-isolate_id').first()
        # print('this is last_record by first', last_record)

        if not last_record:
            new_record = 1
        else:
            try:
                last_id = int(last_record.isolate_id.replace('FSB', ''))
                new_record = last_id + 1
            except (ValueError, TypeError):
                new_record = 1

        instance.isolate_id = f"FSB{new_record:04}"

