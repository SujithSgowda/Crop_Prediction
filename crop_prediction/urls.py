from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'crop_prediction'
router = routers.DefaultRouter()

urlpatterns = [
    path('', views.predict_crop, name='crop_prediction'),
    path('predict/', views.predict, name='predict'),
    path('api/', include(router.urls)),
]