import os
import pandas as pd

image_dir = r"C:\Users\ASUSK45A\pione_images\prepared"
output_csv = "image_metadata.csv"

data = []

for file in os.listdir(image_dir):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        data.append({
            "filename": file,
            "crop": "",            # loại cây (điền sau)
            "disease": "",         # bệnh (điền sau)
            "symptoms": "",        # triệu chứng (điền sau)
            "severity": "",        # mức độ: light / medium / heavy
            "treatment": ""        # hướng xử lý
        })

df = pd.DataFrame(data)
df.to_csv(output_csv, index=False, encoding="utf-8-sig")

print("Đã tạo file:", output_csv)
