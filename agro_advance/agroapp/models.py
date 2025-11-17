from django.db import models

from django.db import models

class crop(models.Model):
    nitrogen = models.FloatField()
    Phosphorus = models.FloatField()
    potassium = models.FloatField()
    temperature = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
       return f"crop({self.id})"

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# 1️⃣ Crop Requirement Table
class CropRequirement(models.Model):
    crop_name = models.CharField(max_length=100,unique=True)
    nitrogen_req = models.FloatField(null=True)
    phosphorus_req = models.FloatField(null=True)
    potassium_req = models.FloatField(null=True)
    ph_min = models.FloatField(null=True)
    ph_max = models.FloatField(null=True)
    rainfall_min = models.FloatField(null=True)
    rainfall_max = models.FloatField(null=True)
    temperature_min = models.FloatField(null=True)
    temperature_max = models.FloatField(null=True)

    def __str__(self):
        return self.crop_name


# 2️⃣ User Soil Input Table
class SoilInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    temperature = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Soil data by {self.user.username}"

from django.db import models

class CropInfo(models.Model):
    crop = models.OneToOneField('CropRequirement', on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)   # Use URL instead of uploaded file
    good_seeds = models.CharField(max_length=200)
    fertilizer = models.CharField(max_length=200)
    methods = models.TextField()
    time_required = models.CharField(max_length=100)
    growth_timeline = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Info for {self.crop.crop_name}"

from django.db import models
from django.contrib.auth.models import User

class DiseaseDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    crop_name = models.CharField(max_length=100)
    disease_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    is_healthy = models.BooleanField(default=False)
    remedies = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.crop_name} - {self.disease_name}"

from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"



