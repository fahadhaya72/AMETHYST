"""
Windows System Permissions Handler.
Requests microphone and system audio permissions from the user.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import logging
import ctypes
import os
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class PermissionsDialog:
    """
    Modern permissions dialog for requesting system access.
    Mimics Windows permission dialogs.
    """

    def __init__(self):
        """Initialize permissions dialog."""
        self.granted = False
        self.root = None

    def request_permissions(self) -> bool:
        """
        Show permissions request dialog.
        
        Returns:
            True if all permissions granted, False otherwise
        """
        self.root = tk.Tk()
        self.root.title("GHOST - Permission Request")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Make it stay on top
        self.root.attributes('-topmost', True)
        
        # Configure style
        self.root.configure(bg='#f0f0f0')
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="GHOST Assistant Needs Your Permission",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="GHOST is a real-time AI assistant for video calls.\n"
                 "It needs access to:\n\n"
                 "• Microphone - to capture audio from calls\n"
                 "• System Audio - to hear the other person\n"
                 "• Screen Overlay - to display AI responses",
            font=("Segoe UI", 10),
            justify=tk.LEFT
        )
        desc_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Warning
        warning_frame = ttk.LabelFrame(main_frame, text="Important", padding=10)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_label = ttk.Label(
            warning_frame,
            text="GHOST only works during video calls and will not activate\n"
                 "for other applications. Your data is processed securely.",
            font=("Segoe UI", 9),
            justify=tk.LEFT
        )
        warning_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0), side=tk.BOTTOM)
        
        deny_btn = ttk.Button(
            button_frame,
            text="Don't Allow",
            command=self._on_deny
        )
        deny_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        allow_btn = ttk.Button(
            button_frame,
            text="Allow",
            command=self._on_allow
        )
        allow_btn.pack(side=tk.LEFT)
        
        # Center frame vertically
        self.root.grid_rowconfigure(0, weight=1)
        
        self.root.mainloop()
        
        return self.granted

    def _on_allow(self):
        """Handle Allow button click."""
        self.granted = True
        logger.info("User granted permissions")
        self.root.destroy()

    def _on_deny(self):
        """Handle Don't Allow button click."""
        self.granted = False
        logger.info("User denied permissions")
        self.root.destroy()

    @staticmethod
    def check_microphone_available() -> bool:
        """Check if microphone is available on system."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            count = p.get_device_count()
            p.terminate()
            return count > 0
        except Exception:
            return False

    @staticmethod
    def elevate_privileges():
        """
        Request admin privileges if needed for audio capture.
        (Windows only)
        """
        try:
            # Check if already running as admin
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            
            if not is_admin:
                logger.warning("Not running as administrator - some audio devices may not work")
                messagebox.showwarning(
                    "Admin Privileges",
                    "GHOST works best with administrator privileges.\n\n"
                    "Please right-click the application and select 'Run as administrator'."
                )
            
            return is_admin
            
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
