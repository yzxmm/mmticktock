import os
import json
from PIL import Image

def generate_ico():
    png_path = os.path.join("assets", "icon.png")
    ico_path = os.path.join("assets", "icon.ico")
    
    if os.path.exists(png_path):
        try:
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(256, 256)])
            print(f"Generated {ico_path} from {png_path}")
        except Exception as e:
            print(f"Failed to generate ICO: {e}")
    else:
        print(f"{png_path} not found!")

def generate_config():
    config_path = "layout_config.json"
    default_config = {
        "window_size": [500, 200],
        "target_date": "2026-01-01 00:00:00",
        "top_most": False,
        "timezone": "Asia/Shanghai"
    }
    
    # Always generate/overwrite to ensure it exists and is valid for build
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4)
    print(f"Generated default {config_path}")

if __name__ == "__main__":
    generate_ico()
    generate_config()
