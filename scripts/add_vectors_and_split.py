# embed_images_and_split.py
"""
Embed image binary (base64) directly into CSV and split into parts <= MAX_BYTES.

Usage (Windows):
  1. Put this script in the folder containing `image_metadata_with_desc.csv`
     or adjust INPUT_CSV and IMAGE_DIR in CONFIG.
  2. Open Command Prompt, cd to the folder and run:
       python embed_images_and_split.py

Outputs:
  - image_metadata_with_images.csv   (full CSV with new column 'image_base64')
  - image_metadata_part_001.csv ...  (parts, each <= MAX_BYTES)
"""

import os
import sys
import base64
import math
import io
from PIL import Image
import pandas as pd
from tqdm import tqdm

# ========== CONFIG ==========
IMAGE_DIR = r"C:\Users\ASUSK45A\pione_images\prepared"   # folder chứa ảnh đã chuẩn
INPUT_CSV = "image_metadata_with_desc.csv"               # input CSV tên
OUTPUT_FULL_CSV = "image_metadata_with_images.csv"       # full CSV output (may be large)
PART_PREFIX = "image_metadata_part_"                     # prefix cho các phần
MAX_BYTES = 5 * 1024 * 1024                              # 5 MB giới hạn phần
# Image compress options (giúp giảm base64 size)
RESIZE = (512, 512)          # kích thước resize (None để giữ nguyên)
JPEG_QUALITY = 70            # 1..95, thấp hơn -> nhỏ hơn file (cân nhắc)
SKIP_IF_MISSING = True       # nếu ảnh không tìm thấy, sẽ bỏ trống image_base64 (không dừng script)
# ============================

def find_image_path(fname):
    """
    Tìm file bằng tên:
      - nếu fname là đường dẫn tuyệt đối và tồn tại -> dùng
      - nếu fname exists relative -> dùng
      - thử tìm basename trong IMAGE_DIR
    Trả về đường dẫn tồn tại hoặc None.
    """
    # check absolute/path as-is
    if os.path.isabs(fname) and os.path.exists(fname):
        return fname
    # check relative
    if os.path.exists(fname):
        return os.path.abspath(fname)
    # try in IMAGE_DIR
    p = os.path.join(IMAGE_DIR, fname)
    if os.path.exists(p):
        return p
    # try basename matches in IMAGE_DIR (case-insensitive)
    bn = os.path.basename(fname)
    for root, _, files in os.walk(IMAGE_DIR):
        for f in files:
            if f.lower() == bn.lower():
                return os.path.join(root, f)
    return None

def load_and_encode_image(path, resize=RESIZE, quality=JPEG_QUALITY):
    """
    Load image via PIL, optionally resize and re-encode to JPEG with given quality,
    then return base64 string (utf-8 str).
    """
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Cannot open image {path}: {e}")

    if resize is not None:
        img = img.resize(resize, Image.LANCZOS)

    # save to bytes buffer as JPEG to control size
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    b = buf.getvalue()
    # encode to base64 (ascii)
    b64 = base64.b64encode(b).decode('ascii')
    return b64

def safe_write_part(path, header_line, rows_bytes):
    """
    Write rows_bytes (list of bytes lines) to path.
    header_line: bytes already containing header + newline (utf-8)
    """
    with open(path, "wb") as f:
        f.write(header_line)
        for line in rows_bytes:
            f.write(line)

def main():
    if not os.path.exists(INPUT_CSV):
        print("Input CSV not found:", INPUT_CSV)
        sys.exit(1)

    print("Loading CSV:", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

    # Ensure columns exist
    if 'filename' not in df.columns and 'file' not in df.columns:
        print("CSV must contain a 'filename' (or 'file') column with image file names.")
        sys.exit(1)

    fname_col = 'filename' if 'filename' in df.columns else 'file'
    # add image_base64 column
    if 'image_base64' not in df.columns:
        df['image_base64'] = ""

    # Process each row: find image, encode and insert base64
    print("Embedding images (this may take time) ...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        fname = str(row.get(fname_col, "")).strip()
        if fname == "":
            # no filename specified
            df.at[idx, 'image_base64'] = ""
            continue
        img_path = find_image_path(fname)
        if img_path is None:
            warning = f"[MISSING:{fname}]"
            print("Warning: image not found for", fname)
            if SKIP_IF_MISSING:
                df.at[idx, 'image_base64'] = ""
                continue
            else:
                print("Stopping due missing image.")
                sys.exit(1)
        try:
            b64 = load_and_encode_image(img_path, resize=RESIZE, quality=JPEG_QUALITY)
            # embed as data URI style optional: "data:image/jpeg;base64,<b64>"
            df.at[idx, 'image_base64'] = b64
        except Exception as e:
            print("Error encoding", img_path, e)
            df.at[idx, 'image_base64'] = ""
            continue

    # Save full CSV (may be big)
    print("Saving full CSV with embedded images:", OUTPUT_FULL_CSV)
    df.to_csv(OUTPUT_FULL_CSV, index=False, encoding="utf-8-sig")
    print("Full CSV saved. Size (bytes):", os.path.getsize(OUTPUT_FULL_CSV))

    # Now split into parts <= MAX_BYTES
    print("Splitting into parts with max bytes:", MAX_BYTES)
    header = df.columns.tolist()
    # prepare header bytes (utf-8-sig)
    import csv
    header_line = (",".join(header) + "\n").encode('utf-8')
    part_idx = 1
    out_rows = []   # list of bytes lines for current part
    current_bytes = len(header_line)
    written_rows = 0

    def row_to_bytes(row_values):
        # quote fields as needed and return bytes
        # use simple CSV quoting: wrap " and double internal "
        safe_vals = []
        for v in row_values:
            if v is None:
                v = ""
            s = str(v)
            s = s.replace('"', '""')
            safe_vals.append(f'"{s}"')
        line = ",".join(safe_vals) + "\n"
        return line.encode('utf-8')

    # iterate rows and accumulate
    for i, row in df.iterrows():
        row_values = [row.get(col, "") for col in header]
        rb = row_to_bytes(row_values)
        rb_len = len(rb)
        # if adding would exceed MAX_BYTES and we already have rows -> flush
        if current_bytes + rb_len > MAX_BYTES and written_rows > 0:
            out_name = f"{PART_PREFIX}{part_idx:03d}.csv"
            print(f"Writing part {out_name} - size ~{current_bytes} bytes, rows {written_rows}")
            # write file
            with open(out_name, "wb") as f:
                f.write(header_line)
                for r in out_rows:
                    f.write(r)
            # reset
            part_idx += 1
            out_rows = []
            current_bytes = len(header_line)
            written_rows = 0
        # append current row
        out_rows.append(rb)
        current_bytes += rb_len
        written_rows += 1

    # flush last part
    if written_rows > 0:
        out_name = f"{PART_PREFIX}{part_idx:03d}.csv"
        print(f"Writing part {out_name} - size ~{current_bytes} bytes, rows {written_rows}")
        with open(out_name, "wb") as f:
            f.write(header_line)
            for r in out_rows:
                f.write(r)

    print("Done. Parts created (prefix):", PART_PREFIX)
    print("Tip: if parts exceed limit, reduce RESIZE or JPEG_QUALITY to make images smaller.")

if __name__ == "__main__":
    main()
