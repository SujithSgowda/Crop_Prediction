from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SoilData
from .serializers import SoilDataSerializer
from .forms import SoilDataForm
import joblib
import numpy as np
import os
import json
import logging
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

def predict_crop(request):
    """Main crop prediction page"""
    if request.method == 'GET':
        form = SoilDataForm()
        return render(request, 'crop_prediction/prediction.html', {'form': form})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def load_model_and_scaler():
    """Helper function to load model and scaler"""
    try:
        # Try multiple possible paths for model files
        possible_paths = [
            # Path from the updated version
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'models'),
            # Path from the original version
            os.path.join(settings.BASE_DIR.parent, 'ML', 'crop_prediction'),
            # Alternative path in media directory
            os.path.join(settings.MEDIA_ROOT, 'models'),
        ]
        
        model_files = ['crop_prediction_model.pkl', 'filetest2.pkl']
        scaler_files = ['scaler.pkl']
        
        model = None
        scaler = None
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                # Try to load model
                for model_file in model_files:
                    model_path = os.path.join(base_path, model_file)
                    if os.path.exists(model_path):
                        model = joblib.load(model_path)
                        logger.info(f"Model loaded from: {model_path}")
                        break
                
                # Try to load scaler
                for scaler_file in scaler_files:
                    scaler_path = os.path.join(base_path, scaler_file)
                    if os.path.exists(scaler_path):
                        scaler = joblib.load(scaler_path)
                        logger.info(f"Scaler loaded from: {scaler_path}")
                        break
                
                if model:
                    break
        
        if not model:
            raise FileNotFoundError("Model file not found in any expected location")
        
        return model, scaler
        
    except Exception as e:
        logger.error(f"Error loading model/scaler: {str(e)}")
        raise

def validate_input_data(data):
    """Validate and convert input data"""
    required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
    
    # Check if all required fields are present
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Convert to float and validate ranges
    validated_data = {}
    for field in required_fields:
        try:
            value = float(data[field])
            
            # Basic range validation
            if field in ['nitrogen', 'phosphorus', 'potassium'] and (value < 0 or value > 200):
                raise ValueError(f"{field} value should be between 0 and 200")
            elif field == 'temperature' and (value < -50 or value > 60):
                raise ValueError("Temperature should be between -50°C and 60°C")
            elif field == 'humidity' and (value < 0 or value > 100):
                raise ValueError("Humidity should be between 0% and 100%")
            elif field == 'ph' and (value < 0 or value > 14):
                raise ValueError("pH should be between 0 and 14")
            elif field == 'rainfall' and (value < 0 or value > 500):
                raise ValueError("Rainfall should be between 0 and 500mm")
            
            validated_data[field] = value
            
        except (ValueError, TypeError) as e:
            if "could not convert" in str(e).lower():
                raise ValueError(f"Invalid {field} value: must be a number")
            raise e
    
    return validated_data

@csrf_exempt
@require_http_methods(['POST'])
def predict(request):
    """Handle prediction requests"""
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
        # Validate input data
        validated_data = validate_input_data(data)
        
        # Prepare input data for prediction
        input_data = np.array([
            validated_data['nitrogen'],
            validated_data['phosphorus'],
            validated_data['potassium'],
            validated_data['temperature'],
            validated_data['humidity'],
            validated_data['ph'],
            validated_data['rainfall']
        ]).reshape(1, -1)
        
        # Load model and scaler
        model, scaler = load_model_and_scaler()
        
        # Scale input data if scaler is available
        if scaler is not None:
            scaled_input = scaler.transform(input_data)
        else:
            scaled_input = input_data
            logger.warning("No scaler found, using raw input data")
        
        # Make prediction
        predicted_crop = model.predict(scaled_input)[0]
        
        # Get prediction probability/confidence
        try:
            probabilities = model.predict_proba(scaled_input)[0]
            confidence = round(np.max(probabilities) * 100, 2)
        except AttributeError:
            # Some models might not have predict_proba method
            confidence = None
            logger.warning("Model doesn't support probability prediction")
        
        # Save prediction to database
        try:
            soil_data = SoilData.objects.create(
                nitrogen=validated_data['nitrogen'],
                phosphorus=validated_data['phosphorus'],
                potassium=validated_data['potassium'],
                temperature=validated_data['temperature'],
                humidity=validated_data['humidity'],
                ph=validated_data['ph'],
                rainfall=validated_data['rainfall'],
                predicted_crop=predicted_crop,
                confidence=confidence
            )
            logger.info(f"Prediction saved to database with ID: {soil_data.id}")
        except Exception as db_error:
            logger.error(f"Database save error: {db_error}")
            # Continue even if database save fails
        
        # Prepare response
        response_data = {
            'success': True,
            'predicted_crop': predicted_crop,
            'input_data': validated_data
        }
        
        if confidence is not None:
            response_data['confidence'] = confidence
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': f'Invalid input data: {str(e)}'}, status=400)
    except FileNotFoundError as e:
        return JsonResponse({'error': f'Model files not found: {str(e)}'}, status=500)
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return JsonResponse({'error': f'An error occurred during prediction: {str(e)}'}, status=500)