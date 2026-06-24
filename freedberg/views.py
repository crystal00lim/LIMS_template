from django.shortcuts import render
from  django.db.models import Count, Q
from .models import Culture, Sample, Isolate
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from django.shortcuts import render
from django.apps import apps
"""
def get_progress():
    totalSamples = Sample.objects.values('sample_id').distinct()
    totalSamples = len([item['sample_id'] for item in totalSamples])
    print(totalSamples)

    culture = Culture.objects.values('sample_id_id').distinct()
    culture = len([item['sample_id_id'] for item in culture])
    print(culture)

    percent = culture / totalSamples
    percent *= 100

    context = {
        'data': [round(percent)],
        'title': ['Culture Progress']
    }

    return {'sample': context}
"""
# Create your views here.
def dashboard(request):
    app_config = apps.get_app_config('freedberg')
    # samples = get_progress()
    # samples = samples['sample']
    # print(samples)

    return render(request, 'freedberg-dashboard.html', {'app_name': app_config.verbose_name})
    # return render(request, 'freedberg-dashboard.html', {'radialdata': samples,'app_name': app_config.verbose_name})