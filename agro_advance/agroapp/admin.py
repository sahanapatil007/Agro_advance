from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CropRequirement, SoilInput, CropInfo,DiseaseDetection,UserProfile,ContactMessage

admin.site.register(CropRequirement)
admin.site.register(SoilInput)
admin.site.register(CropInfo)
admin.site.register(DiseaseDetection)
admin.site.register(UserProfile)
admin.site.register(ContactMessage)


from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import SoilInput, CropRequirement, CropInfo, DiseaseDetection, UserProfile

class CustomAdminSite(admin.AdminSite):
    site_header = "Agro Advance Admin"
    site_title = "Agro Advance"
    index_title = "Welcome to Agro Advance Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = {
            'total_users': UserProfile.objects.count(),
            'soil_records': SoilInput.objects.count(),
            'crop_types': CropInfo.objects.count(),
            'disease_reports': DiseaseDetection.objects.count(),
        }
        return render(request, 'admin.html', context)

admin_site = CustomAdminSite(name='custom_admin')