from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
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

            # Load the dataset
            data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    'ML', 'fertilizer_recommendation', 'fertilizer_recommendation.csv')
            data = pd.read_csv(data_path)

            # Label encoding for categorical features
            le_soil = LabelEncoder()
            data['Soil Type'] = le_soil.fit_transform(data['Soil Type'])
            le_crop = LabelEncoder()
            data['Crop Type'] = le_crop.fit_transform(data['Crop Type'])

            # Splitting the data into input and output variables
            X = data.iloc[:, :8]
            y = data.iloc[:, -1]

            # Training the Decision Tree Classifier model
            model = DecisionTreeClassifier(random_state=0)
            model.fit(X, y)

            # Encode soil type and crop type
            soil_enc = le_soil.transform([soil_type])[0]
            crop_enc = le_crop.transform([crop_type])[0]

            # Prepare input data for prediction
            input_data = np.array([[temperature, humidity, moisture, soil_enc, crop_enc, nitrogen, phosphorus, potassium]])
            
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
