from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
import os

# Load the dataset
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/datasets/rainfall_in_india_1901-2015.csv')
df = pd.read_csv(data_path)

def get_rainfall_prediction(state, year):
    # Filter the dataframe to only include rows with the given state
    state_data = df[df['SUBDIVISION'] == state]
    
    # Calculate the average annual rainfall for the state
    annual_cols = [col for col in df.columns if col not in ['YEAR', 'SUBDIVISION', 'ANNUAL']]
    historical_avg = state_data[annual_cols].mean().mean()
    
    # Simulate a prediction based on historical data with some variation
    # In a real application, this would use a trained ML model
    base_prediction = historical_avg * (1 + (int(year) - 2015) * 0.01)  # Simple trend
    random_factor = np.random.normal(1, 0.05)  # Add some randomness
    prediction = base_prediction * random_factor
    
    # Classify the rainfall
    if prediction < 500:
        classification = "Low Rainfall"
    elif prediction < 1000:
        classification = "Moderate Rainfall"
    elif prediction < 1500:
        classification = "High Rainfall"
    else:
        classification = "Very High Rainfall"
    
    return {
        'prediction': round(prediction, 2),
        'classification': classification,
        'historical_avg': round(historical_avg, 2)
    }

def rainfall_prediction(request):
    return render(request, 'rainfall_prediction/rainfall_form.html')

def predict_rainfall(request):
    if request.method == 'POST':
        try:
            # Get input values from the form
            state = request.POST.get('state')
            year = request.POST.get('year')

            # Validate inputs
            if not state or not year:
                return JsonResponse({'error': 'Please provide both state and year'}, status=400)

            # Make prediction
            result = get_rainfall_prediction(state, year)
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
