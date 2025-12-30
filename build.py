import os
import json
import shutil
import subprocess
import sys
from PIL import Image

def generate_ico():
    print("Generating icon...")
    png_path = os.path.join("assets", "icon.png")
    ico_path = os.path.join("assets", "icon.ico")
    
    # Check if we need to rename icon.ico.png (common user error)
    weird_path = os.path.join("assets", "icon.ico.png")
    if os.path.exists(weird_path) and not os.path.exists(png_path):
        print(f"Renaming {weird_path} to {png_path}")
        os.rename(weird_path, png_path)

    if os.path.exists(png_path):
        try:
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(256, 256)])
            print(f"Generated {ico_path} from {png_path}")
        except Exception as e:
            print(f"Failed to generate ICO: {e}")
    else:
        print(f"{png_path} not found! Checking for existing icon.ico...")
        if not os.path.exists(ico_path):
            print("Warning: No icon found.")

def generate_config():
    print("Checking configuration...")
    config_path = "layout_config.json"
    default_config = {
        "window_size": [500, 200],
        "target_date": "2026-01-01 00:00:00",
        "top_most": False,
        "timezone": "Asia/Shanghai"
    }
    
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        print(f"Generated default {config_path}")
    else:
        print(f"{config_path} already exists.")

def clean_build_dirs():
    print("Cleaning up...")
    for d in ['build', 'dist']:
        if os.path.exists(d):
            shutil.rmtree(d)
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            os.remove(f)

def build_exe():
    print("Building EXE...")
    cmd = [
        'pyinstaller',
        '--noconsole',
        '--onefile',
        '--name', 'mmticktock',
        '--add-data', 'assets;assets',
        'main.py'
    ]
    
    if os.path.exists(os.path.join("assets", "icon.ico")):
        cmd.insert(5, '--icon')
        cmd.insert(6, os.path.join("assets", "icon.ico"))
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

def copy_files():
    print("Copying files to dist...")
    dist_dir = 'dist'
    
    # Copy config
    if os.path.exists("layout_config.json"):
        shutil.copy("layout_config.json", dist_dir)
    
    # Copy assets
    dest_assets = os.path.join(dist_dir, "assets")
    if os.path.exists("assets"):
        shutil.copytree("assets", dest_assets)
        
    # Copy tutorial
    doc_name = "mmticktock教程.docx"
    if os.path.exists(doc_name):
        shutil.copy(doc_name, dist_dir)
    else:
        print(f"Warning: {doc_name} not found.")

if __name__ == "__main__":
    generate_ico()
    generate_config()
    clean_build_dirs()
    build_exe()
    copy_files()
    print("Build complete! Check the dist folder.")
