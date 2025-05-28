from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
import joblib
import os

def fertilizer_recommendation(request):
    return render(request, 'fertilizer_recommendation/fertilizer_form.html')

def predict_fertilizer(request):
    if request.method == 'POST':
        try:
            # Get input values from the form
            temperature = float(request.POST.get('temperature'))
            humidity = float(request.POST.get('humidity'))
            moisture = float(request.POST.get('moisture'))
            soil_type = request.POST.get('soil_type')
            crop_type = request.POST.get('crop_type')
            nitrogen = float(request.POST.get('nitrogen'))
            phosphorus = float(request.POST.get('phosphorus'))
            potassium = float(request.POST.get('potassium'))

            # Load the ML model
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    'ML', 'fertilizer_recommendation', 'fertilizer_model.pkl')
            model = joblib.load(model_path)

            # Prepare input data for prediction
            input_data = np.array([[temperature, humidity, moisture, nitrogen, phosphorus, potassium]])
            
            # Make prediction
            prediction = model.predict(input_data)[0]

            # Return the prediction result
            return JsonResponse({
                'status': 'success',
                'prediction': prediction,
                'recommendation': get_fertilizer_recommendation(prediction, soil_type, crop_type)
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_fertilizer_recommendation(prediction, soil_type, crop_type):
    # Add custom fertilizer recommendations based on the prediction, soil type, and crop type
    recommendations = {
        'N': 'Nitrogen deficiency. Add nitrogen-rich fertilizers like Urea.',
        'P': 'Phosphorus deficiency. Add phosphorus-rich fertilizers like DAP.',
        'K': 'Potassium deficiency. Add potassium-rich fertilizers like MOP.',
        'NP': 'Nitrogen and Phosphorus deficiency. Add NPK fertilizers with higher N and P content.',
        'NK': 'Nitrogen and Potassium deficiency. Add NPK fertilizers with higher N and K content.',
        'PK': 'Phosphorus and Potassium deficiency. Add NPK fertilizers with higher P and K content.',
        'NPK': 'Overall nutrient deficiency. Add balanced NPK fertilizers.'
    }
    return recommendations.get(prediction, 'No specific recommendation available.')
