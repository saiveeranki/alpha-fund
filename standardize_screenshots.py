import os
from PIL import Image

def process_image(source_path, target_path, target_size=(1440, 900)):
    print(f"Processing {source_path} -> {target_path}")
    img = Image.open(source_path)
    
    # Resize to target width while maintaining aspect ratio
    w_percent = (target_size[0] / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((target_size[0], h_size), Image.Resampling.LANCZOS)
    
    # Crop to target height
    if img.size[1] > target_size[1]:
        img = img.crop((0, 0, target_size[0], target_size[1]))
    else:
        # If smaller, we could pad or just leave it. But they are likely taller.
        pass
        
    img.save(target_path)
    print(f"Saved: {target_path} {img.size}")

base_dir = r"c:\Users\Sai Veeranki\My Drive\antigravity\stockmarket\docs\screenshots"
brain_dir = r"C:\Users\Sai Veeranki\.gemini\antigravity\brain\836f3dc7-2833-482c-bd5d-4109545ac8e7"

mappings = [
    (os.path.join(brain_dir, "legendary_portfolios_final_view_1773473357650.png"), os.path.join(base_dir, "legendary_portfolios.png")),
    (os.path.join(brain_dir, "sector_heatmap_final_capture_1773473632838.png"), os.path.join(base_dir, "sector_heatmap.png")),
    (os.path.join(brain_dir, "sector_indices_final_capture_1773473861699.png"), os.path.join(base_dir, "sector_indices.png")),
    (os.path.join(brain_dir, "legendary_portfolios_final_view_1773473357650.png"), os.path.join(base_dir, "legendary_portfolios_dynamic.png")),
    (os.path.join(brain_dir, "allocation_advisor_final_capture_1773474757129.png"), os.path.join(base_dir, "allocation.png")),
]

for src, dst in mappings:
    if os.path.exists(src):
        process_image(src, dst)
    else:
        print(f"Source not found: {src}")
