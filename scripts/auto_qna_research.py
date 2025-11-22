# auto_qna_research.py
import os
from openai import OpenAI  # Hoặc thư viện của mô hình LLM bạn chọn
import time

# --- THIẾT LẬP API VÀ ĐƯỜNG DẪN ---
# CẦN THAY THẾ KHÓA API CỦA BẠN VÀO ĐÂY
# Bạn nên lưu khóa này trong biến môi trường, nhưng để đơn giản, có thể dán trực tiếp.
client = OpenAI(api_key="YOUR_OPENAI_API_KEY") 
LLM_MODEL = "gpt-3.5-turbo" # Mô hình mạnh mẽ, hiệu quả về chi phí
# Thư mục đầu vào (đã được chia đoạn bởi chunk_and_format.py)
INPUT_DIR = "pione_knowledge/text_qa" 
OUTPUT_DIR = "pione_knowledge/auto_qna_final"

os.makedirs(OUTPUT_DIR, exist_ok=True)
processed_count = 0

def generate_qna_from_text(chunk_text):
    """Sử dụng LLM để chuyển đổi đoạn văn bản thành định dạng Q&A."""
    
    # --- PROMPT CHUYÊN SÂU CHO AI ---
    # Prompt này rất quan trọng để đảm bảo chất lượng chuyên môn
    SYSTEM_PROMPT = (
        "Bạn là một chuyên gia nông nghiệp hàng đầu. Nhiệm vụ của bạn là chuyển đổi "
        "đoạn văn bản kỹ thuật sau đây thành một danh sách các cặp Hỏi & Đáp (Q&A) chuyên môn. "
        "Mỗi câu trả lời (A) phải dựa trên thông tin có trong đoạn văn. "
        "Sử dụng tiếng Việt, KHÔNG THÊM BẤT KỲ THÔNG TIN NÀO BÊN NGOÀI ĐOẠN VĂN GỐC. "
        "Định dạng đầu ra PHẢI LÀ 'Q: [câu hỏi]\nA: [câu trả lời]'."
    )
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Đoạn văn cần chuyển đổi: \n\n{chunk_text}"}
            ],
            temperature=0.3 # Giữ nhiệt độ thấp để câu trả lời chính xác, ít sáng tạo
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  [LỖI API]: {e}")
        return None

print(f"BẮT ĐẦU TẠO Q&A TỰ ĐỘNG bằng AI từ thư mục: {INPUT_DIR}")

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".txt"):
        input_path = os.path.join(INPUT_DIR, filename)
        
        # Bỏ qua file nếu nó quá nhỏ (ví dụ: file trống)
        if os.path.getsize(input_path) < 100:
            print(f"  [BỎ QUA] File {filename} quá nhỏ.")
            continue
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                # Đọc nội dung và chỉ lấy đoạn văn bản gốc (loại bỏ hướng dẫn biên tập)
                content = f.read()
                # Loại bỏ phần header nếu script chunk_and_format đã tạo ra
                content_to_process = content.split('--- ĐOẠN VĂN GỐC ---')[-1].strip()
            
            print(f"\n[{processed_count + 1}] Đang gọi AI xử lý file: {filename}...")
            
            # 1. Gọi API để tạo Q&A
            qna_text = generate_qna_from_text(content_to_process)
            
            if qna_text:
                # 2. Lưu kết quả vào thư mục cuối cùng
                output_path = os.path.join(OUTPUT_DIR, filename)
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(qna_text)
                
                print(f"  -> THÀNH CÔNG! Lưu tại: {output_path}")
                processed_count += 1
            
            # Dừng 1 giây để tránh bị giới hạn tốc độ (rate limit) của API
            time.sleep(1) 
            
        except Exception as e:
            print(f"  [LỖI HỆ THỐNG]: Xử lý file {filename} thất bại: {e}")

print("------------------------------------------------")
print(f"HOÀN TẤT! Tổng số file Q&A được AI xử lý: {processed_count}")