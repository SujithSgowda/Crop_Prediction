import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# Set paths
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_path = os.path.join(base_dir, 'media', 'datasets', 'crop_data.csv')
model_output_path = os.path.join(base_dir, 'media', 'models', 'crop_prediction_model.pkl')
scaler_output_path = os.path.join(base_dir, 'media', 'models', 'scaler.pkl')

# Load and preprocess the dataset
print(f"Loading data from {data_path}")
data = pd.read_csv(data_path)

# Display dataset information
print(f"Dataset shape: {data.shape}")
print(f"Unique crops in dataset: {data['label'].unique()}")
print(f"Crop distribution:\n{data['label'].value_counts()}")

# Select features for soil-based prediction
features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
X = data[features]
y = data['label']

# Check if we have enough samples for stratified split
class_counts = y.value_counts()
min_class_count = class_counts.min()
print(f"Minimum class count: {min_class_count}")

# Split the dataset - use stratify only if we have enough samples
if min_class_count >= 2:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print("Using stratified split")
else:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Using regular split (not stratified)")
    
# Check class distribution in train and test sets
print(f"Training set class distribution:\n{y_train.value_counts()}")
print(f"Test set class distribution:\n{y_test.value_counts()}")

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train multiple models and compare
models = {
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
}

for name, model in models.items():
    # Skip cross-validation due to small sample sizes for some classes
    print(f"Training {name}...")
    
    # Train on full training set
    model.fit(X_train_scaled, y_train)
    
    # Evaluate on test set
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{name} Test Accuracy: {accuracy:.4f}")
    
    # Print detailed classification report
    print(f"{name} Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

# Select the best model (Random Forest typically performs better)
best_model = models['Random Forest']

# Test with a sample input
sample_input = np.array([[90, 40, 40, 25, 80, 6.5, 200]])
sample_input_scaled = scaler.transform(sample_input)
prediction = best_model.predict(sample_input_scaled)
print(f"Sample prediction test: {prediction[0]}")

# Feature importance
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feature_names = X.columns
    indices = np.argsort(importances)[::-1]
    
    print("\nFeature ranking:")
    for i in range(X.shape[1]):
        print(f"{i+1}. {feature_names[indices[i]]} ({importances[indices[i]]:.4f})")  

# Save the model and scaler
print("\nSaving model and scaler...")
media_models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'models')

# Create directory if it doesn't exist
os.makedirs(media_models_dir, exist_ok=True)

# Save to media/models directory
model_path = os.path.join(media_models_dir, 'improved_crop_model.joblib')
scaler_path = os.path.join(media_models_dir, 'improved_crop_scaler.joblib')

joblib.dump(best_model, model_path)
joblib.dump(scaler, scaler_path)
print(f"Model saved to: {model_path}")
print(f"Scaler saved to: {scaler_path}")