from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SoilData
from .serializers import SoilDataSerializer
import joblib
import numpy as np
import os
from django.conf import settings

class CropPredictionViewSet(viewsets.ModelViewSet):
    queryset = SoilData.objects.all()
    serializer_class = SoilDataSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                # Prepare input data for prediction
                input_data = np.array([
                    serializer.validated_data['nitrogen'],
                    serializer.validated_data['phosphorus'],
                    serializer.validated_data['potassium'],
                    serializer.validated_data['temperature'],
                    serializer.validated_data['humidity'],
                    serializer.validated_data['ph'],
                    serializer.validated_data['rainfall']
                ]).reshape(1, -1)

                # Load the model
                model_path = os.path.join(settings.BASE_DIR.parent, 'ML', 'crop_prediction', 'filetest2.pkl')
                model = joblib.load(model_path)

                # Make prediction
                predicted_crop = model.predict(input_data)[0]
                probabilities = model.predict_proba(input_data)[0]
                confidence = round(np.max(probabilities) * 100, 2)

                # Save the instance with prediction
                instance = serializer.save(
                    predicted_crop=predicted_crop,
                )

                response_data = serializer.data
                response_data.update({
                    'prediction': {
                        'crop': predicted_crop,
                        'confidence': confidence
                    }
                })

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(
                    {'error': f'Prediction failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def recent_predictions(self, request):
        """Get recent prediction history"""
        recent = self.get_queryset().order_by('-created_at')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)