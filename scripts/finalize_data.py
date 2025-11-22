# finalize_data.py - Tổng hợp tất cả các file Q&A đã tạo thành một file cuối cùng
import os
import re
import json
from sys import exit

# --- CẤU HÌNH ĐƯỜNG DẪN ---
INPUT_DIR = "pione_knowledge/final_qna"  # Thư mục chứa các file Q&A đã tạo bằng LLM
OUTPUT_DIR = "final_submission_data"   # Thư mục lưu trữ file cuối cùng
OUTPUT_FILENAME_TXT = "final_qna_data.txt" # Định dạng TXT (có thể đọc dễ dàng)
OUTPUT_FILENAME_JSON = "final_qna_data.json" # Định dạng JSON (có cấu trúc)

# --- THIẾT LẬP DỮ LIỆU ---
all_qna_data = []
all_qna_text = []
file_count = 0

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Kiểm tra thư mục đầu vào
if not os.path.exists(INPUT_DIR) or not os.listdir(INPUT_DIR):
    print(f"🛑 LỖI: Thư mục đầu vào '{INPUT_DIR}' không tồn tại hoặc trống.")
    print("Vui lòng đảm bảo script auto_qna_generation.py đã chạy thành công.")
    exit()

print(f"BẮT ĐẦU TỔNG HỢP DỮ LIỆU TỪ {INPUT_DIR}...")

# Lặp qua tất cả các file trong thư mục Q&A đã tạo
for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".txt"):
        input_path = os.path.join(INPUT_DIR, filename)
        file_count += 1
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 1. Tổng hợp dữ liệu dưới dạng JSON (có cấu trúc)
            # Tách nội dung thành các cặp Q&A dựa trên định dạng "Q: ... \n A: ..."
            qna_pairs = re.findall(r'Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)', content, re.DOTALL)
            
            for q, a in qna_pairs:
                q = q.strip()
                a = a.strip()
                if q and a:
                    all_qna_data.append({
                        "question": q,
                        "answer": a,
                        "source_file": filename
                    })
            
            # 2. Tổng hợp dữ liệu dưới dạng TEXT (dễ đọc/kiểm tra)
            all_qna_text.append(f"--- SOURCE: {filename} ---\n{content}\n\n")

        except Exception as e:
            print(f"  [LỖI] Không thể đọc hoặc xử lý file {filename}: {e}")

print(f"TỔNG HỢP HOÀN TẤT. Đã xử lý {file_count} file.")
print(f"Tổng số cặp Hỏi & Đáp (Q&A) được tạo: {len(all_qna_data)}")

# --- BƯỚC 1: LƯU FILE TEXT TỔNG HỢP ---
output_path_txt = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME_TXT)
try:
    with open(output_path_txt, 'w', encoding='utf-8') as f:
        f.write("".join(all_qna_text))
    print(f"✅ Đã lưu dữ liệu tổng hợp dạng TXT tại: {output_path_txt}")
except Exception as e:
    print(f"🛑 LỖI: Không thể lưu file TXT: {e}")

# --- BƯỚC 2: LƯU FILE JSON TỔNG HỢP ---
output_path_json = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME_JSON)
try:
    with open(output_path_json, 'w', encoding='utf-8') as f:
        json.dump(all_qna_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Đã lưu dữ liệu tổng hợp dạng JSON tại: {output_path_json}")
except Exception as e:
    print(f"🛑 LỖI: Không thể lưu file JSON: {e}")

print("\n--- QUÁ TRÌNH HOÀN TẤT DỰ ÁN ĐÃ KẾT THÚC ---")