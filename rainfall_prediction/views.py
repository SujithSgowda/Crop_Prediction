from django.shortcuts import render
import pandas as pd
import os

# Load the dataset
data_path = os.path.join(os.path.dirname(__file__), '../../ML/rainfall_prediction/rainfall_in_india_1901-2015.csv')
df = pd.read_csv(data_path)

def predict_rainfall(state, month):
    # Filter the dataframe to only include rows with the given state
    state_data = df[df['SUBDIVISION'] == state]
    # Calculate the average rainfall for the given month across all years
    avg_rainfall = state_data[month].mean()
    return avg_rainfall

def rainfall_prediction(request):
    prediction_result = None
    error_message = None

    if request.method == 'POST':
        try:
            # Get input values from the form
            state = request.POST.get('state')
            month = request.POST.get('month')

            # Validate inputs
            if not state or not month:
                raise ValueError("Please provide both state and month")

            # Make prediction
            prediction_result = predict_rainfall(state, month)
            if prediction_result is None:
                error_message = "No data available for the selected state and month"
        except ValueError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "An error occurred while processing your request"

    return render(request, 'rainfall_prediction/rainfall_form.html', {
        'prediction_result': prediction_result,
        'error_message': error_message
    })
