import cv2
import numpy as np

def process_image(image_path):
    # 讀取圖像並灰度化
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 二值化（反轉顏色：黑框變為白色區域）
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
    
    # 形態學操作去除雜訊
    kernel = np.ones((3,3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # 檢測輪廓
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 過濾小面積輪廓（僅保留可能的黑框）
    min_area = 100
    boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append((x, y, w, h))
    
    return boxes, img.shape