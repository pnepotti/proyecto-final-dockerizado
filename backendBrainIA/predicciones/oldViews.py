from .serializers import DoctorSerializer, PatientSerializer, ImagenMRISerializer, PredictionSerializer
from .models import Doctor, Patient, ImagenMRI, Prediction
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
import tensorflow as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Cargar modelos
MODEL_PATH_DIAGNOSIS = "./resources/ModeloBrainIA4Clases-12-14_23-28-06.h5"
MODEL_PATH_VALIDATION = "./resources/validacionDeMRI.h5"
diagnosis_model = tf.keras.models.load_model(MODEL_PATH_DIAGNOSIS)
validation_model = tf.keras.models.load_model(MODEL_PATH_VALIDATION)

# Clases del modelo de diagnóstico
disease_labels = ['glioma', 'meningioma', 'notumor', 'pituitary']


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class ImagenMRIViewSet(viewsets.ModelViewSet):
    queryset = ImagenMRI.objects.all()
    serializer_class = ImagenMRISerializer
    parser_classes = (MultiPartParser, FormParser)


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer

    @action(detail=False, methods=['post'])
    def predict(self, request):
        """
        Recibe una imagen de resonancia, valida si es una MRI de cerebro y devuelve un diagnóstico con su probabilidad.
        """
        resonancia_id = request.data.get('resonancia_id')
        resonancia = get_object_or_404(ImagenMRI, id=resonancia_id)
        image_path = resonancia.resonancia.path

        # Cargar y preprocesar la imagen
        img = tf.keras.preprocessing.image.load_img(
            image_path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalización

        # Validar si la imagen es una MRI de cerebro
        # validation_prediction = validation_model.predict(img_array)
        # Suponiendo que 1 representa MRI de cerebro

        if np.argmax(validation_prediction[0]) != 0:
            return Response({"error": "La imagen no es una MRI de cerebro válida."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la predicción del diagnóstico
        predictions = diagnosis_model.predict(img_array)
        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        predicted_disease = disease_labels[predicted_class]

        # Calcular entropía como medida de incertidumbre
        entropy = -np.sum(predictions[0] * np.log(predictions[0] + 1e-10))

        # Guardar predicción en la base de datos
        prediction = Prediction.objects.create(
            resonancia_image=resonancia,
            disease=predicted_disease,
            prediction_probability=confidence,
            prediction_confidence=confidence,
            prediction_entropy=entropy
        )

        return Response(PredictionSerializer(prediction).data, status=status.HTTP_201_CREATED)
