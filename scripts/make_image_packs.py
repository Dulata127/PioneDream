# make_image_packs.py
import os
import shutil
import pandas as pd

# --- CONFIG ---
IMAGE_DIR = r"C:\Users\ASUSK45A\pione_images\prepared"   # nơi ảnh gốc
PART_PREFIX = "image_metadata_part_"    # phải khớp với script split
N_PARTS = 10
OUT_BASE = r"C:\Users\ASUSK45A\pione_images\packs"      # nơi tạo pack folders + zips

os.makedirs(OUT_BASE, exist_ok=True)

for i in range(1, N_PARTS+1):
    part_file = f"{PART_PREFIX}{i:02d}.csv"
    if not os.path.exists(part_file):
        print("Warning: part file not found:", part_file)
        continue
    df = pd.read_csv(part_file, dtype=str)
    filenames = df['filename'].dropna().unique().tolist()
    pack_dir = os.path.join(OUT_BASE, f"pack_part_{i:02d}")
    if os.path.exists(pack_dir):
        shutil.rmtree(pack_dir)
    os.makedirs(pack_dir, exist_ok=True)
    copied = 0
    for fname in filenames:
        src = os.path.join(IMAGE_DIR, fname)
        if os.path.exists(src):
            dst = os.path.join(pack_dir, fname)
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"Missing image for {fname} (referenced in {part_file})")
    # copy the CSV into pack folder for reference
    shutil.copy2(part_file, os.path.join(pack_dir, part_file))
    # create zip
    zip_name = os.path.join(OUT_BASE, f"pack_part_{i:02d}")
    shutil.make_archive(zip_name, 'zip', pack_dir)
    print(f"Created {zip_name}.zip with {copied} images (+1 CSV).")

print("All packs created in:", OUT_BASE)
