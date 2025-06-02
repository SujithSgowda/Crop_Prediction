import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
import joblib
import os

class MLService:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.media_dir = os.path.join(self.base_dir, 'media')
        self.models_dir = os.path.join(self.media_dir, 'models')
        self.datasets_dir = os.path.join(self.media_dir, 'datasets')
        
        # Create necessary directories
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.datasets_dir, exist_ok=True)
        
        # Initialize model paths
        self.crop_model_path = os.path.join(self.models_dir, 'crop_prediction_model.pkl')
        self.crop_scaler_path = os.path.join(self.models_dir, 'crop_scaler.pkl')
        self.fertilizer_model_path = os.path.join(self.models_dir, 'fertilizer_model.pkl')
        self.yield_model_path = os.path.join(self.models_dir, 'yield_model.pkl')
        
        # Train all models if they don't exist
        self.train_all_models()
    
    def train_crop_prediction_model(self):
        if os.path.exists(self.crop_model_path) and os.path.exists(self.crop_scaler_path):
            print("Loading existing crop prediction model...")
            self.crop_model = joblib.load(self.crop_model_path)
            self.crop_scaler = joblib.load(self.crop_scaler_path)
            return
        
        print("Training crop prediction model...")
        data = pd.read_csv(os.path.join(self.datasets_dir, 'crop_data.csv'))
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        X = data[features]
        y = data['label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.crop_scaler = StandardScaler()
        X_train_scaled = self.crop_scaler.fit_transform(X_train)
        
        self.crop_model = DecisionTreeClassifier(random_state=42)
        self.crop_model.fit(X_train_scaled, y_train)
        
        joblib.dump(self.crop_model, self.crop_model_path)
        joblib.dump(self.crop_scaler, self.crop_scaler_path)
        
        print(f"Crop prediction model accuracy: {self.crop_model.score(self.crop_scaler.transform(X_test), y_test):.2f}")
    
    def train_fertilizer_model(self):
        if os.path.exists(self.fertilizer_model_path):
            print("Loading existing fertilizer recommendation model...")
            self.fertilizer_model = joblib.load(self.fertilizer_model_path)
            return
            
        print("Training fertilizer recommendation model...")
        data = pd.read_csv(os.path.join(self.datasets_dir, 'fertilizer_recommendation.csv'))
        
        self.le_soil = LabelEncoder()
        self.le_crop = LabelEncoder()
        data['Soil Type'] = self.le_soil.fit_transform(data['Soil Type'])
        data['Crop Type'] = self.le_crop.fit_transform(data['Crop Type'])
        
        X = data.iloc[:, :8]
        y = data.iloc[:, -1]
        
        self.fertilizer_model = DecisionTreeClassifier(random_state=0)
        self.fertilizer_model.fit(X, y)
        
        joblib.dump(self.fertilizer_model, self.fertilizer_model_path)
    
    def train_yield_model(self):
        if os.path.exists(self.yield_model_path):
            print("Loading existing yield prediction model...")
            self.yield_model = joblib.load(self.yield_model_path)
            return
            
        print("Training yield prediction model...")
        df = pd.read_csv(os.path.join(self.datasets_dir, 'crop_production_karnataka.csv'))
        df = df.drop(['Crop_Year'], axis=1)
        
        X = df.drop(['Production'], axis=1)
        y = df['Production']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        categorical_cols = ['State_Name', 'District_Name', 'Season', 'Crop']
        self.yield_ohe = OneHotEncoder(handle_unknown='ignore')
        self.yield_ohe.fit(X_train[categorical_cols])
        
        X_train_categorical = self.yield_ohe.transform(X_train[categorical_cols])
        X_train_final = np.hstack((X_train_categorical.toarray(), X_train.drop(categorical_cols, axis=1)))
        
        self.yield_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.yield_model.fit(X_train_final, y_train)
        
        joblib.dump(self.yield_model, self.yield_model_path)
    
    def train_all_models(self):
        self.train_crop_prediction_model()
        self.train_fertilizer_model()
        self.train_yield_model()
    
    def predict_crop(self, N, P, K, temperature, humidity, ph, rainfall):
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        features_scaled = self.crop_scaler.transform(features)
        prediction = self.crop_model.predict(features_scaled)
        return prediction[0]
    
    def predict_fertilizer(self, temperature, humidity, moisture, soil_type, crop_type, N, K, P):
        soil_enc = self.le_soil.transform([soil_type])[0]
        crop_enc = self.le_crop.transform([crop_type])[0]
        features = np.array([[temperature, humidity, moisture, soil_enc, crop_enc, N, K, P]])
        prediction = self.fertilizer_model.predict(features)
        return prediction[0]
    
    def predict_rainfall(self, state, month):
        df = pd.read_csv(os.path.join(self.datasets_dir, 'rainfall_in_india_1901-2015.csv'))
        state_data = df[df['SUBDIVISION'] == state]
        avg_rainfall = state_data[month].mean()
        return avg_rainfall
    
    def predict_yield(self, state, district, season, crop, area):
        user_input = np.array([[state, district, season, crop, area]])
        user_input_categorical = self.yield_ohe.transform(user_input[:, :4])
        user_input_final = np.hstack((user_input_categorical.toarray(), user_input[:, 4:].astype(float)))
        prediction = self.yield_model.predict(user_input_final)
        return prediction[0]