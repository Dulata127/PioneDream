import os
import pandas as pd

image_dir = r"C:\Users\ASUSK45A\pione_images\prepared"
files = [f for f in os.listdir(image_dir) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]

df = pd.DataFrame({"filename": files})
df.to_csv("image_metadata.csv", index=False, encoding="utf-8-sig")

print("Đã tạo image_metadata.csv với", len(files), "ảnh.")
