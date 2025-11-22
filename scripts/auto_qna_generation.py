# auto_qna_generation.py - SỬ DỤNG GEMINI API (Mô hình gemini-2.5-flash)
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
import time
from sys import exit

# --- THIẾT LẬP KHÓA API GEMINI ---
# Khóa API đã được bổ sung theo yêu cầu của bạn.
GEMINI_API_KEY = "AIzaSyAWb0D8hpbm2Qg1Ekvoye0EyAw1Vd9nC7Y" 

if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("DÁN_KHÓA_API"):
    print("!!! LỖI KHÓA API: Khóa API Gemini chưa được thiết lập chính xác. !!!")
    exit()

# Khởi tạo Client Gemini
# API Key được truyền trực tiếp khi khởi tạo Client
client = genai.Client(api_key=GEMINI_API_KEY)

# --- CẤU HÌNH LLM ---
LLM_MODEL = "gemini-2.5-flash"
INPUT_DIR = "pione_knowledge/text_qa" 
OUTPUT_DIR = "pione_knowledge/final_qna"

os.makedirs(OUTPUT_DIR, exist_ok=True)
processed_count = 0

def generate_qna_from_text(chunk_text):
    """Sử dụng Gemini LLM để chuyển đổi đoạn văn bản thành định dạng Q&A."""
    
    SYSTEM_INSTRUCTION = (
        "Bạn là một chuyên gia nông nghiệp có kinh nghiệm. Nhiệm vụ của bạn là chuyển đổi "
        "đoạn văn bản kỹ thuật sau đây thành một danh sách khoảng 5-8 cặp Hỏi & Đáp (Q&A) chuyên môn, "
        "tập trung vào các thông tin quan trọng nhất (triệu chứng, cách phòng ngừa, liều lượng,...). "
        "Mỗi câu trả lời (A) phải dựa chặt chẽ trên thông tin CÓ TRONG đoạn văn. "
        "Sử dụng tiếng Việt, KHÔNG THÊM thông tin ngoài. "
        "Định dạng đầu ra PHẢI LÀ 'Q: [câu hỏi]\nA: [câu trả lời]' cho mỗi cặp Q&A, và mỗi cặp cách nhau một dòng trống."
    )
    
    USER_PROMPT = f"Đoạn văn cần chuyển đổi: \n\n{chunk_text}"

    # Thử lại 3 lần nếu gặp lỗi Rate Limit (429) hoặc lỗi kết nối
    for attempt in range(3):
        try:
            # Gọi Gemini API
            response = client.models.generate_content(
                model=LLM_MODEL,
                contents=USER_PROMPT,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                ),
            )
            # Trả về nội dung đã tạo
            return response.text

        except APIError as e:
            error_msg = str(e)
            
            if "429" in error_msg or "rate limit" in error_msg:
                print(f"  [LỖI API] Gặp Rate Limit (429). Đang chờ và thử lại...")
                time.sleep(5) 
            elif "400" in error_msg or "403" in error_msg:
                print(f"  [LỖI API] Khóa không hợp lệ (400/403). Vui lòng kiểm tra lại Khóa API.")
                break 
            else:
                print(f"  [LỖI API KHÁC] Lỗi: {error_msg}. Đang thử lại...")
                time.sleep(5)
        
        except Exception as e:
            print(f"  [LỖI KẾT NỐI/HỆ THỐNG]: {e}. Đang thử lại...")
            time.sleep(5)
    
    print(f"  [THẤT BẠI] Xử lý file này thất bại sau các lần thử.")
    return None

print(f"BẮT ĐẦU TẠO Q&A TỰ ĐỘNG bằng {LLM_MODEL} từ thư mục: {INPUT_DIR}")

# --- Bắt đầu quá trình xử lý file ---
for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".txt"):
        input_path = os.path.join(INPUT_DIR, filename)
        
        # Bỏ qua file quá nhỏ
        if os.path.getsize(input_path) < 100: continue
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Lấy nội dung gốc sau dấu phân cách
                content_to_process = content.split('--- ĐOẠN VĂN GỐC ---')[-1].strip()
            
            if not content_to_process: continue

            print(f"\n[{processed_count + 1}] Đang xử lý file: {filename}...")
            
            qna_text = generate_qna_from_text(content_to_process)
            
            if qna_text:
                output_path = os.path.join(OUTPUT_DIR, filename)
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(qna_text)
                
                print(f"  -> THÀNH CÔNG! Lưu tại: {output_path}")
                processed_count += 1
            
            time.sleep(0.5) 
            
        except Exception as e:
            print(f"  [LỖI HỆ THỐNG]: Xử lý file {filename} thất bại: {e}")

print("------------------------------------------------")
print(f"HOÀN TẤT! Tổng số file Q&A được AI xử lý: {processed_count}. Kết quả nằm trong {OUTPUT_DIR}")