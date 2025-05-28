from django.urls import path
from . import views

app_name = 'rainfall_prediction'

urlpatterns = [
    path('', views.rainfall_prediction, name='rainfall_prediction'),
    path('predict/', views.predict_rainfall, name='predict_rainfall'),
]