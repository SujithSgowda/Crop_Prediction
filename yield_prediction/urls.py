from django.urls import path
from . import views

app_name = 'yield_prediction'

urlpatterns = [
    path('', views.yield_prediction, name='yield_prediction'),
    path('predict/', views.predict_yield, name='predict_yield'),
]