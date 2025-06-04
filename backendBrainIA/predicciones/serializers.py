from rest_framework import serializers
from .models import Prediction, ImagenMRI, Doctor, Patient


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'matricula', 'speciality']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'dni', 'date_of_birth']


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'resonancia_image', 'disease',
                  'prediction_probability', 'prediction_confidence', 'prediction_entropy']


class ImagenMRISerializer(serializers.ModelSerializer):
    # Incluir predicciones relacionadas
    predictions = PredictionSerializer(many=True, read_only=True)

    class Meta:
        model = ImagenMRI
        fields = ['id', 'resonancia', 'uploaded_at',
                  'doctor', 'patient', 'descripcion', 'diagnostico', 'predictions']
