from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, render
from .models import crop

def about(request):
    return render(request,"about.html")


def home(request):
    return render(request,'home.html')


def crop(request):
    return render(request,"crop.html")

from django.shortcuts import render, get_object_or_404
from .models import CropRequirement, SoilInput, CropInfo
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
import json, math

@login_required
def recommend_crop(request):
    if request.method == 'POST':
        nitrogen = float(request.POST.get('nitrogen'))
        phosphorus = float(request.POST.get('phosphorus'))
        potassium = float(request.POST.get('potassium'))
        ph = float(request.POST.get('ph'))
        rainfall = float(request.POST.get('rainfall'))
        temperature = float(request.POST.get('temperature'))

        # ✅ Save user input
        soil_input = SoilInput.objects.create(
            user=request.user,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ph=ph,
            rainfall=rainfall,
            temperature=temperature
        )

        # ✅ Find best crop based on minimum difference
        crops = CropRequirement.objects.all()
        best_crop = None
        min_diff = float('inf')
        top_3 = []

        for crop in crops:
            # Handle missing values safely
            def safe_val(value): return value if value is not None else 0

            diff = (
                abs(safe_val(crop.nitrogen_req) - nitrogen) +
                abs(safe_val(crop.phosphorus_req) - phosphorus) +
                abs(safe_val(crop.potassium_req) - potassium) +
                abs(safe_val(crop.ph_max) - ph) +
                abs(safe_val(crop.rainfall_max) - rainfall) +
                abs(safe_val(crop.temperature_max) - temperature)
            )

            if diff < min_diff:
                min_diff = diff
                best_crop = crop

            # Maintain top 3 crops
            top_3.append((crop.crop_name, diff))

        # Sort and take top 3
        top_3 = sorted(top_3, key=lambda x: x[1])[:3]

        # ✅ Get crop info correctly
        crop_info = CropInfo.objects.filter(crop__crop_name__iexact=best_crop.crop_name).first()

        if not crop_info:
            print(f"⚠️ No CropInfo found for {best_crop.crop_name}")

        # ✅ Generate growth timeline
        total_days = 120
        if crop_info and crop_info.time_required:
            try:
                total_days = int(''.join(filter(str.isdigit, crop_info.time_required)))
            except:
                pass

        today = date.today()
        stages = [
            {"name": "Seedling", "icon": "🌱", "percent": 0.15},
            {"name": "Vegetative", "icon": "🌿", "percent": 0.35},
            {"name": "Flowering", "icon": "🌸", "percent": 0.25},
            {"name": "Maturity", "icon": "🌾", "percent": 0.15},
            {"name": "Harvesting", "icon": "🧺", "percent": 0.10},
        ]

        timeline = []
        current_date = today
        for stage in stages:
            duration = math.ceil(total_days * stage["percent"])
            end_date = current_date + timedelta(days=duration)
            timeline.append({
                "name": stage["name"],
                "icon": stage["icon"],
                "start": current_date.strftime("%b %d"),
                "end": end_date.strftime("%b %d"),
                "info": f"{stage['name']} stage lasts for {duration} days."
            })
            current_date = end_date

        # ✅ Prepare chart data
        top_crops_json = json.dumps({
            "labels": [name for name, _ in top_3],
            "scores": [round(100 - (diff / (min_diff + 1)) * 100, 2) for _, diff in top_3]
        })

        # ✅ Final context
        context = {
            "crop": best_crop,
            "crop_info": crop_info,
            "soil_input": soil_input,
            "top_crops_json": top_crops_json,
            "timeline": timeline,
        }

        return render(request, "suggest.html", context)

    return render(request, "crop.html")


from django.shortcuts import render
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import json
import os
from .models import DiseaseDetection
from disease_remedies import REMEDIES

# Load model and class labels
model = tf.keras.models.load_model("disease_model.h5")
class_labels = json.load(open("class_labels.json"))

def detect_disease(request):
    context = {}

    if request.method == "POST" and request.FILES.get("leaf_image"):
        img_file = request.FILES["leaf_image"]

        # Save uploaded image
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        img_path = os.path.join(upload_dir, img_file.name)
        with open(img_path, "wb+") as f:
            for chunk in img_file.chunks():
                f.write(chunk)

        # Preprocess the image
        img = image.load_img(img_path, target_size=(128, 128))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Make prediction
        pred = model.predict(img_array)
        pred_index = np.argmax(pred)
        pred_class = class_labels[pred_index]
        confidence = np.max(pred)

        # Split crop and disease name if label structured like "Tomato___Leaf_Mold"
        if "___" in pred_class:
            crop_name, disease_name = pred_class.split("___")
        else:
            crop_name = "Unknown Crop"
            disease_name = pred_class

        # Fetch description & remedy
        if pred_class in REMEDIES:
            desc = REMEDIES[pred_class]["description"]
            remedy = REMEDIES[pred_class]["remedy"]
        else:
            desc = "No description available."
            remedy = "No remedy found."

        # Determine if crop is healthy
        is_healthy = "healthy" in disease_name.lower()

        # ✅ Save record to the database
        DiseaseDetection.objects.create(
            user=request.user if request.user.is_authenticated else None,
            crop_name=crop_name,
            disease_name=disease_name,
            description=desc,
            image_url="/" + img_path,
            is_healthy=is_healthy,
            remedies=remedy,
        )

        # Pass result to the template
        context = {
            "predicted_class": pred_class,
            "crop":crop_name,
            "confidence": f"{confidence * 100:.2f}%",
            "description": desc,
            "remedy": remedy,
            "image_url": "/" + img_path,
        }

    return render(request, "disease.html", context)

from django.contrib.auth.decorators import login_required
from .models import DiseaseDetection

@login_required
def detect_history(request):
    # Fetch all disease detections for the logged-in user
    history = DiseaseDetection.objects.filter(user=request.user).order_by('-id')

    return render(request, 'disease_history.html', {'history': history})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import CropRequirement, CropInfo, SoilInput, DiseaseDetection, UserProfile, ContactMessage

@login_required
def custom_admin(request):
    # ======= Dashboard counts =======
    total_users = User.objects.count()
    soil_records = SoilInput.objects.count()
    crop_types = CropRequirement.objects.count()
    disease_reports = DiseaseDetection.objects.count()

    # ======= Get all data =======
    crops = CropRequirement.objects.all()
    crop_infos = CropInfo.objects.select_related("crop").all()
    soil_inputs = SoilInput.objects.select_related("user").all()
    diseases = DiseaseDetection.objects.select_related("user").all()
    users = UserProfile.objects.all()
    contact_messages = ContactMessage.objects.all()

    # ======= Add Crop Requirement =======
    if request.method == "POST" and "add_crop" in request.POST:
        CropRequirement.objects.create(
            crop_name=request.POST.get("crop_name"),
            nitrogen_req=request.POST.get("nitrogen_req") or 0,
            phosphorus_req=request.POST.get("phosphorus_req") or 0,
            potassium_req=request.POST.get("potassium_req") or 0,
            ph_min=request.POST.get("ph_min") or 0,
            ph_max=request.POST.get("ph_max") or 0,
            rainfall_min=request.POST.get("rainfall_min") or 0,
            rainfall_max=request.POST.get("rainfall_max") or 0,
            temperature_min=request.POST.get("temperature_min") or 0,
            temperature_max=request.POST.get("temperature_max") or 0,
        )
        return redirect("custom_admin")

    # ======= Add Crop Info =======
    if request.method == "POST" and "add_cropinfo" in request.POST:
        crop_id = request.POST.get("crop_id")
        CropInfo.objects.create(
            crop_id=crop_id,
            good_seeds=request.POST.get("good_seeds"),
            fertilizer=request.POST.get("fertilizer"),
            season=request.POST.get("season"),
            yield_range=request.POST.get("yield_range"),
        )
        return redirect("custom_admin")

    # ======= Delete Crop Requirement =======
    if request.method == "POST" and "delete_crop" in request.POST:
        crop = get_object_or_404(CropRequirement, id=request.POST.get("crop_id"))
        crop.delete()
        return redirect("custom_admin")

    # ======= Delete Crop Info =======
    if request.method == "POST" and "delete_cropinfo" in request.POST:
        crop_info = get_object_or_404(CropInfo, id=request.POST.get("cropinfo_id"))
        crop_info.delete()
        return redirect("custom_admin")

    # ======= Delete Soil Record =======
    if request.method == "POST" and "delete_soil" in request.POST:
        soil = get_object_or_404(SoilInput, id=request.POST.get("soil_id"))
        soil.delete()
        return redirect("custom_admin")

    # ======= Delete Disease =======
    if request.method == "POST" and "delete_disease" in request.POST:
        disease = get_object_or_404(DiseaseDetection, id=request.POST.get("disease_id"))
        disease.delete()
        return redirect("custom_admin")

    if 'delete_contact' in request.POST:
     ContactMessage.objects.filter(id=request.POST.get('contact_id')).delete()


    context = {
        "total_users": total_users,
        "soil_records": soil_records,
        "crop_types": crop_types,
        "disease_reports": disease_reports,
        "crops": crops,
        "crop_infos": crop_infos,
        "soil_inputs": soil_inputs,
        "diseases": diseases,
        "users": users,
        "contact_messages": contact_messages,
    }
    return render(request, "admin.html", context)



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Show success message
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")  # Redirect to the same page

    return render(request, "contact.html")
