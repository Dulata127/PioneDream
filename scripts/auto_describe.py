# auto_describe.py
import os
import cv2
import numpy as np
import pandas as pd
from skimage import color, measure, filters, morphology
from PIL import Image
from tqdm import tqdm
import hashlib

# ===== CONFIG =====
IMAGE_DIR = r"C:\Users\ASUSK45A\pione_images\prepared"   # thư mục ảnh đã resize
INPUT_CSV = "image_metadata.csv"      # file CSV ban đầu (tạo ở bước trước)
OUTPUT_CSV = "image_metadata_with_desc.csv"
TARGET_SIZE = None   # nếu muốn resize khi đọc, set (512,512) hoặc None để giữ nguyên
# thresholds (có thể tinh chỉnh)
BROWN_HUE_MIN = 5    # độ (HSV) tham khảo
BROWN_HUE_MAX = 30
BROWN_SAT_MIN = 60   # độ bão hòa tối thiểu
BROWN_VAL_MAX = 200  # loại trừ các vùng quá sáng
GREEN_HUE_MIN = 35
GREEN_HUE_MAX = 100
# Minimum area in pixels to count as a spot
MIN_SPOT_AREA = 50  

# ===== helpers =====
def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

def read_image(path):
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)  # handles unicode paths on Windows
    if img is None:
        return None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def compute_brightness(img):
    # img in RGB
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return float(np.mean(gray))

def compute_green_ratio_hsv(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h,s,v = cv2.split(hsv)
    # mask for green hue range
    mask = ((h >= GREEN_HUE_MIN) & (h <= GREEN_HUE_MAX) & (s >= 40))
    return float(mask.sum()) / (img.shape[0] * img.shape[1])

def detect_brown_spots(img):
    """
    Return: brown_area_pixels, brown_area_pct, spot_count, avg_spot_area
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h,s,v = cv2.split(hsv)
    # brown-ish mask heuristics
    mask_brown = ((h >= BROWN_HUE_MIN) & (h <= BROWN_HUE_MAX) & (s >= BROWN_SAT_MIN) & (v <= BROWN_VAL_MAX))
    mask_brown = mask_brown.astype(np.uint8) * 255

    # Morphology clean
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask_brown = cv2.morphologyEx(mask_brown, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_brown = cv2.morphologyEx(mask_brown, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Label connected components
    labeled = measure.label(mask_brown > 0)
    regions = measure.regionprops(labeled)
    areas = [r.area for r in regions if r.area >= MIN_SPOT_AREA]
    spot_count = len(areas)
    total_brown = int(np.sum(mask_brown > 0))
    img_area = img.shape[0] * img.shape[1]
    brown_pct = float(total_brown) / img_area if img_area>0 else 0.0
    avg_area = float(np.mean(areas)) if areas else 0.0
    return total_brown, brown_pct, spot_count, avg_area

def estimate_severity(brown_pct, green_ratio):
    # heuristic: adjust thresholds to your dataset
    if brown_pct > 0.10 or green_ratio < 0.25:
        return "nặng"
    elif brown_pct > 0.03 or green_ratio < 0.40:
        return "trung bình"
    else:
        return "nhẹ"

def make_description(filename, brightness, green_ratio, brown_pct, spot_count, avg_spot_area):
    parts = []
    parts.append(f"Ảnh '{filename}': độ sáng trung bình {brightness:.0f}.")
    parts.append(f"Tỷ lệ màu xanh lá (ước tính): {green_ratio*100:.1f}%.")
    parts.append(f"Tỷ lệ vùng nâu/đốm: {brown_pct*100:.2f}% với {spot_count} vết (TB diện tích vết {avg_spot_area:.1f} px).")
    # quick diagnosis hint
    hint = ""
    if brown_pct > 0.05 and spot_count >= 3:
        hint = "Khả năng cao có bệnh do nấm (vết nâu)."
    elif green_ratio < 0.30:
        hint = "Cây có thể thiếu dinh dưỡng/khô hạn (vàng/thiếu xanh)."
    else:
        hint = "Trông tương đối khỏe; cần kiểm tra thực địa nếu nghi ngờ."
    parts.append(hint)
    parts.append("Ghi chú: mô tả tự động, cần xác nhận bởi chuyên gia.")
    return " ".join(parts)

# ===== main =====
def main():
    # load csv (or build list if csv not exists)
    if os.path.exists(INPUT_CSV):
        df = pd.read_csv(INPUT_CSV, dtype=str)
    else:
        # build from image folder
        rows = []
        for f in sorted(os.listdir(IMAGE_DIR)):
            if f.lower().endswith((".jpg",".jpeg",".png")):
                rows.append({"filename": f, "crop":"", "disease":"", "symptoms":"", "severity":"", "treatment":""})
        df = pd.DataFrame(rows)

    # prepare output columns
    for col in ["sha256","width","height","brightness","green_ratio","brown_pct","brown_pixels","spot_count","avg_spot_area","auto_description","auto_severity"]:
        if col not in df.columns:
            df[col] = ""

    # iterate
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        fname = row["filename"]
        path = os.path.join(IMAGE_DIR, fname)
        if not os.path.exists(path):
            print("Không tìm thấy:", path)
            continue
        img = read_image(path)
        if img is None:
            print("Không đọc ảnh:", path)
            continue
        # optional resizing
        if TARGET_SIZE is not None:
            img = cv2.resize(img, TARGET_SIZE, interpolation=cv2.INTER_AREA)

        h, w, _ = img.shape
        brightness = compute_brightness(img)
        green_ratio = compute_green_ratio_hsv(img)
        brown_pixels, brown_pct, spot_count, avg_spot_area = detect_brown_spots(img)
        severity = estimate_severity(brown_pct, green_ratio)
        desc = make_description(fname, brightness, green_ratio, brown_pct, spot_count, avg_spot_area)
        sha = sha256_file(path)

        # write back
        df.at[idx, "sha256"] = sha
        df.at[idx, "width"] = w
        df.at[idx, "height"] = h
        df.at[idx, "brightness"] = round(float(brightness),1)
        df.at[idx, "green_ratio"] = round(float(green_ratio),4)
        df.at[idx, "brown_pct"] = round(float(brown_pct),6)
        df.at[idx, "brown_pixels"] = int(brown_pixels)
        df.at[idx, "spot_count"] = int(spot_count)
        df.at[idx, "avg_spot_area"] = round(float(avg_spot_area),1)
        df.at[idx, "auto_description"] = desc
        df.at[idx, "auto_severity"] = severity

    # save
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print("Hoàn tất. File đầu ra:", OUTPUT_CSV)

if __name__ == "__main__":
    main()
