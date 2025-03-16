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
        self.timer_ui = TimerUI(self.root, self.settings, self)
        
        # Initialize system event handler
        self.system_events = SystemEventHandler(self.on_system_unlock)
        
        # Setup window behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Track window state
        self.is_minimized = False
        self._minimizing = False  # Flag to track minimize operation in progress
        
        # Handle window minimize event
        self.root.bind("<Unmap>", self.on_minimize)
        
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
        print("[DEBUG] Cleanup called")
        if hasattr(self, 'timer_ui'):
            print("[DEBUG] Timer UI exists")
            self.timer_ui.running = False
            if hasattr(self.timer_ui, 'tray_icon') and self.timer_ui.tray_icon is not None and self.timer_ui.tray_icon_running:
                print("[DEBUG] Stopping tray icon")
                self.timer_ui.tray_icon.stop()
            else:
                print("[DEBUG] No tray icon to stop")
        self.root.quit()

    def on_system_unlock(self):
        """Handler for system unlock event"""
        if self.settings.get_auto_start() and not self.is_minimized:  # Only show if not minimized
            self.root.deiconify()  # Show window
            self.timer_ui.start_timer()

    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()

    def on_minimize(self, event=None):
        """Handle window minimize event"""
        print("[DEBUG] on_minimize called - event widget:", event.widget if event else None)
        print("[DEBUG] is_minimized state:", self.is_minimized)
        print("[DEBUG] _minimizing state:", self._minimizing)
        
        # Only process root window events and prevent re-entry
        if event and event.widget is self.root and not self._minimizing:
            self._minimizing = True  # Set flag to prevent re-entry
            try:
                if not self.is_minimized:
                    print("[DEBUG] Proceeding with minimize to tray")
                    self.is_minimized = True
                    self.timer_ui.minimize_to_tray()
                else:
                    print("[DEBUG] Already minimized, ignoring event")
            finally:
                self._minimizing = False  # Reset flag
        else:
            print("[DEBUG] Skipping minimize - conditions not met")

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
