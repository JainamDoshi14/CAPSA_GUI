"""A focused Simple / Exam explanation panel for a result tile."""

import customtkinter as ctk

from core.explain_content import explain_result
from core.models import LineModel, Result
from theme import COLORS, INK, FONT_DISPLAY, FONT_BODY
from .neo import NeoButton


class ExplainSheet(ctk.CTkToplevel):
    def __init__(self, master, metric: str, model: LineModel, result: Result, digits: int = 5):
        super().__init__(master)
        self.configure(fg_color=COLORS["bg"])
        self.title("Understand this result")
        self.geometry("520x520")
        self.minsize(420, 440)
        self.transient(master.winfo_toplevel())
        self.content = explain_result(metric, model, result, digits)
        self.level = ctk.StringVar(value="Simple")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text=self.content["title"].upper(), text_color=INK,
                     font=ctk.CTkFont(FONT_DISPLAY, 20, weight="bold")).grid(
                         row=0, column=0, sticky="w", padx=20, pady=(18, 6))
        ctk.CTkSegmentedButton(self, values=["Simple", "Exam"], variable=self.level,
                               selected_color=COLORS["yellow"], selected_hover_color=COLORS["hover"],
                               unselected_color=COLORS["surface"], text_color=INK,
                               corner_radius=4, border_width=3, command=self._render).grid(
                                   row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        self.body = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(FONT_BODY, 13),
                                   fg_color=COLORS["surface"], text_color=INK,
                                   border_color=INK, border_width=3, corner_radius=4)
        self.body.grid(row=2, column=0, sticky="nsew", padx=16, pady=4)
        NeoButton(self, text="CLOSE", height=40, command=self.destroy).grid(
            row=3, column=0, sticky="e", padx=20, pady=16)
        self._render()

    def _render(self, _value=None):
        if self.level.get() == "Simple":
            text = (f"What is it?\n{self.content['what']}\n\n"
                    f"A way to picture it\n{self.content['analogy']}\n\n"
                    f"Your result\n{self.content['substitution']}\n\n"
                    f"Why it matters\n{self.content['why']}")
        else:
            text = (f"Definition\n{self.content['what']}\n\n"
                    f"Formula\n{self.content['formula']}\n\n"
                    f"Substitution\n{self.content['substitution']}\n\n"
                    f"Engineering interpretation\n{self.content['why']}")
        self.body.configure(state="normal")
        self.body.delete("1.0", "end")
        self.body.insert("1.0", text)
        self.body.configure(state="disabled")
