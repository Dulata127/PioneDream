# extract_pdf_auto.py
import pdfplumber
import re
import os

# --- THIẾT LẬP ĐƯỜNG DẪN CỐ ĐỊNH (WINDOWS) ---
# Thư mục chứa file PDF gốc của bạn
INPUT_DIR = r"C:\Users\ASUSK45A\raw_docs"
# Thư mục sẽ lưu trữ các file text đã trích xuất
OUTPUT_DIR = "cleaned_text"

# Tạo thư mục đầu ra nếu chưa tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text(text):
    """Hàm dọn dẹp nội dung văn bản."""
    text = text.strip()
    # Xóa các ký tự lặp lại (ví dụ: ---, ===)
    text = re.sub(r'[-]{2,}', '', text)
    text = re.sub(r'[=]{2,}', '', text)
    # Xóa số trang (ví dụ: Trang 10, Page 15)
    text = re.sub(r'Trang\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Page\s+\d+', '', text, flags=re.IGNORECASE)
    # Xóa các dòng chỉ chứa số (có thể là số mục lục hoặc số trang)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Giảm khoảng trắng xuống dòng quá nhiều thành 2 dòng
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

# --- BẮT ĐẦU QUÁ TRÌNH TỰ ĐỘNG ---
print(f"BẮT ĐẦU QUÉT THƯ MỤC: {INPUT_DIR}")
count = 0

# Lặp qua tất cả file trong thư mục đầu vào
for filename in os.listdir(INPUT_DIR):
    # Chỉ xử lý file có đuôi .pdf
    if filename.lower().endswith(".pdf"):
        
        pdf_input_path = os.path.join(INPUT_DIR, filename)
        
        # Tạo tên file đầu ra: Lấy tên file (bỏ .pdf) + thêm "_clean.txt"
        base_name = os.path.splitext(filename)[0]
        txt_output_filename = f"{base_name}_clean.txt"
        txt_output_path = os.path.join(OUTPUT_DIR, txt_output_filename)
        
        all_text = ""
        print(f"\n[{count + 1}] Đang xử lý file: {filename}...")

        try:
            with pdfplumber.open(pdf_input_path) as pdf:
                for page in pdf.pages:
                    raw = page.extract_text()
                    if raw:
                        cleaned = clean_text(raw)
                        all_text += cleaned + "\n\n"

            # Ghi nội dung đã dọn dẹp ra file .txt
            with open(txt_output_path, "w", encoding="utf-8") as f:
                f.write(all_text)
            
            print(f"  --> THÀNH CÔNG! Lưu tại: {txt_output_path}")
            count += 1

        except FileNotFoundError:
            print(f"  [LỖI] KHÔNG TÌM THẤY FILE: {filename}")
        except Exception as e:
            print(f"  [LỖI XỬ LÝ file {filename}]: {e}")

print("------------------------------------------------")
print(f"HOÀN TẤT TRÍCH XUẤT. Tổng số file PDF được xử lý: {count}")