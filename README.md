# Crop Management System

A comprehensive agricultural management system that provides crop prediction, fertilizer recommendation, rainfall prediction, and yield prediction using machine learning models.

## Features

- **Crop Prediction**: Predicts the most suitable crop based on soil parameters and environmental conditions
- **Fertilizer Recommendation**: Suggests optimal fertilizer based on soil type and crop requirements
- **Rainfall Prediction**: Forecasts rainfall patterns for different regions
- **Yield Prediction**: Estimates crop yield based on various agricultural parameters

## Tech Stack

- **Backend**: Django
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Machine Learning**: scikit-learn
- **Database**: SQLite

## Quick Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crop-management-system.git
cd crop-management-system
```

2. Set up and run the application (just two commands!):
```bash
pip install -r requirements.txt
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

## Project Structure

```
crop-management-system/
├── crop_management/        # Django project directory
│   ├── crop_prediction/    # Crop prediction app
│   ├── fertilizer_recommendation/
│   ├── rainfall_prediction/
│   ├── yield_prediction/
│   └── ml_service.py       # Consolidated ML service
├── media/                  # Media files directory
│   ├── datasets/           # ML model datasets
│   └── models/             # Trained ML models
└── requirements.txt        # Project dependencies
```

## ML Models

All machine learning models are consolidated in `ml_service.py` and include:
- Crop Prediction Model (Decision Tree Classifier)
- Fertilizer Recommendation Model (Decision Tree Classifier)
- Rainfall Prediction Model (Statistical Analysis)
- Yield Prediction Model (Random Forest Regressor)

## Dataset Sources

The system uses the following datasets:
- Crop Data: Soil parameters and suitable crops
- Fertilizer Recommendation: Soil types and optimal fertilizers
- Rainfall Data: Historical rainfall patterns (1901-2015)
- Crop Production: Historical yield data for Karnataka

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.