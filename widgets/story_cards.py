"""Five-card guided explanation for a completed line calculation."""

from tkinter import filedialog

import customtkinter as ctk

from core.explain_content import story_steps
from core.models import LineModel, Result
from theme import COLORS, INK, FONT_DISPLAY, FONT_BODY
from .neo import NeoButton


class StoryCards(ctk.CTkToplevel):
    def __init__(self, master, model: LineModel, result: Result, digits: int = 5):
        super().__init__(master)
        self.configure(fg_color=COLORS["bg"])
        self.title("Your calculation, step by step")
        self.geometry("640x440")
        self.minsize(520, 380)
        self.transient(master.winfo_toplevel())
        self.steps = story_steps(model, result, digits)
        self.index = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.heading = ctk.CTkLabel(self, text="", text_color=COLORS["text"],
                                    font=ctk.CTkFont(FONT_DISPLAY, 21, weight="bold"))
        self.heading.grid(row=0, column=0, sticky="w", padx=22, pady=(20, 4))
        self.text = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(FONT_BODY, 14),
                                   fg_color=COLORS["surface"], text_color=INK,
                                   border_color=INK, border_width=3, corner_radius=4)
        self.text.grid(row=1, column=0, sticky="nsew", padx=18, pady=8)
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=18, pady=(5, 18))
        nav.grid_columnconfigure(1, weight=1)
        self.back = NeoButton(nav, text="← BACK", width=88, height=40, command=lambda: self._show(-1))
        self.back.grid(row=0, column=0, padx=(0, 8))
        self.counter = ctk.CTkLabel(nav, text="", text_color=COLORS["muted"])
        self.counter.grid(row=0, column=1)
        self.next = NeoButton(nav, text="NEXT →", width=88, height=40, command=lambda: self._show(1))
        self.next.grid(row=0, column=2, padx=(8, 0))
        NeoButton(nav, text="COPY STEP", width=96, height=40, command=self.copy_step).grid(row=0, column=3, padx=4)
        NeoButton(nav, text="COPY ALL", width=88, height=40, command=self.copy_all).grid(row=0, column=4, padx=4)
        NeoButton(nav, text="EXPORT .MD", width=104, height=40, command=self.export).grid(row=0, column=5, padx=(4, 0))
        self._show(0)

    def _show(self, offset: int):
        self.index = max(0, min(len(self.steps) - 1, self.index + offset))
        step = self.steps[self.index]
        self.heading.configure(text=step["title"])
        self.counter.configure(text=f"Step {self.index + 1} of {len(self.steps)}")
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", f"{step['body']}\n\n{step['formula']}")
        self.text.configure(state="disabled")
        self.back.configure(state="normal" if self.index else "disabled")
        self.next.configure(state="normal" if self.index < len(self.steps) - 1 else "disabled")

    def _all_text(self) -> str:
        return "\n\n".join(f"## {step['title']}\n\n{step['body']}\n\n{step['formula']}" for step in self.steps)

    def copy_step(self):
        step = self.steps[self.index]
        self.clipboard_clear()
        self.clipboard_append(f"{step['title']}\n{step['body']}\n{step['formula']}")

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self._all_text())

    def export(self):
        path = filedialog.asksaveasfilename(
            parent=self, title="Export explanation", defaultextension=".md",
            filetypes=[("Markdown files", "*.md")], initialfile="line-explanation",
        )
        if path:
            with open(path, "w", encoding="utf-8", newline="\n") as output:
                output.write("# Calculation explained\n\n" + self._all_text())
