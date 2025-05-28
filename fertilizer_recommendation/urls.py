from django.urls import path
from . import views

app_name = 'fertilizer_recommendation'

urlpatterns = [
    path('', views.fertilizer_recommendation, name='fertilizer_recommendation'),
    path('predict/', views.predict_fertilizer, name='predict_fertilizer'),
]