import cv2
import numpy as np
from ultralytics import YOLO
# Parameters to reduce false positives
CONF_THRESHOLD = 0.5   # confidence threshold
IOU_THRESHOLD = 0.45   # NMS IoU threshold
MIN_BOX_SIZE = 10      # minimum box width/height in pixels

model = YOLO(r"best.pt")
# Load image
img_path = "two.jpeg"
img = cv2.imread(img_path)

# YOLOv8 inference
results = model.predict(
    source=img_path,
    conf=CONF_THRESHOLD,
    iou=IOU_THRESHOLD,
    verbose=False
)

# Get detections
boxes = results[0].boxes  # xyxy, confidence, class
xyxy = boxes.xyxy.cpu().numpy()
conf = boxes.conf.cpu().numpy()
cls = boxes.cls.cpu().numpy().astype(int)
names = model.names

# Filter tiny boxes (optional)
filtered_boxes = []
for i in range(len(xyxy)):
    x1, y1, x2, y2 = xyxy[i]
    w, h = x2 - x1, y2 - y1
    if w >= MIN_BOX_SIZE and h >= MIN_BOX_SIZE:
        filtered_boxes.append((int(x1), int(y1), int(x2), int(y2), conf[i], cls[i]))

# Draw boxes
for x1, y1, x2, y2, c, cl in filtered_boxes:
    label = f"{names[cl]} {c:.2f}"
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Show result
cv2.imshow("Prediction", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save output
cv2.imwrite("/content/test/prediction.jpg", img)