import tkinter as tk
from timer_ui import TimerUI
from system_events import SystemEventHandler
from settings import Settings
import sys
import threading
import signal
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PomodoroApp:
    def __init__(self):
        start_time = time.time()
        logger.debug("Starting PomodoroApp initialization")
        
        self.root = tk.Tk()
        logger.debug("Tkinter root window created: %.3f seconds", time.time() - start_time)
        
        self.root.title("Pomodoro Timer")
        self.root.geometry("300x400")
        
        # Initialize settings
        logger.debug("Initializing settings")
        self.settings = Settings()
        logger.debug("Settings initialized: %.3f seconds", time.time() - start_time)
        
        # Create and setup UI
        logger.debug("Creating TimerUI")
        self.timer_ui = TimerUI(self.root, self.settings, self)
        logger.debug("TimerUI created: %.3f seconds", time.time() - start_time)
        
        # Initialize system event handler
        logger.debug("Initializing SystemEventHandler")
        self.system_events = SystemEventHandler(self.on_system_unlock)
        logger.debug("SystemEventHandler initialized: %.3f seconds", time.time() - start_time)
        
        # Setup window behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Track window state
        self.is_minimized = False
        self._minimizing = False  # Flag to track minimize operation in progress
        
        # Handle window minimize event
        self.root.bind("<Unmap>", self.on_minimize)
        
        # Start system event monitoring in a separate thread
        logger.debug("Starting system event monitoring thread")
        self.event_thread = threading.Thread(target=self.system_events.start_monitoring, daemon=True)
        self.event_thread.start()
        logger.debug("System event thread started: %.3f seconds", time.time() - start_time)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.debug("PomodoroApp initialization completed in %.3f seconds", time.time() - start_time)

    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        print("\nReceived signal to terminate. Cleaning up...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up resources before exit"""
        if hasattr(self, 'timer_ui'):
            self.timer_ui.running = False
            if hasattr(self.timer_ui, 'tray_icon') and self.timer_ui.tray_icon is not None and self.timer_ui.tray_icon_running:
                self.timer_ui.tray_icon.stop()
        self.root.quit()

    def on_system_unlock(self):
        """Handler for system unlock event"""
        if self.settings.get_auto_start() and not self.is_minimized:  # Only show if not minimized
            self.root.deiconify()  # Show window
            logger.debug("System unlocked with auto-start enabled, starting timer")
            self.timer_ui.start_timer()

    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()

    def on_minimize(self, event=None):
        """Handle window minimize event"""
        # Only process root window events and prevent re-entry
        if event and event.widget is self.root and not self._minimizing:
            self._minimizing = True  # Set flag to prevent re-entry
            try:
                if not self.is_minimized:
                    print("[DEBUG] Minimizing to tray")
                    self.is_minimized = True
                    self.timer_ui.minimize_to_tray()
            finally:
                self._minimizing = False  # Reset flag

    def run(self):
        """Start the application"""
        try:
            logger.debug("Starting main application loop")
            start_time = time.time()
            self.root.mainloop()
            logger.debug("Main loop ended after %.3f seconds", time.time() - start_time)
        except KeyboardInterrupt:
            logger.info("Application terminated by user")
            self.cleanup()

if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
