import time
import os
import logging
import psutil

logger = logging.getLogger(__name__)

class SystemEventHandler:
    def __init__(self, unlock_callback):
        self.unlock_callback = unlock_callback
        self.running = True
        self.last_state = None  # Track last session state

    def is_user_logged_in(self):
        """Check if Windows PC is unlocked by checking for absence of LogonUI.exe"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == "LogonUI.exe":
                    return False  # PC is locked
            return True  # PC is unlocked
            
        except Exception as e:
            logger.error("Error checking lock state: %s", e)
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