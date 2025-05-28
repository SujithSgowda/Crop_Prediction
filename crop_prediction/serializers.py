from rest_framework import serializers
from .models import SoilData

class SoilDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilData
        fields = ['id', 'nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 
                 'humidity', 'rainfall', 'predicted_crop', 'created_at']
        read_only_fields = ['id', 'predicted_crop', 'created_at']

    def validate(self, data):
        """Validate the input data ranges"""
        if not (0 <= data['nitrogen'] <= 140):
            raise serializers.ValidationError({'nitrogen': 'Nitrogen content must be between 0 and 140 mg/kg'})
        if not (0 <= data['phosphorus'] <= 145):
            raise serializers.ValidationError({'phosphorus': 'Phosphorus content must be between 0 and 145 mg/kg'})
        if not (0 <= data['potassium'] <= 205):
            raise serializers.ValidationError({'potassium': 'Potassium content must be between 0 and 205 mg/kg'})
        if not (0 <= data['ph'] <= 14):
            raise serializers.ValidationError({'ph': 'pH must be between 0 and 14'})
        if not (0 <= data['temperature'] <= 50):
            raise serializers.ValidationError({'temperature': 'Temperature must be between 0 and 50°C'})
        if not (0 <= data['humidity'] <= 100):
            raise serializers.ValidationError({'humidity': 'Humidity must be between 0 and 100%'})
        if not (0 <= data['rainfall'] <= 300):
            raise serializers.ValidationError({'rainfall': 'Rainfall must be between 0 and 300mm'})
        return data