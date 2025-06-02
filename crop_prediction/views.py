from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import SoilDataForm
from .models import SoilData
import joblib
import numpy as np
import os
import json

def predict_crop(request):
    if request.method == 'GET':
        form = SoilDataForm()
        return render(request, 'crop_prediction/prediction.html', {'form': form})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@require_http_methods(['POST'])
def predict(request):
    try:
        data = json.loads(request.body)
        
        # Prepare input data for prediction
        input_data = np.array([
            float(data.get('nitrogen', 0)),
            float(data.get('phosphorus', 0)),
            float(data.get('potassium', 0)),
            float(data.get('temperature', 0)),
            float(data.get('humidity', 0)),
            float(data.get('ph', 0)),
            float(data.get('rainfall', 0))
        ]).reshape(1, -1)
        
        # Load the model and scaler
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'media', 'models')
        model_path = os.path.join(base_path, 'crop_prediction_model.pkl')
        scaler_path = os.path.join(base_path, 'scaler.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            return JsonResponse({
                'error': 'Model files not found. Please ensure the model is properly trained.'
            }, status=500)
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Scale input data
        scaled_input = scaler.transform(input_data)
        
        # Make prediction
        predicted_crop = model.predict(scaled_input)[0]
        
        # Get prediction probability
        probabilities = model.predict_proba(scaled_input)[0]
        confidence = round(np.max(probabilities) * 100, 2)
        
        # Save prediction to database
        SoilData.objects.create(
            nitrogen=data.get('nitrogen'),
            phosphorus=data.get('phosphorus'),
            potassium=data.get('potassium'),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            ph=data.get('ph'),
            rainfall=data.get('rainfall'),
            predicted_crop=predicted_crop,
            confidence=confidence
        )
        
        return JsonResponse({
            'predicted_crop': predicted_crop,
            'confidence': confidence
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': f'Invalid input data: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
