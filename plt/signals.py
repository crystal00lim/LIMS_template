from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Patient, Stool, StoolAliquot, Isolate, IsolateStock, WGS

@receiver(post_save, sender=Stool)
def auto_generate_stool_aliquot(sender, instance, created, **kwargs):
    if created: 
        aliquots_to_create = []
        for i in range(1, 6):
            aliquots_to_create.append(
                SampleAliquot(
                    sample=instance,
                    aliquot=i
                )
            )
        SampleAliquot.objects.bulk_create(aliquots_to_create)

@receiver(post_save, sender=Isolate)
def auto_generate_isolate_stocks(sender, instance, created, **kwargs):
    if created:
        stocks_to_create = []
        alphabet = string.ascii_lowercase 
        num_stocks = min(instance.amount, 26)
        
        target_letters = list(alphabet[:num_stocks])
        
        for letter in target_letters:
            stocks_to_create.append(
                IsolateStock(
                    isolate=instance,
                    stock_letter=letter
                )
            )
            
        IsolateStock.objects.bulk_create(stocks_to_create)

