"""Small hover glossary bubbles used by explanatory UI labels."""

import tkinter as tk

import customtkinter as ctk

from theme import COLORS


class GlossaryTooltip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.window = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")

    def show(self, _event=None):
        if self.window is not None or not self.widget.winfo_exists():
            return
        x = self.widget.winfo_rootx() + 8
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.window = ctk.CTkToplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.geometry(f"+{x}+{y}")
        bubble = ctk.CTkFrame(
            self.window, fg_color=COLORS["lavender"], corner_radius=6,
            border_width=2, border_color=COLORS["border"],
        )
        bubble.pack()
        ctk.CTkLabel(
            bubble, text=self.text, fg_color="transparent",
            text_color=COLORS["text"], wraplength=280, justify="left",
            font=ctk.CTkFont("Segoe UI", 12),
        ).pack(padx=10, pady=8)

    def hide(self, _event=None):
        if self.window is not None:
            try:
                self.window.destroy()
            except tk.TclError:
                pass
            self.window = None
