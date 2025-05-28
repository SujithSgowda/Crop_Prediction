from django.db import models

class SoilData(models.Model):
    nitrogen = models.FloatField(help_text='Nitrogen content in soil (mg/kg)')
    phosphorus = models.FloatField(help_text='Phosphorus content in soil (mg/kg)')
    potassium = models.FloatField(help_text='Potassium content in soil (mg/kg)')
    ph = models.FloatField(help_text='pH value of soil')
    temperature = models.FloatField(help_text='Temperature in celsius')
    humidity = models.FloatField(help_text='Humidity percentage')
    rainfall = models.FloatField(help_text='Rainfall in mm')
    predicted_crop = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Soil Data #{self.id} - {self.predicted_crop}'
