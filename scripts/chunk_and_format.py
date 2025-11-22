# chunk_and_format.py
import os
import re

# --- THIẾT LẬP ĐƯỜNG DẪN VÀ KÍCH THƯỚC CHUNK ---
INPUT_DIR = "cleaned_text"
OUTPUT_DIR = "pione_knowledge/text_qa"
# Kích thước tối đa của một đoạn (chunk)
CHUNK_SIZE = 1000  # Tính bằng ký tự

# Tạo thư mục đầu ra nếu chưa tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("BẮT ĐẦU CHIA NHỎ VÀ ĐỊNH DẠNG Q&A CƠ BẢN...")
total_chunks = 0

# Duyệt qua tất cả các file text đã được làm sạch
for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".txt"):
        input_path = os.path.join(INPUT_DIR, filename)
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chia nội dung thành các đoạn dựa trên CHUNK_SIZE
            # Sử dụng regex để chia tại các điểm ngắt câu (dấu chấm câu) gần CHUNK_SIZE nhất
            chunks = re.findall(f'.{{1,{CHUNK_SIZE}}}(?:\.|\n\n|$)', content, re.DOTALL)
            
            if not chunks:
                 # Nếu file nhỏ hơn CHUNK_SIZE, nó vẫn là một chunk
                 chunks = [content]

            file_base_name = os.path.splitext(filename)[0].replace('_clean', '')
            
            print(f"\n--- Xử lý file {filename}: {len(chunks)} đoạn ---")

            for i, chunk in enumerate(chunks):
                # Tên file đầu ra: Tên_gốc_Phan_i.txt
                output_filename = f"{file_base_name}_Phan_{i+1}.txt"
                output_path = os.path.join(OUTPUT_DIR, output_filename)

                # Thêm hướng dẫn biên tập vào đầu file
                formatted_chunk = (
                    "**[CHÚ Ý: Cần biên tập thủ công thành Q: và A:]**\n\n"
                    f"Q: Tóm tắt nội dung chính của đoạn văn này?\n"
                    f"A: {chunk.strip()}\n"
                    "\n--- ĐOẠN VĂN GỐC ---\n"
                    f"{chunk.strip()}"
                )

                with open(output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(formatted_chunk)
                
                total_chunks += 1
                print(f"  -> Tạo {output_filename}")

        except Exception as e:
            print(f"  [LỖI] Xử lý file {filename}: {e}")

print("------------------------------------------------")
print(f"HOÀN TẤT! Tổng số file Q&A được tạo: {total_chunks}. Vui lòng kiểm tra thư mục {OUTPUT_DIR}")