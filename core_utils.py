import os
import json
import datetime
import pytz

CONFIG_FILE = "layout_config.json"

class ConfigManager:
    @staticmethod
    def load_config():
        config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
            except Exception:
                config = {}
        
        # Defaults
        if "window_size" not in config:
            config["window_size"] = [600, 240]
        if "top_most" not in config:
            config["top_most"] = False
        if "target_date" not in config:
            config["target_date"] = "2026-01-01 00:00:00"
            
        return config

    @staticmethod
    def save_config(config_data):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f)
        except Exception as e:
            print(f"Save config error: {e}")

class TimeCalculator:
    @staticmethod
    def get_time_str(target_date_str, current_tz):
        now = datetime.datetime.now(current_tz)
        try:
            target_naive = datetime.datetime.strptime(target_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            target_naive = datetime.datetime(2026, 1, 1, 0, 0, 0)
        
        target = current_tz.localize(target_naive)
        
        diff = target - now if now < target else now - target
        total_seconds = int(diff.total_seconds())
        
        if total_seconds > 3600:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 99: hours, minutes = 99, 99
            val1, val2 = hours, minutes
        else:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            if minutes > 99: minutes, seconds = 99, 99
            val1, val2 = minutes, seconds
            
        return f"{val1:02d}", f"{val2:02d}"
