import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

def load_yolo_model(model_path='yolov8n.pt'):
    return YOLO(model_path)

def load_image_from_pil(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def detect_objects(image, model):
    result = model(image)[0]
    boxes_info = []
    img_copy = image.copy()
    for i, box in enumerate(result.boxes.xyxy):
        x1, y1, x2, y2 = map(int, box)
        boxes_info.append({'id': i, 'bbox': (x1, y1, x2, y2)})
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img_copy, str(i + 1), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return boxes_info, img_copy

def crop_object(image, boxes_info, box_id):
    if 0 <= box_id < len(boxes_info):
        x1, y1, x2, y2 = boxes_info[box_id]['bbox']
        return image[y1:y2, x1:x2]
    else:
        return None
