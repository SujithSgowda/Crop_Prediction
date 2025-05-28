from django.shortcuts import render
from django.contrib import messages
from .forms import SoilDataForm
from .models import SoilData
import joblib
import numpy as np
import os

def predict_crop(request):
    prediction_result = None
    error_message = None
    
    if request.method == 'POST':
        form = SoilDataForm(request.POST)
        if form.is_valid():
            try:
                # Save the form data
                soil_data = form.save(commit=False)
                
                # Prepare input data for prediction
                input_data = np.array([
                    form.cleaned_data['nitrogen'],
                    form.cleaned_data['phosphorus'],
                    form.cleaned_data['potassium'],
                    form.cleaned_data['temperature'],
                    form.cleaned_data['humidity'],
                    form.cleaned_data['ph'],
                    form.cleaned_data['rainfall']
                ]).reshape(1, -1)
                
                # Load the model
                try:
                    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                            'ML', 'crop_prediction')
                    model_path = os.path.join(base_path, 'crop_prediction_model.pkl')
                    scaler_path = os.path.join(base_path, 'scaler.pkl')
                    
                    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                        raise FileNotFoundError(f"Model or scaler file not found. Please train the model first.")
                    
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
                except FileNotFoundError as e:
                    raise Exception(f"ML model not found. Please ensure the model is properly trained and saved: {str(e)}")
                except Exception as e:
                    raise Exception(f"Error during model prediction: {str(e)}")
                
                # Validate prediction results
                if not predicted_crop or not isinstance(predicted_crop, str):
                    raise Exception("Invalid prediction result from model")
                
                # Save prediction results
                soil_data.predicted_crop = predicted_crop
                soil_data.confidence = confidence
                soil_data.save()
                
                prediction_result = {
                    'crop': predicted_crop,
                    'confidence': confidence
                }
                
                messages.success(request, 'Prediction completed successfully!')
                
            except Exception as e:
                error_message = f"An error occurred during prediction: {str(e)}"
                messages.error(request, error_message)
    else:
        form = SoilDataForm()
    
    return render(request, 'crop_prediction/prediction.html', {
        'form': form,
        'prediction': prediction_result,
        'error': error_message
    })
