from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
import os

def yield_prediction(request):
    return render(request, 'yield_prediction/yield_form.html')

def predict_yield(request):
    if request.method == 'POST':
        try:
            # Get input values from the form
            state = request.POST.get('state')
            district = request.POST.get('district')
            crop = request.POST.get('crop')
            season = request.POST.get('season')
            area = float(request.POST.get('area'))
            rainfall = float(request.POST.get('rainfall'))
            temperature = float(request.POST.get('temperature'))
            
            # Load historical crop production data
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   'media', 'datasets', 'crop_production_karnataka.csv')
            crop_data = pd.read_csv(data_path)
            
            # Filter data for the specific state, district and crop
            filtered_data = crop_data[
                (crop_data['State_Name'] == state) &
                (crop_data['District_Name'] == district) &
                (crop_data['Crop'] == crop)
            ]
            
            if len(filtered_data) == 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No historical data available for the selected combination'
                })
            
            # Calculate average yield for similar conditions
            avg_yield = filtered_data['Yield'].mean()
            
            # Apply environmental factors adjustment
            rainfall_factor = 1 + (rainfall - filtered_data['Rainfall'].mean()) / filtered_data['Rainfall'].std() * 0.1
            temp_factor = 1 + (temperature - filtered_data['Temperature'].mean()) / filtered_data['Temperature'].std() * 0.1
            
            # Predict yield
            predicted_yield = avg_yield * rainfall_factor * temp_factor
            
            # Calculate production
            predicted_production = predicted_yield * area
            
            return JsonResponse({
                'status': 'success',
                'predicted_yield': round(predicted_yield, 2),
                'predicted_production': round(predicted_production, 2),
                'historical_avg_yield': round(avg_yield, 2)
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
