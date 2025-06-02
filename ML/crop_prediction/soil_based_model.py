import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Load and preprocess the dataset
data = pd.read_csv('ML/crop_prediction/crop_data.csv')

# Select features for soil-based prediction
features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
X = data[features]
y = data['label']

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train_scaled, y_train)

# Save the model and scaler
joblib.dump(model, 'ML/crop_prediction/crop_prediction_model.pkl')
joblib.dump(scaler, 'ML/crop_prediction/scaler.pkl')

# Print model accuracy
print(f"Model accuracy: {model.score(X_test_scaled, y_test):.2f}")