import tkinter as tk
from tkinter import ttk
import pystray
from PIL import Image
from plyer import notification
import time
import threading
import winsound
from io import BytesIO

class TimerUI:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.running = False
        self.paused = False
        self.current_time = 25 * 60  # 25 minutes in seconds
        self.is_break = False
        
        self.setup_ui()
        self.setup_tray()

    def setup_ui(self):
        """Setup the main UI components"""
        # Timer display
        self.time_label = ttk.Label(
            self.root,
            text="25:00",
            font=("Arial", 48)
        )
        self.time_label.pack(pady=20)

        # Control buttons
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            self.button_frame,
            text="Start",
            command=self.start_timer
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(
            self.button_frame,
            text="Pause",
            command=self.pause_timer,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            self.button_frame,
            text="Reset",
            command=self.reset_timer
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Settings
        self.settings_frame = ttk.LabelFrame(self.root, text="Settings")
        self.settings_frame.pack(pady=10, padx=10, fill=tk.X)

        # Time settings
        time_frame = ttk.Frame(self.settings_frame)
        time_frame.pack(pady=5, fill=tk.X)

        # Focus time setting
        focus_frame = ttk.Frame(time_frame)
        focus_frame.pack(fill=tk.X, pady=2)
        ttk.Label(focus_frame, text="Focus time (minutes):").pack(side=tk.LEFT, padx=5)
        self.focus_time_var = tk.StringVar(value=str(self.settings.get_focus_time()))
        self.focus_time_entry = ttk.Entry(
            focus_frame,
            textvariable=self.focus_time_var,
            width=5
        )
        self.focus_time_entry.pack(side=tk.LEFT, padx=5)
        self.focus_time_entry.bind('<FocusOut>', lambda e: self.save_time_settings())
        self.focus_time_entry.bind('<Return>', lambda e: self.save_time_settings())

        # Break time setting
        break_frame = ttk.Frame(time_frame)
        break_frame.pack(fill=tk.X, pady=2)
        ttk.Label(break_frame, text="Break time (minutes):").pack(side=tk.LEFT, padx=5)
        self.break_time_var = tk.StringVar(value=str(self.settings.get_break_time()))
        self.break_time_entry = ttk.Entry(
            break_frame,
            textvariable=self.break_time_var,
            width=5
        )
        self.break_time_entry.pack(side=tk.LEFT, padx=5)
        self.break_time_entry.bind('<FocusOut>', lambda e: self.save_time_settings())
        self.break_time_entry.bind('<Return>', lambda e: self.save_time_settings())

        # Auto-start setting
        self.auto_start_var = tk.BooleanVar(value=self.settings.get_auto_start())
        self.auto_start_check = ttk.Checkbutton(
            self.settings_frame,
            text="Auto-start on system unlock",
            variable=self.auto_start_var,
            command=self.save_settings
        )
        self.auto_start_check.pack(pady=5)

    def setup_tray(self):
        """Setup system tray icon and menu"""
        # Create an empty image for the tray icon
        self.icon_image = Image.new('RGB', (64, 64), color='red')
        
        menu = (
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            "pomodoro",
            self.icon_image,
            "Pomodoro Timer",
            menu
        )

    def start_timer(self):
        """Start the timer"""
        if not self.running:
            self.running = True
            self.paused = False
            self.start_button.configure(state=tk.DISABLED)
            self.pause_button.configure(state=tk.NORMAL)
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()

    def pause_timer(self):
        """Pause/Resume the timer"""
        self.paused = not self.paused
        self.pause_button.configure(text="Resume" if self.paused else "Pause")

    def reset_timer(self):
        """Reset the timer"""
        self.running = False
        self.paused = False
        self.current_time = self.settings.get_focus_time() * 60
        self.is_break = False
        self.update_display()
        self.start_button.configure(state=tk.NORMAL)
        self.pause_button.configure(state=tk.DISABLED)

    def timer_loop(self):
        """Main timer loop"""
        while self.running and self.current_time > 0:
            if not self.paused:
                time.sleep(1)
                self.current_time -= 1
                self.update_display()

            if self.current_time <= 0:
                self.timer_complete()

    def update_display(self):
        """Update the timer display"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")

    def timer_complete(self):
        """Handle timer completion"""
        self.play_notification_sound()
        self.show_notification()

        if self.is_break:
            self.current_time = self.settings.get_focus_time() * 60  # Work period
            self.is_break = False
            message = f"Break time is over! Time to focus for {self.settings.get_focus_time()} minutes."
        else:
            self.current_time = self.settings.get_break_time() * 60  # Break period
            self.is_break = True
            message = f"Well done! Take a {self.settings.get_break_time()}-minute break."

        # Show popup window
        popup = tk.Toplevel(self.root)
        popup.title("Timer Complete!")
        popup.geometry("300x150")
        popup.lift()  # Bring window to front

        # Center the popup
        popup.geometry(f"+{self.root.winfo_x() + 150}+{self.root.winfo_y() + 150}")

        # Add message
        ttk.Label(popup, text=message, wraplength=250, justify='center').pack(pady=20)

        # Add dismiss button
        ttk.Button(popup, text="OK", command=popup.destroy).pack()

        # Auto-close after 5 seconds
        popup.after(5000, popup.destroy)

        self.start_timer()

    def play_notification_sound(self):
        """Play notification sound"""
        try:
            # Cross-platform solution using system bell
            self.root.bell()
            self.root.update()
        except:
            pass  # Fallback if bell doesn't work

    def show_notification(self):
        """Show system notification"""
        title = "Break Time!" if not self.is_break else "Back to Work!"
        message = ("Time for a 5-minute break!" if not self.is_break 
                  else "Break's over! Let's focus for 25 minutes.")

        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,
                timeout=10,
                toast=True  # Windows toast notification
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")

    def minimize_to_tray(self):
        """Minimize application to system tray"""
        self.root.withdraw()
        if not self.tray_icon.visible:
            self.tray_icon.run()

    def show_window(self):
        """Show the main window"""
        self.tray_icon.stop()
        self.root.deiconify()

    def quit_app(self):
        """Exit the application"""
        self.running = False
        self.tray_icon.stop()
        self.root.quit()

    def save_settings(self):
        """Save current settings"""
        self.settings.set_auto_start(self.auto_start_var.get())

    def save_time_settings(self):
        """Save focus and break time settings"""
        try:
            focus_time = int(self.focus_time_var.get())
            break_time = int(self.break_time_var.get())

            if focus_time > 0 and break_time > 0:
                self.settings.set_focus_time(focus_time)
                self.settings.set_break_time(break_time)
                self.reset_timer()  # Reset timer with new duration
            else:
                # Reset to previous values if invalid
                self.focus_time_var.set(str(self.settings.get_focus_time()))
                self.break_time_var.set(str(self.settings.get_break_time()))
        except ValueError:
            # Reset to previous values if invalid
            self.focus_time_var.set(str(self.settings.get_focus_time()))
            self.break_time_var.set(str(self.settings.get_break_time()))