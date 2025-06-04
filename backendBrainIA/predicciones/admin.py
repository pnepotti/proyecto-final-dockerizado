from django.contrib import admin
from .models import Prediction, ImagenMRI, Doctor, Patient

# Register your models here.
admin.site.register(Prediction)
admin.site.register(ImagenMRI)
admin.site.register(Doctor)
admin.site.register(Patient)
