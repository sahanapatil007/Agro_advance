import csv
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agro_advance.settings")
django.setup()

from agroapp.models import CropRequirement  # change to your app name

CSV_FILE_PATH = 'Crop_recomendation.csv'

def load_crop_data(csv_file):
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
          print(row)  # 👈 add this
          try:
                crop_name = row.get('label') or row.get('crop') or row.get('Crop_Name')
                nitrogen = float(row['N'])
                phosphorus = float(row['P'])
                potassium = float(row['K'])
                ph = float(row['ph'])
                rainfall = float(row['rainfall'])
                temperature = float(row['temperature'])

                CropRequirement.objects.update_or_create(
                    crop_name=crop_name,
                    defaults={
                        'nitrogen_req': nitrogen,
                        'phosphorus_req': phosphorus,
                        'potassium_req': potassium,
                        'ph_min': ph - 0.5,
                        'ph_max': ph + 0.5,
                        'rainfall_min': rainfall - 20,
                        'rainfall_max': rainfall + 20,
                        'temperature_min': temperature - 3,
                        'temperature_max': temperature + 3,
                    }
                )
                count += 1
          except Exception as e:
                print(f"Skipping row due to error: {e}")
                continue

    print(f"✅ Successfully loaded/updated {count} crop records!")

if __name__ == '__main__':
    if os.path.exists(CSV_FILE_PATH):
        load_crop_data(CSV_FILE_PATH)
    else:
        print(f"❌ CSV file not found at {CSV_FILE_PATH}")