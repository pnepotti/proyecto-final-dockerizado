from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, PatientViewSet, ImagenMRIViewSet, PredictionViewSet

router = DefaultRouter()
router.register(r'doctores', DoctorViewSet)
router.register(r'pacientes', PatientViewSet)
router.register(r'resonancias', ImagenMRIViewSet)
router.register(r'predicciones', PredictionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/predicciones/predict/',
         PredictionViewSet.as_view({'post': 'predict'}), name='predict'),
]
