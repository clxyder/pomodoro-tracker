import time
import os
import ctypes
import logging

logger = logging.getLogger(__name__)

class SystemEventHandler:
    def __init__(self, unlock_callback):
        self.unlock_callback = unlock_callback
        self.running = True
        self.last_state = None  # Track last session state

    def is_user_logged_in(self):
        """Check if user is logged in on Windows"""
        try:
            # Windows constants for session state
            WTS_CURRENT_SERVER_HANDLE = 0
            WTS_CURRENT_SESSION = -1
            WTSConnected = 1
            WTSLock = 2
            WTSLoggedOn = 3
            WTSAvailable = 4
            WTSActive = 5

            # Get session info using Windows API
            session_id = ctypes.c_ulong()
            ctypes.windll.kernel32.WTSGetActiveConsoleSessionId()
            
            state = ctypes.c_ulong()
            state_size = ctypes.c_ulong()
            
            result = ctypes.windll.wtsapi32.WTSQuerySessionInformationW(
                WTS_CURRENT_SERVER_HANDLE,
                WTS_CURRENT_SESSION,
                WTSConnected,
                ctypes.byref(state),
                ctypes.byref(state_size)
            )
            
            if result == 0:
                logger.debug("Failed to query session state")
                return False
                
            is_connected = bool(state.value)
            ctypes.windll.wtsapi32.WTSFreeMemory(state)
            
            return is_connected
            
        except Exception as e:
            logger.error("Error checking session state: %s", e)
            return False

    def start_monitoring(self):
        """Start monitoring system events"""
        try:
            logger.debug("Starting system event monitoring")
            
            # Check initial state and call callback if already logged in
            initial_state = self.is_user_logged_in()
            self.last_state = initial_state
            if initial_state:
                logger.debug("User already logged in, triggering initial unlock callback")
                self.unlock_callback()
            
            while self.running:
                current_state = self.is_user_logged_in()
                
                # If state changed from logged out to logged in
                if current_state and self.last_state is False:
                    logger.debug("User session became active, triggering unlock callback")
                    self.unlock_callback()
                
                self.last_state = current_state
                time.sleep(2)  # Check every 2 seconds

        except Exception as e:
            logger.error("Error in system event monitoring: %s", e)

    def stop(self):
        """Stop monitoring system events"""
        logger.debug("Stopping system event monitoring")
        self.running = False