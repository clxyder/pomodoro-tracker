import win32con
import win32api
import win32gui
import win32ts
import time

class SystemEventHandler:
    def __init__(self, unlock_callback):
        self.unlock_callback = unlock_callback
        self.running = True

    def start_monitoring(self):
        """Start monitoring system events"""
        try:
            while self.running:
                session_id = win32ts.WTSGetActiveConsoleSessionId()
                initial_state = win32ts.WTSQuerySessionInformation(
                    win32ts.WTS_CURRENT_SERVER_HANDLE,
                    session_id,
                    win32ts.WTSSessionInfo
                )

                time.sleep(1)  # Check every second

                current_state = win32ts.WTSQuerySessionInformation(
                    win32ts.WTS_CURRENT_SERVER_HANDLE,
                    session_id,
                    win32ts.WTSSessionInfo
                )

                # Detect unlock by comparing states
                if (initial_state.State == win32ts.WTSLocked and 
                    current_state.State == win32ts.WTSActive):
                    self.unlock_callback()

        except Exception as e:
            print(f"Error monitoring system events: {e}")

    def stop(self):
        """Stop monitoring system events"""
        self.running = False
