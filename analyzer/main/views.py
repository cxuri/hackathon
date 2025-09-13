from django.shortcuts import render

# Create your views here.
from django.conf import settings
from . import views


def Home(request):
    return render(request, "homepage.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("login")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "main/login.html")

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "main/signup.html")


import os
import cv2
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from ultralytics import YOLO
from django.conf import settings

# Load YOLO model once
MODEL_PATH = os.path.join(settings.BASE_DIR, "main", "best.pt")

model = YOLO(MODEL_PATH)

# Simple example cost map (you can expand/change this later)
PART_COSTS = {
    "front_bumper": 10000,
    "rear_bumper": 9000,
    "door": 7000,
    "headlamp": 3000,
    "windshield": 8000,
    "fender": 4500,
    "mirror": 2000,
    "hood": 9000,
    "taillight": 2500,
    "roof": 5000,
}

import os
import cv2
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from ultralytics import YOLO
from django.conf import settings

# Load YOLO model once
MODEL_PATH = os.path.join(settings.BASE_DIR, "main", "best.pt")
model = YOLO(MODEL_PATH)
def analyze_images(request):
    analyzed_results = []  # store results for each image
    overall_total = 0      # sum of all image costs

    if request.method == "POST":
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "uploads"))

        for field in ["car_front", "car_left", "car_right", "car_back"]:
            image_file = request.FILES.get(field)
            if not image_file:
                continue

            # Save file
            filename = fs.save(image_file.name, image_file)
            abs_path = fs.path(filename)

            # Read image
            img = cv2.imread(abs_path)

            # Run YOLO detection
            results = model.predict(source=abs_path, conf=0.5, iou=0.45, verbose=False)
            boxes = results[0].boxes
            names = model.names

            # Per-image cost
            parts_cost = {}
            total_cost = 0

            for i, box in enumerate(boxes.xyxy.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box[:4])
                conf = float(boxes.conf[i])
                cls = int(boxes.cls[i])
                part_name = names[cls]

                # Draw bounding box
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, f"{part_name} {conf:.2f}",
                            (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)

                # Calculate cost
                if part_name in PART_COSTS:
                    cost = PART_COSTS.get(part_name, 5000)  # 5000 is default if part not in dict
                    parts_cost[part_name] = parts_cost.get(part_name, 0) + cost
                    total_cost += cost
                    overall_total += cost


            # Save annotated image
            result_dir = os.path.join(settings.MEDIA_ROOT, "results")
            os.makedirs(result_dir, exist_ok=True)
            result_path = os.path.join(result_dir, filename)
            cv2.imwrite(result_path, img)

            # Append per-image results
            analyzed_results.append({
                "filename": image_file.name,
                "result_image": os.path.join(settings.MEDIA_URL, "results", filename),
                "parts_cost": parts_cost,
                "total_cost": total_cost,
            })

    return render(request, "homepage.html", {
        "analyzed_results": analyzed_results,
        "overall_total": overall_total,
    })
