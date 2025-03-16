import tkinter as tk
from timer_ui import TimerUI
from system_events import SystemEventHandler
from settings import Settings
import sys
import threading

class PomodoroApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.root.geometry("300x400")
        
        # Initialize settings
        self.settings = Settings()
        
        # Create and setup UI
        self.timer_ui = TimerUI(self.root, self.settings)
        
        # Initialize system event handler
        self.system_events = SystemEventHandler(self.on_system_unlock)
        
        # Setup window behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.withdraw()  # Start minimized to system tray
        
        # Start system event monitoring in a separate thread
        self.event_thread = threading.Thread(target=self.system_events.start_monitoring, daemon=True)
        self.event_thread.start()

    def on_system_unlock(self):
        """Handler for system unlock event"""
        if self.settings.get_auto_start():
            self.root.deiconify()  # Show window
            self.timer_ui.start_timer()

    def on_closing(self):
        """Handle window closing"""
        self.timer_ui.minimize_to_tray()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
