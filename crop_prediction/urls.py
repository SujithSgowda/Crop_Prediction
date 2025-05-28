from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

app_name = 'crop_prediction'

# Create a router for API views
router = DefaultRouter()
router.register(r'api', api.CropPredictionViewSet, basename='crop_prediction_api')

urlpatterns = [
    path('', views.predict_crop, name='crop_prediction'),
    path('', include(router.urls)),  # Include API URLs
]