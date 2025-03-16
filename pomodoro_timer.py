import tkinter as tk
from timer_ui import TimerUI
from system_events import SystemEventHandler
from settings import Settings
import sys
import threading
import signal

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
        
        # Handle window minimize event
        self.root.bind("<Unmap>", lambda e: self.on_minimize() if e.widget is self.root else None)
        
        # Start system event monitoring in a separate thread
        self.event_thread = threading.Thread(target=self.system_events.start_monitoring, daemon=True)
        self.event_thread.start()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        print("\nReceived signal to terminate. Cleaning up...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up resources before exit"""
        if hasattr(self, 'timer_ui'):
            self.timer_ui.running = False
            if hasattr(self.timer_ui, 'tray_icon') and self.timer_ui.tray_icon.visible:
                self.timer_ui.tray_icon.stop()
        self.root.quit()

    def on_system_unlock(self):
        """Handler for system unlock event"""
        if self.settings.get_auto_start():
            self.root.deiconify()  # Show window
            self.timer_ui.start_timer()

    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()

    def on_minimize(self):
        """Handle window minimize event"""
        self.timer_ui.minimize_to_tray()

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
