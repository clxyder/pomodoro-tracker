import json
import os

class Settings:
    def __init__(self):
        self.settings_file = "pomodoro_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from file"""
        default_settings = {
            "auto_start": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return default_settings
        except:
            return default_settings

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_auto_start(self):
        """Get auto-start setting"""
        return self.settings.get("auto_start", True)

    def set_auto_start(self, value):
        """Set auto-start setting"""
        self.settings["auto_start"] = value
        self.save_settings()
