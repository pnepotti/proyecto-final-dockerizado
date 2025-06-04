from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import viewsets, status
from keras.models import load_model
from keras.utils import img_to_array, load_img
from django.shortcuts import get_object_or_404
import numpy as np
import os
from django.conf import settings
from .serializers import DoctorSerializer, PatientSerializer, ImagenMRISerializer, PredictionSerializer
from .models import Doctor, Patient, ImagenMRI, Prediction

# Rutas relativas a los modelos .h5
MODEL_PATH_VALIDATION = os.path.join(
    settings.BASE_DIR, 'predicciones', 'resources', 'ia_models', 'validacionDeMRI.h5')
MODEL_PATH_DIAGNOSIS = os.path.join(
    settings.BASE_DIR, 'predicciones', 'resources', 'ia_models', 'ModeloBrainIA4Clases-12-14_23-28-06.h5')

# Carga perezosa del modelo (solo cuando sea necesario)
validation_model = None
diagnosis_model = None

# pylint: disable=no-member

# Función para cargar modelos si aún no están cargados


def load_models():
    global validation_model, diagnosis_model
    try:
        if validation_model is None:
            validation_model = load_model(MODEL_PATH_VALIDATION)
        if diagnosis_model is None:
            diagnosis_model = load_model(MODEL_PATH_DIAGNOSIS)
    except IOError as e:
        raise IOError(f"Error al cargar los modelos: {e}") from e
    except Exception as e:
        raise RuntimeError(
            f"Error inesperado al cargar los modelos: {e}") from e

# Función para preprocesar la imagen


def preprocess_image(img, target_size):
    img = img.convert('RGB')  # Convertir a RGB si no lo está
    img = img.resize(target_size)  # Redimensionar la imagen
    img = img_to_array(img)  # Convertir a un array NumPy
    # Añadir la dimensión extra para lotes (batch)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0  # Normalizar los valores de la imagen (0-1)
    return img


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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        resonancia_id = response.data['id']
        resonancia = get_object_or_404(ImagenMRI, id=resonancia_id)
        image_path = resonancia.resonancia.path

        try:
            # Cargar y preprocesar la imagen
            img = load_img(image_path)

            # Cargar modelos si no están cargados aún
            load_models()

            # Preprocesar la imagen para el modelo de validación
            preprocessed_img = preprocess_image(img, target_size=(224, 224))

            # Validar si la imagen es una MRI de cerebro
            validation_prediction = validation_model.predict(preprocessed_img)
            # Suponiendo que 0 representa MRI de cerebro
            if np.argmax(validation_prediction[0]) != 0:
                return Response({"error": "La imagen no es una MRI de cerebro válida."}, status=status.HTTP_400_BAD_REQUEST)

            # Obtener la predicción del diagnóstico
            predictions = diagnosis_model.predict(preprocessed_img)
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

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer

    def create(self, request, *args, **kwargs):
        # Deshabilitar la creación directa de predicciones
        return Response({"error": "No es posible crear predicciones directamente. Por favor, cargue una imagen válida."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
