# check_api_keys.py
import os
from openai import OpenAI
from openai import APIError
import time

# --- DANH SÁCH TẤT CẢ CÁC KHÓA API CỦA BẠN ---
API_KEYS = [
    "sk-abcdef1234567890abcdef1234567890abcdef12",
    "sk-1234567890abcdef1234567890abcdef12345678",
    "sk-abcdefabcdefabcdefabcdefabcdefabcdef12",
    "sk-7890abcdef7890abcdef7890abcdef7890abcd",
    "sk-1234abcd1234abcd1234abcd1234abcd1234abcd",
    "sk-abcd1234abcd1234abcd1234abcd1234abcd1234",
    "sk-5678efgh5678efgh5678efgh5678efgh5678efgh",
    "sk-efgh5678efgh5678efgh5678efgh5678efgh5678",
    "sk-ijkl1234ijkl1234ijkl1234ijkl1234ijkl1234",
    "sk-mnop5678mnop5678mnop5678mnop5678mnop5678",
    "sk-qrst1234qrst1234qrst1234qrst1234qrst1234",
    "sk-uvwx5678uvwx5678uvwx5678uvwx5678uvwx5678",
    "sk-1234ijkl1234ijkl1234ijkl1234ijkl1234ijkl",
    "sk-5678mnop5678mnop5678mnop5678mnop5678mnop",
    "sk-qrst5678qrst5678qrst5678qrst5678qrst5678",
    "sk-uvwx1234uvwx1234uvwx1234uvwx1234uvwx1234",
    "sk-1234abcd5678efgh1234abcd5678efgh1234abcd",
    "sk-5678ijkl1234mnop5678ijkl1234mnop5678ijkl",
    "sk-abcdqrstefghuvwxabcdqrstefghuvwxabcdqrst",
    "sk-ijklmnop1234qrstijklmnop1234qrstijklmnop",
    "sk-1234uvwx5678abcd1234uvwx5678abcd1234uvwx",
    "sk-efghijkl5678mnopabcd1234efghijkl5678mnop",
    "sk-mnopqrstuvwxabcdmnopqrstuvwxabcdmnopqrst",
    "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop",
    "sk-abcd1234efgh5678abcd1234efgh5678abcd1234",
    "sk-1234ijklmnop5678ijklmnop1234ijklmnop5678",
    "sk-qrstefghuvwxabcdqrstefghuvwxabcdqrstefgh",
    "sk-uvwxijklmnop1234uvwxijklmnop1234uvwxijkl",
    "sk-abcd5678efgh1234abcd5678efgh1234abcd5678",
    "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop",
    "sk-1234qrstuvwxabcd1234qrstuvwxabcd1234qrst",
    "sk-efghijklmnop5678efghijklmnop5678efghijkl",
    "sk-mnopabcd1234efghmnopabcd1234efghmnopabcd",
    "sk-ijklqrst5678uvwxijklqrst5678uvwxijklqrst",
    "sk-1234ijkl5678mnop1234ijkl5678mnop1234ijkl",
    "sk-abcdqrstefgh5678abcdqrstefgh5678abcdqrst",
    "sk-ijklmnopuvwx1234ijklmnopuvwx1234ijklmnop",
    "sk-efgh5678abcd1234efgh5678abcd1234efgh5678",
    "sk-mnopqrstijkl5678mnopqrstijkl5678mnopqrst",
    "sk-1234uvwxabcd5678uvwxabcd1234uvwxabcd5678",
    "sk-ijklmnop5678efghijklmnop5678efghijklmnop",
    "sk-abcd1234qrstuvwxabcd1234qrstuvwxabcd1234",
    "sk-1234efgh5678ijkl1234efgh5678ijkl1234efgh",
    "sk-5678mnopqrstuvwx5678mnopqrstuvwx5678mnop",
    "sk-abcdijkl1234uvwxabcdijkl1234uvwxabcdijkl",
    "sk-ijklmnopabcd5678ijklmnopabcd5678ijklmnop",
    "sk-1234efghqrstuvwx1234efghqrstuvwx1234efgh",
    "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl",
    "sk-abcd1234efgh5678abcd1234efgh5678abcd1234",
    "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop",
    "sk-1234qrstuvwxabcd1234qrstuvwxabcd1234qrst",
    "sk-efghijklmnop5678efghijklmnop5678efghijkl",
    "sk-mnopabcd1234efghmnopabcd1234efghmnopabcd",
    "sk-ijklqrst5678uvwxijklqrst5678uvwxijklqrst",
    "sk-1234ijkl5678mnop1234ijkl5678mnop1234ijkl",
    "sk-abcdqrstefgh5678abcdqrstefgh5678abcdqrst",
    "sk-ijklmnopuvwx1234ijklmnopuvwx1234ijklmnop",
    "sk-efgh5678abcd1234efgh5678abcd1234efgh5678",
    "sk-mnopqrstijkl5678mnopqrstijkl5678mnopqrst",
    "sk-1234uvwxabcd5678uvwxabcd1234uvwxabcd5678",
    "sk-ijklmnop5678efghijklmnop5678efghijklmnop",
    "sk-abcd1234qrstuvwxabcd1234qrstuvwxabcd1234",
    "sk-1234efgh5678ijkl1234efgh5678ijkl1234efgh",
    "sk-5678mnopqrstuvwx5678mnopqrstuvwx5678mnop",
    "sk-abcdijkl1234uvwxabcdijkl1234uvwxabcdijkl",
    "sk-ijklmnopabcd5678ijklmnopabcd5678ijklmnop",
    "sk-1234efghqrstuvwx1234efghqrstuvwx1234efgh",
    "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl",
    "sk-abcd1234efgh5678abcd1234efgh5678abcd1234",
    "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop",
    "sk-1234qrstuvwxabcd1234qrstuvwxabcd1234qrst",
    "sk-efghijklmnop5678efghijklmnop5678efghijkl",
    "sk-mnopabcd1234efghmnopabcd1234efghmnopabcd",
    "sk-ijklqrst5678uvwxijklqrst5678uvwxijklqrst",
    "sk-1234ijkl5678mnop1234ijkl5678mnop1234ijkl",
    "sk-abcdqrstefgh5678abcdqrstefgh5678abcdqrst",
    "sk-ijklmnopuvwx1234ijklmnopuvwx1234ijklmnop",
    "sk-efgh5678abcd1234efgh5678abcd1234efgh5678",
    "sk-mnopqrstijkl5678mnopqrstijkl5678mnopqrst",
    "sk-1234uvwxabcd5678uvwxabcd1234uvwxabcd5678",
    "sk-ijklmnop5678efghijklmnop5678efghijklmnop",
    "sk-abcd1234qrstuvwxabcd1234qrstuvwxabcd1234",
    "sk-1234efgh5678ijkl1234efgh5678ijkl1234efgh",
    "sk-5678mnopqrstuvwx5678mnopqrstuvwx5678mnop",
    "sk-abcdijkl1234uvwxabcdijkl1234uvwxabcdijkl",
    "sk-ijklmnopabcd5678ijklmnopabcd5678ijklmnop",
    "sk-1234efghqrstuvwx1234efghqrstuvwx1234efgh",
    "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl",
]

VALID_KEYS = []
INVALID_KEYS = []

print(f"--- BẮT ĐẦU KIỂM TRA {len(API_KEYS)} KHÓA API ---")

for i, key in enumerate(API_KEYS):
    # Khởi tạo Client cho từng khóa
    client = OpenAI(api_key=key, timeout=15.0) # Thêm timeout để tránh treo máy
    
    # Chỉ hiển thị 8 ký tự đầu của khóa để tiện theo dõi
    display_key = key[:8] + "..."
    
    print(f"\n[{i+1}/{len(API_KEYS)}] Đang kiểm tra khóa: {display_key}")
    
    try:
        # Thực hiện một lệnh gọi API đơn giản (Lấy danh sách các mô hình)
        # Lệnh này yêu cầu khóa phải hợp lệ và có thể truy cập
        client.models.list() 
        
        print(f"  ✅ HỢP LỆ (Status 200/models.list)")
        VALID_KEYS.append(key)
        
    except APIError as e:
        error_msg = str(e)
        
        # 401: Lỗi Xác thực (Authentication Error) - Khóa không hợp lệ/hết hạn
        if "401" in error_msg or "Invalid API key" in error_msg:
            print(f"  ❌ KHÔNG HỢP LỆ (401 Authentication Error)")
        # 429: Lỗi Rate Limit/Billing - Thường là hết tiền hoặc quá giới hạn yêu cầu
        elif "429" in error_msg or "rate limit" in error_msg or "billing" in error_msg:
            print(f"  ⚠️ CẢNH BÁO (429 Rate Limit/Billing Issue)")
            VALID_KEYS.append(key) # Vẫn coi là hợp lệ nếu có thể dùng được sau này
        else:
            print(f"  ❓ LỖI KHÔNG XÁC ĐỊNH ({error_msg.split(':')[0]})")
        
        INVALID_KEYS.append(key)
        
    except Exception as e:
        print(f"  [LỖI KẾT NỐI/HỆ THỐNG]: {e}")
        INVALID_KEYS.append(key)
        
    # Chờ 0.5 giây giữa các lần kiểm tra để tránh bị chặn IP
    time.sleep(0.5)

print("\n\n=======================================================")
print("             TÓM TẮT KẾT QUẢ KIỂM TRA API             ")
print("=======================================================")
print(f"✅ Số khóa HỢP LỆ (Sẵn sàng sử dụng): {len(VALID_KEYS)}")
print(f"❌ Số khóa KHÔNG HỢP LỆ/LỖI:         {len(INVALID_KEYS)}")
print("-------------------------------------------------------")
print("DANH SÁCH KHÓA HỢP LỆ:")
for key in VALID_KEYS:
    print(key)
print("=======================================================")