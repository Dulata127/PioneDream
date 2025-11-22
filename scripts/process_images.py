# process_images.py
import os
from PIL import Image

# ----------------- THIẾT LẬP ĐẦU VÀO/ĐẦU RA -----------------
# Thư mục chứa ảnh thô (đã copy từ PlantVillage)
# CHÚ Ý: Thay đổi đường dẫn này nếu khác
INPUT_DIR = "pione_images/raw/plantvillage" 
# Thư mục chứa ảnh đã xử lý (sẵn sàng upload)
OUTPUT_DIR = "pione_images/prepared" 
# Kích thước ảnh chuẩn hóa (có thể chọn (224, 224) nếu muốn nhẹ hơn)
TARGET_SIZE = (512, 512) 

# Tạo thư mục đầu ra nếu chưa tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bộ đếm số lượng ảnh đã xử lý thành công
count = 0

print(f"Bắt đầu xử lý ảnh từ: {INPUT_DIR}")
print(f"Ảnh sẽ được resize về: {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")

# Duyệt qua tất cả các thư mục con và file trong thư mục INPUT_DIR
for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        # Chỉ xử lý file ảnh JPG, JPEG, PNG
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                # 1. Mở ảnh
                img_path = os.path.join(root, file)
                img = Image.open(img_path).convert('RGB') # Đảm bảo ảnh là 3 kênh màu

                # 2. Resize ảnh
                img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)

                # 3. Đặt tên mới theo quy ước (vd: image_000001.jpg)
                new_name = f"image_{count:06d}.jpg" 
                
                # 4. Lưu ảnh đã xử lý (nén JPEG chất lượng 90)
                output_path = os.path.join(OUTPUT_DIR, new_name)
                img.save(output_path, format="JPEG", quality=90)
                
                count += 1

            except Exception as e:
                # 5. Xử lý ảnh lỗi (không đọc được hoặc định dạng sai)
                print(f"  [LỖI] Bỏ qua file: {img_path}. Lỗi: {e}")

print("------------------------------------------------")
print(f"HOÀN TẤT. Tổng số ảnh đã xử lý thành công: {count}")