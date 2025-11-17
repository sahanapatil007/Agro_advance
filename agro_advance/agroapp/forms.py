from django import forms
from .models import SoilInput , DiseaseDetection

class SoilInputForm(forms.ModelForm):
    class Meta:
        model = SoilInput
        fields = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall', 'temperature']


class DiseaseForm(forms.ModelForm):
    class Meta:
        model = DiseaseDetection
        fields = ['crop_name', 'image']