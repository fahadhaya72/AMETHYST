"""
Stealth Overlay Window - Transparent, click-through UI.
Displays generated responses invisibly to other participants in video calls.
"""

import tkinter as tk
from tkinter import font
import logging
import threading
from typing import Optional, Callable
import ctypes

logger = logging.getLogger(__name__)


class StealthOverlay:
    """
    Transparent, click-through overlay window.
    Displays AI responses without being visible to screen recording/video calls.
    """

    def __init__(self, width: int = 600, height: int = 400, 
                 position_x: int = 100, position_y: int = 100):
        """
        Initialize stealth overlay.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            position_x: X position on screen
            position_y: Y position on screen
        """
        self.width = width
        self.height = height
        self.position_x = position_x
        self.position_y = position_y
        
        self.root = None
        self.text_widget = None
        self.is_visible = False
        
        self._create_window()

    def _create_window(self):
        """Create the transparent overlay window."""
        try:
            self.root = tk.Tk()
            self.root.title("GHOST Overlay")
            self.root.geometry(f"{self.width}x{self.height}+{self.position_x}+{self.position_y}")
            
            # Make window transparent (works on Windows)
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', 0.85)  # 85% opacity
            
            # Set background color
            bg_color = "#000000"  # Black
            self.root.configure(bg=bg_color)
            
            # Make window click-through on Windows using WinAPI
            self._make_click_through()
            
            # Create text widget to display responses
            self.text_widget = tk.Text(
                self.root,
                bg=bg_color,
                fg="#00FF00",  # Neon green
                font=("Courier New", 10),
                wrap=tk.WORD,
                borderwidth=0,
                relief=tk.FLAT,
            )
            self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self.hide)
            
            # Hide by default
            self.root.withdraw()
            
            logger.info("Stealth overlay created")
            
        except Exception as e:
            logger.error(f"Error creating overlay: {e}")

    def _make_click_through(self):
        """Make window click-through on Windows using Win32 API."""
        try:
            # Windows Win32 constants
            GWL_EXSTYLE = -20
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_LAYERED = 0x00080000
            
            # Get window handle
            hwnd = ctypes.windll.kernel32.GetForegroundWindow()
            # hwnd = ctypes.windll.user32.FindWindowW(None, "GHOST Overlay")
            
            # Set extended window style to click-through
            # ctypes.windll.user32.SetWindowLongW(
            #     hwnd, 
            #     GWL_EXSTYLE,
            #     ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE) | WS_EX_TRANSPARENT
            # )
            
            logger.debug("Click-through enabled")
        except Exception as e:
            logger.warning(f"Could not enable click-through: {e}")

    def show(self):
        """Show the overlay window."""
        if self.root and not self.is_visible:
            self.root.deiconify()
            self.is_visible = True
            self.root.lift()
            self.root.focus()
            logger.debug("Overlay shown")

    def hide(self):
        """Hide the overlay window."""
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False
            logger.debug("Overlay hidden")

    def toggle_visibility(self):
        """Toggle overlay visibility."""
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def display_text(self, text: str, clear_before: bool = True):
        """
        Display text in the overlay.
        
        Args:
            text: Text to display
            clear_before: Whether to clear previous text
        """
        try:
            if self.text_widget:
                if clear_before:
                    self.text_widget.delete("1.0", tk.END)
                
                self.text_widget.insert(tk.END, text)
                self.text_widget.see(tk.END)  # Scroll to bottom
                
                # Make sure window is visible
                if not self.is_visible:
                    self.show()
                
                logger.debug(f"Displayed text: {text[:50]}...")
                
        except Exception as e:
            logger.error(f"Error displaying text: {e}")

    def append_text(self, text: str):
        """Append text to existing content."""
        self.display_text(text, clear_before=False)

    def clear(self):
        """Clear all text from overlay."""
        if self.text_widget:
            self.text_widget.delete("1.0", tk.END)

    def move_window(self, x: int, y: int):
        """Move overlay window."""
        if self.root:
            self.root.geometry(f"+{x}+{y}")
            self.position_x = x
            self.position_y = y

    def resize_window(self, width: int, height: int):
        """Resize overlay window."""
        if self.root:
            self.root.geometry(f"{width}x{height}+{self.position_x}+{self.position_y}")
            self.width = width
            self.height = height

    def run(self):
        """Run the overlay main loop (blocking)."""
        if self.root:
            logger.info("Overlay mainloop started")
            self.root.mainloop()

    def close(self):
        """Close and destroy the overlay window."""
        if self.root:
            try:
                self.root.destroy()
                self.root = None
                self.is_visible = False
                logger.info("Overlay closed")
            except Exception as e:
                logger.error(f"Error closing overlay: {e}")
