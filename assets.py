import os
from PyQt5.QtGui import QPixmap
from utils import resource_path

class AssetLoader:
    def __init__(self, asset_dir="assets"):
        self.digits = {}
        self.colon = None
        self.bg = None
        self.icon = None
        
        # Resolve asset_dir
        self.asset_dir = resource_path(asset_dir)
        print(f"Loading assets from: {self.asset_dir}")
        
        try:
            self.load_assets()
        except Exception as e:
            print(f"Resource loading error: {e}")

    def load_assets(self):
        if not os.path.exists(self.asset_dir):
            print(f"Asset directory not found: {self.asset_dir}")
            return

        # Load Digits
        for i in range(10):
            path = os.path.join(self.asset_dir, f"{i}.png")
            if os.path.exists(path):
                self.digits[str(i)] = QPixmap(path)
                
        # Load Colon
        colon_path = os.path.join(self.asset_dir, "colon.png")
        if os.path.exists(colon_path):
            self.colon = QPixmap(colon_path)
            
        # Load Background
        bg_path = os.path.join(self.asset_dir, "bg.png")
        if os.path.exists(bg_path):
            self.bg = QPixmap(bg_path)
            
        # Load Icon (Support .ico or .png)
        icon_path_ico = os.path.join(self.asset_dir, "icon.ico")
        icon_path_png = os.path.join(self.asset_dir, "icon.png")
        if os.path.exists(icon_path_ico):
             self.icon = QPixmap(icon_path_ico)
        elif os.path.exists(icon_path_png):
             self.icon = QPixmap(icon_path_png)
